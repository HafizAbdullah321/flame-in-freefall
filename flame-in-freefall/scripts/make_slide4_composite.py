import asyncio, websockets, requests, json, time, subprocess, base64
from pathlib import Path
from PIL import Image
import io

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222
APP_URL = "http://localhost:8501"

async def make_slide4_composite():
    proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        "--no-first-run",
        "--window-size=1920,1200",
        "--force-device-scale-factor=1"
    ])
    time.sleep(2.5)
    try:
        t_res = requests.put(f"http://127.0.0.1:{PORT}/json/new?{APP_URL}")
        ws_url = t_res.json()["webSocketDebuggerUrl"]

        async with websockets.connect(ws_url, max_size=30_000_000) as ws:
            msg_id = 0
            async def call(method, params=None):
                nonlocal msg_id
                msg_id += 1
                cid = msg_id
                await ws.send(json.dumps({"id": cid, "method": method, "params": params or {}}))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get("id") == cid: return r.get("result", {})

            await call("Page.enable")
            await call("Runtime.enable")
            await asyncio.sleep(5)

            # Dismiss tour
            await call("Runtime.evaluate", {
                "expression": """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const dismiss = btns.find(b => b.innerText.includes('Dismiss Tour'));
                    if (dismiss) dismiss.click();
                })()
                """
            })
            await asyncio.sleep(1)

            # Click Lunar (34%) preset to select Artemis atmosphere
            await call("Runtime.evaluate", {
                "expression": """
                (() => {
                    const btns = Array.from(document.querySelectorAll('button'));
                    const lunarBtn = btns.find(b => b.innerText.includes('Lunar (34%)'));
                    if (lunarBtn) lunarBtn.click();
                })()
                """
            })
            await asyncio.sleep(2.5)

            # 1. Capture the scatter chart
            r1 = await call("Runtime.evaluate", {
                "expression": """
                (() => {
                    const chart = document.querySelector('.st-key-card_chart');
                    if (!chart) return null;
                    chart.scrollIntoView({ behavior: 'instant', block: 'center' });
                    const r = chart.getBoundingClientRect();
                    return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height };
                })()
                """,
                "returnByValue": True
            })
            rect1 = r1.get("result", {}).get("value")

            # 2. Capture the 4 HUD stat cards
            r2 = await call("Runtime.evaluate", {
                "expression": """
                (() => {
                    const hud = document.querySelector('.st-key-card_physics_hud');
                    if (!hud) return null;
                    hud.scrollIntoView({ behavior: 'instant', block: 'center' });
                    const r = hud.getBoundingClientRect();
                    // Get only the header and the 4 stat cards (exclude the large expander at the bottom)
                    const cardsRow = hud.querySelector('.stHorizontalBlock');
                    const cardsRect = cardsRow ? cardsRow.getBoundingClientRect() : r;
                    const top = r.top + window.scrollY;
                    const bottom = (cardsRow ? cardsRow.getBoundingClientRect().bottom : r.bottom) + window.scrollY;
                    return { x: r.left + window.scrollX, y: top, width: r.width, height: bottom - top + 15 };
                })()
                """,
                "returnByValue": True
            })
            rect2 = r2.get("result", {}).get("value")

            print("Chart rect:", rect1)
            print("HUD rect:", rect2)

            # Capture Chart
            shot1 = await call("Page.captureScreenshot", {
                "format": "png",
                "clip": {"x": rect1["x"], "y": rect1["y"], "width": rect1["width"], "height": rect1["height"], "scale": 1.2}
            })
            img_chart = Image.open(io.BytesIO(base64.b64decode(shot1["data"])))

            # Capture HUD cards
            shot2 = await call("Page.captureScreenshot", {
                "format": "png",
                "clip": {"x": rect2["x"], "y": rect2["y"], "width": rect2["width"], "height": rect2["height"], "scale": 1.2}
            })
            img_hud = Image.open(io.BytesIO(base64.b64decode(shot2["data"])))

            # Stack them vertically with dark navy background
            w = max(img_chart.width, img_hud.width)
            h = img_chart.height + img_hud.height + 10
            composite = Image.new("RGB", (w, h), (11, 15, 25))
            composite.paste(img_chart, (0, 0))
            composite.paste(img_hud, (0, img_chart.height + 10))

            out_path = Path("slide4_perfect_composite.png")
            composite.save(out_path)
            print(f"Created slide4_perfect_composite.png: size={composite.size}, file_size={out_path.stat().st_size/1024:.1f} KB")

    finally:
        proc.terminate()

asyncio.run(make_slide4_composite())

