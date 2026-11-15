"""Resource tests: server memory stays under budget and does not leak across many reruns; prediction latency stays under 100 ms.
Run from the repo root:  python tests/test_resources.py        (needs: pip install psutil streamlit)"""
import os, sys, time
from pathlib import Path
import numpy as np, psutil
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
BUDGET_MB, GROWTH_MB = 1024, 80          # design target about 1 GB (hard ceiling 4 GB in the PRD)

def rss_mb(): return psutil.Process().memory_info().rss / 1e6

def test_latency():
    from ffbackend.predict import Predictor
    P = Predictor.load("backend/artifacts/ff_model.joblib"); ts = []
    for i in range(400):
        t0 = time.perf_counter(); P.predict_on_line("PMMA", 0.0, 22 + (i % 14), 0.75 + (i % 25) / 100); ts.append(time.perf_counter() - t0)
    p95 = np.percentile(ts, 95) * 1000; assert p95 < 100, p95
    t0 = time.perf_counter(); [P.predict_on_line("PMMA", 0.0, o, 1.0) for o in np.arange(22, 36, 0.25)]; curve_ms = (time.perf_counter() - t0) * 1000
    assert curve_ms < 1000, curve_ms
    return p95, curve_ms

def test_memory():
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(ROOT / "app/streamlit_app.py"), default_timeout=90).run(); assert not at.exception
    base = rss_mb(); marks = {}
    for i in range(30):
        at.sidebar.slider[0].set_value(22.0 + (i * 1.5) % 13); at.sidebar.slider[1].set_value(0.75 + (i % 6) * 0.05)
        if i % 7 == 3: at.sidebar.radio[0].set_value("1g (Earth)")
        if i % 7 == 5: at.sidebar.radio[0].set_value("0g (microgravity)")
        at.run(); assert not at.exception, at.exception
        if i in (9, 29): marks[i] = rss_mb()
    assert marks[29] < BUDGET_MB, f"RSS {marks[29]:.0f} MB over budget"
    assert marks[29] - marks[9] < GROWTH_MB, f"memory grew {marks[29]-marks[9]:.0f} MB between rerun 10 and 30 (possible leak)"
    return base, marks[9], marks[29]

if __name__ == "__main__":
    p95, curve = test_latency(); base, m10, m30 = test_memory()
    print(f"predict p95 {p95:.2f} ms | 57-point curve {curve:.0f} ms | RSS after load {base:.0f} MB, after 10 reruns {m10:.0f} MB, after 30 {m30:.0f} MB (budget {BUDGET_MB} MB)")
    print("RESOURCE TESTS PASSED")
