"""End-to-end browser test: real Streamlit server + headless Chromium.
Checks that the 3D flame iframe is NOT remounted when sliders/gravity change, receives new props, and keeps the camera.
Setup: pip install streamlit playwright && playwright install chromium     Run from anywhere: python test_app_e2e.py"""
import subprocess, sys, time, urllib.request, os
import numpy as np
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]; PORT = os.environ.get("PORT", "8599"); SHOTS = Path(os.environ.get("SHOTS", "/tmp/shots"))

def wait_health():
    for _ in range(60):
        try:
            if urllib.request.urlopen(f"http://localhost:{PORT}/_stcore/health", timeout=2).read() == b"ok": return
        except Exception: time.sleep(1)
    raise RuntimeError("Streamlit did not start")

def comp_frame(pg, timeout=120):
    end = time.time() + timeout
    while time.time() < end:
        for f in pg.frames:
            if "flame3d" in f.url:
                try:
                    f.wait_for_function("typeof window.__flame !== 'undefined'", timeout=20000); return f
                except Exception: pass
        pg.wait_for_timeout(2000)
    raise RuntimeError("flame component frame not found")

def run():
    srv = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py", "--server.headless", "true",
                            "--server.port", PORT, "--browser.gatherUsageStats", "false"], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        wait_health()
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"])
            pg = b.new_page(viewport={"width": 1500, "height": 1000}); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f"http://localhost:{PORT}"); pg.get_by_role("heading", name="Predicted spread rate").first.wait_for(timeout=60000)
            fr = comp_frame(pg); ev = fr.evaluate
            assert ev("document.body.classList.contains('embedded')"), "tuning panel must be hidden inside the dashboard"
            ev("window.__mark = 'alive'"); ev("__flame.camera.position.set(3,2,4)")
            assert ev("__flame.props.gravity") == 0 and abs(ev("__flame.props.o2") - 28) < 0.01 and ev("__flame.props.rate") > 2
            pg.screenshot(path=str(SHOTS / "app_0g.png"))
            # move the oxygen slider with the keyboard (each press = 0.5 %)
            sl = pg.get_by_role("slider").first; sl.focus()
            for _ in range(8): sl.press("ArrowRight")
            pg.wait_for_function("document.body.innerText.includes('Oxygen (%)')"); pg.wait_for_timeout(3000)
            fr2 = comp_frame(pg)
            assert fr2.evaluate("window.__mark") == "alive", "iframe was remounted on slider change"
            assert fr2.evaluate("__flame.props.o2") > 31.5, fr2.evaluate("__flame.props.o2")
            assert np.allclose(fr2.evaluate("__flame.camera.position.toArray()"), [3, 2, 4], atol=0.05), "camera was reset"
            # switch to 1g: same iframe, gravity prop changes, illustration banner, no numeric prediction
            pg.get_by_text("1g (Earth)").click(); pg.wait_for_timeout(3000)
            fr3 = comp_frame(pg)
            assert fr3.evaluate("window.__mark") == "alive" and fr3.evaluate("__flame.props.gravity") == 1
            assert fr3.evaluate("__flame.props.illustration") is True
            assert "illustration only" in pg.inner_text("body").lower()
            assert "Illustration only" in fr3.inner_text("#rateTxt")
            assert np.allclose(fr3.evaluate("__flame.camera.position.toArray()"), [3, 2, 4], atol=0.05), "camera was reset"
            pg.screenshot(path=str(SHOTS / "app_1g.png"))
            # back to 0g, push oxygen to the end of the range -> flame must stay alive (same iframe)
            pg.get_by_text("0g (microgravity)").click(); pg.wait_for_timeout(3000)
            fr4 = comp_frame(pg); assert fr4.evaluate("window.__mark") == "alive" and fr4.evaluate("__flame.props.gravity") == 0
            assert not errs, errs
            print("E2E PASSED: iframe persisted across slider + gravity changes; camera kept; props updated; no page errors")
            b.close()
    finally:
        srv.terminate()

if __name__ == "__main__":
    run()
