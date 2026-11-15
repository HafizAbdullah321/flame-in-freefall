"""Browser tests for the volumetric 3D flame (headless Chromium via Playwright). Checks the actual rendered pixels.
Setup once:  pip install playwright pillow numpy && playwright install chromium
Run:         python test_flame3d.py          (software rendering is slow; the page runs in ?q=low mode with a larger time step)"""
import io, os, numpy as np
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

PAGE = (Path(__file__).resolve().parents[1] / "components/flame3d/frontend/index.html").as_uri() + "?q=low"
SHOTS = Path(os.environ.get("SHOTS", "/tmp/shots")); SHOTS.mkdir(exist_ok=True, parents=True)

def run():
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 640, "height": 520}); errs = []
        pg.on("console", lambda m: errs.append(m.text[:300]) if m.type == "error" else None); pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
        pg.goto(PAGE); pg.wait_for_function("window.__flame !== undefined"); ev = pg.evaluate
        ev("__flame.config.dtCap = 0.5; document.getElementById('panel').style.display='none'; for (const id of ['state','fps','note','reset']) document.getElementById(id).style.visibility='hidden'")   # measure the canvas only, not the overlay text
        def sim_wait(sec):
            t0 = ev("__flame.S.t"); pg.wait_for_function(f"__flame.S.t - {t0} > {sec}", timeout=180000)
        def frame():
            return np.array(Image.open(io.BytesIO(pg.locator("canvas").screenshot())).convert("RGB")).astype(float)
        def shape(img):                               # bounding box of the bright region (2nd to 98th percentile extents)
            m = img.mean(axis=2) > 70; ys, xs = np.where(m)
            h = np.percentile(ys, 98) - np.percentile(ys, 2); w = np.percentile(xs, 98) - np.percentile(xs, 2)
            return dict(height=h, width=w, aspect=h / w, area=int(m.sum()))
        # pure helpers
        assert ev("__flame.speedScalar(null)") == 0 and ev("__flame.speedScalar(4)") == 1
        assert ev("__flame.sootMix(1,28,97)") > 0.8 and ev("__flame.sootMix(0,28,20)") < 0.2 and ev("__flame.sootMix(0,36,150)") <= 0.25
        # 0g is round, 1g is a tall teardrop (REQ-S5), measured on the rendered image
        ev("setFlameProps({gravity:0,rate:4,status:'IN'})"); pg.wait_for_function("__flame.S.buoy < 0.02", timeout=180000); sim_wait(1)
        im0 = frame(); s0 = shape(im0); Image.fromarray(im0.astype("uint8")).save(SHOTS / "flame_0g.png")
        node_mark = ev("(__flame.canvas.dataset.m = String(Math.random()))"); cam0 = ev("__flame.camera.position.toArray()")
        ev("setFlameProps({gravity:1})"); pg.wait_for_function("__flame.S.buoy > 0.97", timeout=180000); sim_wait(1)
        im1 = frame(); s1 = shape(im1); Image.fromarray(im1.astype("uint8")).save(SHOTS / "flame_1g.png")
        assert 0.8 < s0["aspect"] < 1.3, ("0g should be roughly round", s0)
        assert s1["aspect"] > 1.6 and s1["aspect"] > 1.4 * s0["aspect"], ("1g should be a tall teardrop", s1, s0)
        assert (im0.mean(axis=2) > 70).sum() > 500 and (im1.mean(axis=2) > 70).sum() > 500, "flame must actually be visible"
        # continuity: no isolated dots. A discrete particle look has many tiny bright islands; a continuous flame has few.
        from scipy import ndimage
        for im in (im0, im1):
            lab, n = ndimage.label(im.mean(axis=2) > 70); sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
            assert n <= 12 or (sizes.max() / sizes.sum()) > 0.9, ("flame fragmented into many blobs", n)
        # persistence (REQ-S1, S7)
        assert ev("__flame.canvas.dataset.m") == node_mark and ev("document.querySelectorAll('canvas').length") == 1
        assert np.allclose(cam0, ev("__flame.camera.position.toArray()"), atol=1e-6), "camera must not reset on prop change"
        ev("__flame.camera.position.set(3,2,4)"); ev("setFlameProps({gravity:0})"); sim_wait(1)
        assert np.allclose([3, 2, 4], ev("__flame.camera.position.toArray()"), atol=0.05)
        ev("__flame.camera.position.set(0,1.35,4.5)")
        # speed follows the spread rate: flame time advances faster for a higher rate
        def tf_rate(rate):
            ev(f"setFlameProps({{rate:{rate}}})"); sim_wait(2)
            a, t = ev("[__flame.S.tf, __flame.S.t]"); sim_wait(1.5); c, t2 = ev("[__flame.S.tf, __flame.S.t]"); return (c - a) / (t2 - t)
        r_slow, r_fast = tf_rate(2.0), tf_rate(6.0)
        assert r_fast > 1.8 * r_slow, (r_slow, r_fast)
        # OUT: freezes, grays, shows alert (REQ-A5)
        ev("setFlameProps({status:'OUT'})"); pg.wait_for_function("__flame.S.speed < 1e-4 && __flame.S.gray > 0.95", timeout=180000)
        assert pg.is_visible("#alert") and "Bounds Exceeded" in pg.inner_text("#alert") and pg.get_attribute("#alert", "role") == "alert"
        ev("document.getElementById('alert').style.visibility='hidden'")      # alert verified; hide it so only the flame pixels are compared
        a = frame(); sim_wait(1); c = frame(); Image.fromarray(c.astype("uint8")).save(SHOTS / "flame_out.png")
        assert np.abs(a - c).max() <= 3, "image must freeze when there is no prediction"
        def satur(img):                                                   # saturation of the light the flame ADDS (background colour removed)
            add = np.clip(img - np.array([20, 26, 46]), 0, None); return (add.max(axis=2) - add.min(axis=2))[img.mean(axis=2) > 70].mean()
        assert satur(c) < 0.5 * satur(im1) and satur(c) < 25, ("OUT state must be gray", satur(c), satur(im1))
        # recover; reduce motion slows the flame
        ev("setFlameProps({status:'IN',rate:4})"); sim_wait(2); n_rate = tf_rate(4.0)
        ev("setFlameProps({reduceMotion:true})"); sim_wait(2); a, t = ev("[__flame.S.tf, __flame.S.t]"); sim_wait(1.5); c2, t2 = ev("[__flame.S.tf, __flame.S.t]")
        assert (c2 - a) / (t2 - t) < 0.6 * n_rate, "reduce motion must slow the flame"
        assert not errs, errs
        print(f"0g aspect {s0['aspect']:.2f} | 1g aspect {s1['aspect']:.2f} | time-rate slow/fast {r_slow:.2f}/{r_fast:.2f} | console errors: 0")
        print("FLAME TESTS PASSED"); b.close()

if __name__ == "__main__":
    run()
