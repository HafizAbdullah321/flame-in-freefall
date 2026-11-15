"""Accessibility tests (WCAG 2.1 AA): palette contrast, an axe-core audit of the running dashboard + flame component, keyboard control.
Setup once: npm install axe-core   (set AXE_JS to its axe.min.js if it is not in ./node_modules)   pip install streamlit playwright && playwright install chromium
Run:        python app/tests/test_accessibility.py   (from the repo root)"""
import os, subprocess, sys, time, urllib.request
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]; PORT = os.environ.get("PORT", "8572")
AXE = Path(os.environ.get("AXE_JS", "node_modules/axe-core/axe.min.js"))
BG = "#202940"                                                     # card color (page background #1a2035 is darker, so also passes)
TEXT = {"body text": "#ffffff", "muted text": "#a8b2c6", "link": "#4dd0e1", "accent (slider values)": "#ce93d8", "flame HUD text": "#c8d0e0", "flame HUD fps": "#b4bdd0"}
WARN = {"warning amber": "#ffb74d", "error": "#FF9E9E"}            # warnings aim for 7:1
HEADERS = {"green": ("#43a047", "#2e7d32"), "orange": ("#ef6c00", "#e65100"), "red": ("#e53935", "#c62828"), "purple": ("#9c27b0", "#8e24aa"), "teal": ("#0097a7", "#00838f")}

def lum(h):
    c = np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]); c = np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)

def test_palette():
    for n, c in TEXT.items(): assert contrast(c, BG) >= 4.5, (n, contrast(c, BG))
    for n, c in WARN.items(): assert contrast(c, BG) >= 7.0, (n, contrast(c, BG))
    for n, (c1, c2) in HEADERS.items():                              # white card titles are large bold text: 3:1 minimum
        assert min(contrast("#ffffff", c1), contrast("#ffffff", c2)) >= 3.0, (n, c1, c2)
    print("palette contrast OK:", {n: round(float(contrast(c, BG)), 1) for n, c in {**TEXT, **WARN}.items()})

def find_flame(pg):
    for _ in range(60):
        for f in pg.frames:
            if "flame3d" in f.url:
                try: f.wait_for_function("typeof window.__flame!=='undefined'", timeout=15000); return f
                except Exception: pass
        pg.wait_for_timeout(2000)
    raise RuntimeError("flame frame not found")

def axe(frame):
    frame.add_script_tag(path=str(AXE))
    return frame.evaluate("axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','best-practice']}}).then(r=>r.violations.map(v=>v.id+' ('+v.impact+') x'+v.nodes.length))")

def test_browser():
    srv = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py", "--server.headless", "true", "--server.port", PORT,
                            "--browser.gatherUsageStats", "false"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(60):
            try:
                if urllib.request.urlopen(f"http://localhost:{PORT}/_stcore/health", timeout=2).read() == b"ok": break
            except Exception: time.sleep(1)
        with sync_playwright() as p:
            b = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist"]); pg = b.new_page(viewport={"width": 1500, "height": 1000})
            pg.goto(f"http://localhost:{PORT}"); pg.get_by_role("heading", name="Predicted spread rate").first.wait_for(timeout=60000); fr = find_flame(pg); pg.wait_for_timeout(2000)
            v = axe(pg); assert not v, ("dashboard", v)
            v = axe(fr); assert not v, ("flame component", v)
            # keyboard: the canvas is focusable, labelled, and arrow keys move the view; Reset view restores it
            assert fr.get_attribute("canvas", "tabindex") == "0" and "flame" in fr.get_attribute("canvas", "aria-label").lower()
            c0 = fr.evaluate("__flame.camera.position.toArray()"); fr.focus("canvas")
            for _ in range(6): pg.keyboard.press("ArrowLeft"); pg.wait_for_timeout(250)
            pg.wait_for_timeout(1500); c1 = fr.evaluate("__flame.camera.position.toArray()")
            assert np.linalg.norm(np.array(c1) - np.array(c0)) > 0.05, "arrow keys must move the view"
            fr.focus("#reset"); pg.keyboard.press("Enter"); pg.wait_for_timeout(2000)      # keyboard-operable button
            c2 = fr.evaluate("__flame.camera.position.toArray()")
            assert np.allclose(c2, [0, 1.35, 4.5], atol=0.15), c2
            pg.get_by_role("tab", name="Mission insights").click(); pg.get_by_role("heading", name="NASA findings, ranked").first.wait_for(timeout=60000); pg.wait_for_timeout(1500)
            v = axe(pg); assert not v, ("mission insights tab", v)
            pg.get_by_role("tab", name="Experiments").click(); pg.get_by_role("heading", name="Find experiments").first.wait_for(timeout=60000); pg.wait_for_timeout(1500)
            v = axe(pg); assert not v, ("experiments tab", v)
            pg.get_by_role("tab", name="Documents & Synthesis").click(); pg.get_by_role("heading", name="Topic synthesis").first.wait_for(timeout=60000); pg.wait_for_timeout(1500)
            v = axe(pg); assert not v, ("documents & synthesis tab", v)
            pg.get_by_role("tab", name="AI assistant").click(); pg.wait_for_timeout(2000); v = axe(pg); assert not v, ("assistant tab", v)   # last: switching back is slow under software rendering
            print("AXE: 0 violations on dashboard, flame component, mission insights, experiments and assistant tab | keyboard control OK"); b.close()
    finally:
        srv.terminate()

if __name__ == "__main__":
    test_palette(); test_browser(); print("ACCESSIBILITY TESTS PASSED")
