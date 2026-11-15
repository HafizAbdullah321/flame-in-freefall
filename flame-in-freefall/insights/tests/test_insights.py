"""Tests for the mission-insights logic on the REAL model and experiments table. Run from the repo root: python -m insights.tests.test_insights"""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT))
from ffbackend.predict import Predictor
from insights.findings import load_findings, rank_findings, EVIDENCE_WEIGHT
from insights.scenarios import SCENARIOS, Scenario, evaluate, tested_ranges
from insights.brief import build_brief

def test_all():
    F = load_findings(); assert len(F) >= 16
    assert all(f["source_url"].startswith("https://") and f["evidence"] in EVIDENCE_WEIGHT and f["finding"] and f["id"] for f in F)
    assert len({f["id"] for f in F}) == len(F)
    P = Predictor.load(ROOT / "backend/artifacts/ff_model.joblib")
    exp = pd.read_csv(ROOT / "phase0/raw/zarm_experiments_global.csv"); exp["o2_pct"] = exp["o2_frac"] * 100; exp["p_kpa"] = exp["p_kpa"]
    rg = tested_ranges(exp); assert 21 < rg["o2"][0] < 22 and 35 < rg["o2"][1] < 37 and 20 < rg["ppo2"][0] < 22 and rg["ppo2"][1] < 26
    # ranking: lunar scenario surfaces lunar-gravity evidence; ISS scenario surfaces microgravity experiments
    lun = SCENARIOS["lunar"]; r = rank_findings(F, lun.g, lun.o2_pct, lun.pressure_kpa, lun.tags)
    top5 = [x["id"] for x in r[:5]]; assert {"F04", "F07"} <= set(top5) and "F13" not in top5, top5
    assert r[0]["score"] >= r[-1]["score"] and all(0 <= x["score"] <= 1 for x in r)
    iss = SCENARIOS["iss"]; r2 = rank_findings(F, iss.g, iss.o2_pct, iss.pressure_kpa, iss.tags)
    ids2 = [x["id"] for x in r2]; assert ids2.index("F12") < ids2.index("F04") and ids2.index("F14") < ids2.index("F05"), ids2[:6]
    tr = SCENARIOS["transit"]; r3 = rank_findings(F, tr.g, tr.o2_pct, tr.pressure_kpa, tr.tags); assert "F14" in [x["id"] for x in r3[:4]], [x["id"] for x in r3[:6]]
    # evidence strength matters: same relevance, stronger evidence ranks higher
    base = dict(F[0]); a = dict(base, id="A", evidence="experiment_micro"); b = dict(base, id="B", evidence="planning")
    assert rank_findings([b, a], 0.0, 28, 84)[0]["id"] == "A"
    # scenario evaluation is honest
    e_iss = evaluate(iss, P, exp); assert e_iss["verdict"] == "NEAR" and e_iss["prediction"] is None and e_iss["comparator"], e_iss["reasons"]
    e_tr = evaluate(tr, P, exp); assert e_tr["verdict"] == "NOT_COVERED" and e_tr["prediction"] is None
    assert any("Pressure" in x for x in e_tr["reasons"]) and any("partial pressure" in x for x in e_tr["reasons"])
    for k in ("lunar", "lunar_alt", "mars"):
        e = evaluate(SCENARIOS[k], P, exp); assert e["verdict"] == "NOT_COVERED" and e["prediction"] is None and any("No experiments" in x for x in e["reasons"]), k
    cov = Scenario("c", "Custom covered", 84.0, 28.0, 0.0, ("microgravity",), "test"); e_c = evaluate(cov, P, exp)
    assert e_c["verdict"] == "COVERED" and e_c["prediction"]["rate"] > 2 and e_c["prediction"]["lo"] < e_c["prediction"]["rate"] < e_c["prediction"]["hi"]
    # brief never states a prediction it does not have, always carries sources and the disclaimer
    for k, e in (("transit", e_tr), ("lunar", evaluate(lun, P, exp)), ("iss", e_iss)):
        s = SCENARIOS[k]; txt = build_brief(e, rank_findings(F, s.g, s.o2_pct, s.pressure_kpa, s.tags))
        assert "Predicted flame spread rate" not in txt and "not a prediction" in txt.lower() or k == "lunar" and "no prediction" in txt.lower() or "make no prediction" in txt
        assert "https://" in txt and "Not certified fire-safety guidance" in txt and "Data gaps" in txt
    txt = build_brief(e_c, rank_findings(F, 0, 28, 84, ("microgravity",))); assert "Predicted flame spread rate" in txt and "inside the tested range" in txt
    print("INSIGHTS TESTS PASSED |", {k: evaluate(v, P, exp)["verdict"] for k, v in SCENARIOS.items()}, "| lunar top 3:", top5[:3])

if __name__ == "__main__":
    test_all()
