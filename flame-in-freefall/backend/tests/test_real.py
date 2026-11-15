"""Tests on the REAL harmonized table (22 ZARM drop-tower experiments).
Run: python -m tests.test_real        (set FF_TABLE to override the table path)"""
import os, json, time, tempfile, numpy as np, pandas as pd
from pathlib import Path
from ffbackend.config import Config
from ffbackend.train import train
from ffbackend.predict import Predictor

TABLE = Path(os.environ.get("FF_TABLE", "../phase0/out/harmonized.csv"))
GOLDEN = Path(__file__).with_name("golden.json")
KEYS = {"rate", "lo", "hi", "status", "message", "disclaimer"}

def build():
    t = pd.read_csv(TABLE)
    d = tempfile.mkdtemp()
    train(t, Config(model_feats=("o2_pct", "fuel_coverage")), d)
    return Predictor.load(d + "/ff_model.joblib"), t[t.comparable]

def test_all():
    P, d = build()
    rep = P.meta["report"]["PMMA|g=0"]
    assert rep["status"] == "MODEL_OK" and rep["beats_baseline"], rep
    assert 0.80 <= rep["cross_conformal_coverage"] <= 1.0, rep["cross_conformal_coverage"]
    # contract (REQ-B1)
    r = P.predict("PMMA", 0.0, 28, 84, 97, 1.0)
    assert set(r) == KEYS and r["lo"] < r["rate"] < r["hi"]
    for bad in [("PMMA", 0.0, float("nan"), 84, 97), ("PMMA", 0.0, "x", 84, 97), ("teflon", 0.0, 28, 84, 97), ("PMMA", 1.0, 28, 84, 97)]:
        rb = P.predict(*bad); assert set(rb) == KEYS and rb["status"] == "OUT" and rb["rate"] is None, bad
    # oxygen line (REQ-B3): single control stays inside the envelope
    lo, hi = P.safe_o2_range("PMMA", 0.0, 1.0)
    assert lo < 24 and hi > 35, (lo, hi)
    for o in np.linspace(lo, hi, 10):
        ro = P.predict_on_line("PMMA", 0.0, o, 1.0)
        assert ro["status"] in ("IN", "SPARSE") and 1.0 < ro["rate"] < 10.0, (o, ro)
    # guard (REQ-B4): midpoints between neighbouring experiments accepted, off-line combinations refused
    e = d.groupby("experiment_id")[["o2_pct", "pressure_kpa", "flow_velocity_mm_s", "fuel_coverage"]].mean().sort_values("o2_pct")
    for a, b in zip(e.index[:-1], e.index[1:]):
        m = (e.loc[a] + e.loc[b]) / 2
        rm = P.predict("PMMA", 0.0, m.o2_pct, m.pressure_kpa, m.flow_velocity_mm_s, m.fuel_coverage)
        assert rm["status"] in ("IN", "SPARSE"), (a, b, rm["message"])
    for o, p in [(36, 101), (21, 62), (28, 62), (30, 101), (25, 70), (60, 30)]:
        ro = P.predict("PMMA", 0.0, o, p, 100, 1.0); assert ro["status"] == "OUT" and ro["rate"] is None, (o, p)
    assert P.predict("PMMA", 0.0, 28, 84, 97, 0.6)["status"] == "OUT"          # fuel coverage below tested range
    # physical sanity: spread rate rises with oxygen along the line
    rates = [P.predict_on_line("PMMA", 0.0, o, 1.0)["rate"] for o in (23, 27, 31, 35)]
    assert all(np.diff(rates) > 0), rates
    # latency
    ts = []
    for _ in range(300):
        t0 = time.perf_counter(); P.predict_on_line("PMMA", 0.0, 28, 0.9); ts.append(time.perf_counter() - t0)
    assert np.percentile(ts, 95) * 1000 < 100
    # golden regression
    pts = [(o, f) for o in (23, 26, 29, 32, 35) for f in (0.8, 1.0)]
    cur = {f"{o}|{f}": P.predict_on_line("PMMA", 0.0, o, f)["rate"] for o, f in pts}
    if not GOLDEN.exists():
        GOLDEN.write_text(json.dumps(cur, indent=1)); print("golden.json written (first run)")
    else:
        old = json.loads(GOLDEN.read_text())
        for k, v in old.items():
            assert (v is None and cur[k] is None) or abs(cur[k] - v) / v < 0.01, (k, v, cur[k])
    print("model:", rep["chosen"], "| safe O2 range: %.1f-%.1f%%" % (lo, hi), "| p95 latency %.2f ms" % (np.percentile(ts, 95) * 1000))
    print("REAL-DATA TESTS PASSED")

if __name__ == "__main__":
    test_all()
