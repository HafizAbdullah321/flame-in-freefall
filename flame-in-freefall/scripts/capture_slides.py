"""
Refined headless Chrome CDP automation script to capture all 7 presentation screenshots
from the live 'Flame in Freefall' Streamlit app with pixel-perfect framing and high resolution.
"""

import os
import sys
import time
import json
import base64
import subprocess
import asyncio
from pathlib import Path
import requests
import websockets

OUTPUT_DIR = Path("flame-in-freefall/assets/slides")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
APP_URL = "http://localhost:8501"

class CDPClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.ws = None
        self.msg_id = 0

    async def connect(self):
        self.ws = await websockets.connect(self.ws_url, max_size=30_000_000)

    async def close(self):
        if self.ws:
            await self.ws.close()

    async def call(self, method, params=None):
        self.msg_id += 1
        cid = self.msg_id
        payload = {"id": cid, "method": method, "params": params or {}}
        await self.ws.send(json.dumps(payload))
        while True:
            resp = json.loads(await self.ws.recv())
            if resp.get("id") == cid:
                if "error" in resp:
                    print(f"CDP Error in {method}: {resp['error']}")
                return resp.get("result", {})

    async def eval_js(self, js_code):
        res = await self.call("Runtime.evaluate", {
            "expression": js_code,
            "returnByValue": True,
            "awaitPromise": True
        })
        return res.get("result", {}).get("value")

    async def click_tab(self, tab_text):
        js = f"""
        (() => {{
            const tabs = Array.from(document.querySelectorAll('[role="tab"]'));
            const target = tabs.find(t => t.innerText.trim().includes("{tab_text}"));
            if (target) {{
                target.click();
                return true;
            }}
            return false;
        }})()
        """
        res = await self.eval_js(js)
        await asyncio.sleep(2.0)
        return res

    async def capture_rect(self, rect, output_path, padding=12, scale=1.5):
        if not rect or rect.get("width", 0) <= 0 or rect.get("height", 0) <= 0:
            print(f"Invalid rect for {output_path}: {rect}")
            return False

        clip = {
            "x": max(0, rect["x"] - padding),
            "y": max(0, rect["y"] - padding),
            "width": rect["width"] + (padding * 2),
            "height": rect["height"] + (padding * 2),
            "scale": scale
        }

        shot_res = await self.call("Page.captureScreenshot", {
            "format": "png",
            "clip": clip,
            "captureBeyondViewport": True
        })

        if "data" in shot_res:
            raw_bytes = base64.b64decode(shot_res["data"])
            Path(output_path).write_bytes(raw_bytes)
            print(f"Successfully captured: {output_path} ({len(raw_bytes) / 1024:.1f} KB, size={int(clip['width']*scale)}x{int(clip['height']*scale)})")
            return True
        return False

