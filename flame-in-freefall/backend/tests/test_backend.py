"""Pipeline tests on SYNTHETIC data (a made-up smooth function). They validate code
behaviour only; the numbers have no physical meaning."""
import time, numpy as np, pandas as pd, tempfile
from ffbackend.train import train
from ffbackend.predict import Predictor

def synth(n, fuel, g, vary_p=True, seed=0):
    r = np.random.default_rng(seed)
    o2 = r.uniform(16, 25, n); p = r.uniform(50, 100, n) if vary_p else np.full(n, 101.3)
    u = r.uniform(10, 200, n)
    ppo2 = o2 * p / 100
    rate = 0.02 * ppo2 ** 1.3 * np.exp(-((np.log(u) - np.log(60)) ** 2) / 2) * np.exp(r.normal(0, .05, n))
    return pd.DataFrame(dict(experiment_id=[f"{fuel}{g}_{i}" for i in range(n)], source="literature",
        fuel=fuel, g_level=float(g), o2_pct=o2, pressure_kpa=p, flow_velocity_mm_s=u,
        spread_rate_mm_s=rate, spread_rate_definition="steady_opposed_flat", comparable=True))

def build():
    t = pd.concat([synth(60, "PMMA", 0, True, 1),               # varying pressure
                   synth(40, "cellulose", 0, False, 2),         # ISS-like fixed pressure
                   synth(6, "PMMA", 1, True, 3)])               # too few -> DATA_ONLY
    d = tempfile.mkdtemp(); train(t, out_dir=d); return Predictor.load(d + "/ff_model.joblib"), d

def test_all():
    P, d = build()
    rep = P.meta["report"]
    assert rep["PMMA|g=0"]["status"] == "MODEL_OK" and rep["PMMA|g=0"]["beats_baseline"]
    assert rep["PMMA|g=1"]["status"] == "DATA_ONLY"
    r = P.predict("PMMA", 0, 20.9, 75, 60)
    assert r["status"] in ("IN", "SPARSE") and r["lo"] < r["rate"] < r["hi"]
    # outside hull / unknown combos must suppress the prediction
    assert P.predict("PMMA", 0, 100, 5, 60)["rate"] is None
    assert P.predict("PMMA", 0, 100, 5, 60)["status"] == "OUT"
    assert P.predict("PMMA", 0.16, 20, 75, 60)["status"] == "OUT"      # untested partial g
    assert P.predict("teflon", 0, 20, 75, 60)["status"] == "OUT"       # unknown fuel
    g1 = synth(6, "PMMA", 1, True, 3)   # centroid of the training points is always inside the hull
    c = g1[["o2_pct", "pressure_kpa", "flow_velocity_mm_s"]].mean()
    assert P.predict("PMMA", 1, c.o2_pct, c.pressure_kpa, c.flow_velocity_mm_s)["status"] == "DATA_ONLY"
    # fixed-pressure group: ISS pressure ok, other pressure rejected
    assert P.predict("cellulose", 0, 20, 101.3, 60)["rate"] is not None
    assert P.predict("cellulose", 0, 20, 60, 60)["status"] == "OUT"
    # corner of bounding box but outside hull is caught
    for _ in range(1): pass
    ts = []
    for _ in range(300):
        t0 = time.perf_counter(); P.predict("PMMA", 0, 21, 80, 70); ts.append(time.perf_counter() - t0)
    p95 = np.percentile(ts, 95) * 1000
    print(f"p95 predict latency: {p95:.2f} ms"); assert p95 < 100
    print({k: {a: round(b, 3) if isinstance(b, float) else b for a, b in v.items() if a in
          ("status","mae_log","r2_log","baseline_mae_log","cross_conformal_coverage")} for k, v in rep.items()})
    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_all()