async def run():
    print("Launching Chrome headless at 1920x1200...")
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        "--disable-gpu",
        "--no-first-run",
        "--window-size=1920,1200",
        "--force-device-scale-factor=1"
    ])
    time.sleep(2.5)

    try:
        t_res = requests.put(f"http://127.0.0.1:{PORT}/json/new?{APP_URL}")
        page_info = t_res.json()
        ws_url = page_info["webSocketDebuggerUrl"]

        client = CDPClient(ws_url)
        await client.connect()
        await client.call("Page.enable")
        await client.call("Runtime.enable")
        await client.call("DOM.enable")

        print("Waiting for Streamlit app to load...")
        await asyncio.sleep(6)

        # Dismiss tour banner to keep layout clean
        await client.eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const dismiss = btns.find(b => b.innerText.includes('Dismiss Tour'));
            if (dismiss) dismiss.click();
        })()
        """)
        await asyncio.sleep(1.5)

        # -------------------------------------------------------------
        # Slide 1 (Picture 1): 3D Ray-Marched Flame (0g Spherical Mode)
        # -------------------------------------------------------------
        print("\n--- 1/7: Capturing Slide 1 (3D Ray-Marched Flame & Prediction) ---")
        await client.click_tab("Simulation and analytics")
        await asyncio.sleep(2)

        p1_path = OUTPUT_DIR / "slide_1_3d_microgravity_flame.png"
        rect1 = await client.eval_js("""
        (() => {
            const pred = document.querySelector('.st-key-card_pred');
            const flame = document.querySelector('.st-key-card_flame');
            if (!flame) return null;
            const target = pred ? pred.parentElement : flame;
            target.scrollIntoView({ behavior: 'instant', block: 'center' });
            const r = target.getBoundingClientRect();
            return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height };
        })()
        """)
        await client.capture_rect(rect1, p1_path)

        # -------------------------------------------------------------
        # Slide 2 (Picture 2): Historic Spaceflight Disasters (Mir 1997)
        # -------------------------------------------------------------
        print("\n--- 2/7: Capturing Slide 2 (Historic Spaceflight Fires: Mir 1997) ---")
        await client.click_tab("Documents & Synthesis")
        await asyncio.sleep(2.5)

        p2_path = OUTPUT_DIR / "slide_2_historic_spaceflight_fires.png"
        rect2 = await client.eval_js("""
        (() => {
            const el = document.querySelector('.st-key-card_d_historic');
            if (!el) return null;
            el.scrollIntoView({ behavior: 'instant', block: 'start' });
            const r = el.getBoundingClientRect();
            return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height };
        })()
        """)
        await client.capture_rect(rect2, p2_path)

        # -------------------------------------------------------------
        # Slide 3 (Picture 3): Interactive "What-If?" Contingency Scenarios
        # -------------------------------------------------------------
        print("\n--- 3/7: Capturing Slide 3 (Interactive 'What-If?' Spaceflight Emergencies) ---")
        await client.click_tab("Simulation and analytics")
        await asyncio.sleep(2)

        p3_path = OUTPUT_DIR / "slide_3_what_if_emergency_scenarios.png"
        rect3 = await client.eval_js("""
        (() => {
            const el = document.querySelector('.st-key-card_what_if');
            if (!el) return null;
            el.scrollIntoView({ behavior: 'instant', block: 'center' });
            const r = el.getBoundingClientRect();
            return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height };
        })()
        """)
        await client.capture_rect(rect3, p3_path)

        # -------------------------------------------------------------
        # Slide 4 (Picture 4): Live Non-Dimensional HUD & Conformal Curve
        # -------------------------------------------------------------
        print("\n--- 4/7: Capturing Slide 4 (Non-Dimensional Physics HUD & Conformal Curve) ---")
        # Click the "Lunar (34%)" preset button in the sidebar to showcase the Artemis atmosphere
        await client.eval_js("""
        (() => {
            const btns = Array.from(document.querySelectorAll('button'));
            const lunarBtn = btns.find(b => b.innerText.includes('Lunar (34%)'));
            if (lunarBtn) lunarBtn.click();
        })()
        """)
        await asyncio.sleep(2.5)

        p4_path = OUTPUT_DIR / "slide_4_physics_hud_and_conformal_curve.png"
        rect4 = await client.eval_js("""
        (() => {
            const chart = document.querySelector('.st-key-card_chart');
            const hud = document.querySelector('.st-key-card_physics_hud');
            if (!chart || !hud) return null;
            const r1 = chart.getBoundingClientRect();
            const r2 = hud.getBoundingClientRect();
            const top = Math.min(r1.top, r2.top) + window.scrollY;
            const bottom = Math.max(r1.bottom, r2.bottom) + window.scrollY;
            const left = Math.min(r1.left, r2.left) + window.scrollX;
            const right = Math.max(r1.right, r2.right) + window.scrollX;
            chart.scrollIntoView({ behavior: 'instant', block: 'start' });
            return { x: left, y: top, width: right - left, height: bottom - top };
        })()
        """)
        await client.capture_rect(rect4, p4_path)

        # -------------------------------------------------------------
        # Slide 5 (Picture 5): Deep-Space Comm Blackout Mode & AI Vault
        # -------------------------------------------------------------
        print("\n--- 5/7: Capturing Slide 5 (Deep-Space Comm Blackout & Air-Gapped AI) ---")
        # Ensure blackout toggle is turned on
        await client.eval_js("""
        (() => {
            const toggles = Array.from(document.querySelectorAll('input[type="checkbox"]'));
            const blackout = toggles.find(t => {
                const label = t.closest('label');
                return label && label.innerText.includes('Simulate Deep-Space Comm Blackout');
            });
            if (blackout && !blackout.checked) {
                blackout.click();
            }
        })()
        """)
        await asyncio.sleep(2)

        # Switch to Tab 5: AI assistant
        await client.click_tab("AI assistant")
        await asyncio.sleep(2)

        # Open the Question Discovery Vault expander if collapsed
        await client.eval_js("""
        (() => {
            const details = Array.from(document.querySelectorAll('[role="tabpanel"] details'));
            details.forEach(d => d.open = true);
        })()
        """)
        await asyncio.sleep(1)

        p5_path = OUTPUT_DIR / "slide_5_deep_space_comm_blackout.png"
        rect5 = await client.eval_js("""
        (() => {
            const panel = document.querySelector('[role="tabpanel"]');
            if (!panel) return null;
            panel.scrollIntoView({ behavior: 'instant', block: 'start' });
            const r = panel.getBoundingClientRect();
            return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: Math.min(r.height, 920) };
        })()
        """)
        await client.capture_rect(rect5, p5_path)

        # -------------------------------------------------------------
        # Slide 6 (Picture 6): Terrestrial Spin-offs & Earth Safety Matrix
        # -------------------------------------------------------------
        print("\n--- 6/7: Capturing Slide 6 (Terrestrial Spin-offs & Earth Safety Matrix) ---")
        await client.click_tab("Documents & Synthesis")
        await asyncio.sleep(2)

        # Expand the first two spinoff accordions
        await client.eval_js("""
        (() => {
            const expanders = Array.from(document.querySelectorAll('.st-key-card_d_terrestrial details'));
            expanders.slice(0, 2).forEach(d => d.open = true);
        })()
        """)
        await asyncio.sleep(1)

        p6_path = OUTPUT_DIR / "slide_6_terrestrial_spinoffs_matrix.png"
        rect6 = await client.eval_js("""
        (() => {
            const el = document.querySelector('.st-key-card_d_terrestrial');
            if (!el) return null;
            el.scrollIntoView({ behavior: 'instant', block: 'start' });
            const r = el.getBoundingClientRect();
            return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: Math.min(r.height, 900) };
        })()
        """)
        await client.capture_rect(rect6, p6_path)

        # -------------------------------------------------------------
        # Slide 7 (Picture 7): Provenance (SHA-256) & Flight SLA Telemetry
        # -------------------------------------------------------------
        print("\n--- 7/7: Capturing Slide 7 (System Provenance & Flight SLA Sidebar) ---")
        # Open both expanders in sidebar
        await client.eval_js("""
        (() => {
            const sidebarExpanders = Array.from(document.querySelectorAll('[data-testid="stSidebar"] details'));
            sidebarExpanders.forEach(d => d.open = true);
        })()
        """)
        await asyncio.sleep(1.5)

        p7_path = OUTPUT_DIR / "slide_7_system_provenance_and_flight_sla.png"
        rect7 = await client.eval_js("""
        (() => {
            const sidebar = document.querySelector('[data-testid="stSidebar"]');
            if (!sidebar) return null;
            const provExp = Array.from(sidebar.querySelectorAll('details')).find(d => d.innerText.includes('System Provenance'));
            const slaExp = Array.from(sidebar.querySelectorAll('details')).find(d => d.innerText.includes('Flight SLA'));
            if (!provExp || !slaExp) return null;
            provExp.scrollIntoView({ behavior: 'instant', block: 'start' });
            const r1 = provExp.getBoundingClientRect();
            const r2 = slaExp.getBoundingClientRect();
            const top = Math.min(r1.top, r2.top) + window.scrollY;
            const bottom = Math.max(r1.bottom, r2.bottom) + window.scrollY;
            const left = Math.min(r1.left, r2.left) + window.scrollX;
            const right = Math.max(r1.right, r2.right) + window.scrollX;
            return { x: left, y: top, width: right - left, height: bottom - top };
        })()
        """)
        await client.capture_rect(rect7, p7_path)

        # Also copy to root assets/slides for convenience
        root_slides = Path("assets/slides")
        root_slides.mkdir(parents=True, exist_ok=True)
        for img in OUTPUT_DIR.glob("*.png"):
            root_copy = root_slides / img.name
            root_copy.write_bytes(img.read_bytes())

        print("\nAll 7 high-resolution screenshots captured and copied successfully!")

        await client.close()
    finally:
        print("Terminating Chrome...")
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(run())
