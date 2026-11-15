"""Tests for risk cards on the REAL model and findings. Run from the repo root: python -m insights.tests.test_risk_cards"""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT))
from ffbackend.predict import Predictor
from insights.findings import load_findings, rank_findings
from insights.scenarios import SCENARIOS, Scenario, evaluate
from insights.risk_cards import build_cards, CARDS, STATES

def cards_for(sc, P, exp, F):
    ev = evaluate(sc, P, exp); r = rank_findings(F, sc.g, sc.o2_pct, sc.pressure_kpa, sc.tags); return ev, {c["key"]: c for c in build_cards(ev, r)}

def test_all():
    F = load_findings(); P = Predictor.load(ROOT / "backend/artifacts/ff_model.joblib")
    exp = pd.read_csv(ROOT / "phase0/raw/zarm_experiments_global.csv"); exp["o2_pct"] = exp["o2_frac"] * 100
    assert all(f["categories"] for f in F) and all(f["verified"] == "yes" for f in F)
    ev, c = cards_for(SCENARIOS["lunar"], P, exp, F)
    assert list(c) == [k for k, _ in CARDS] and all(v["state"] in STATES for v in c.values())
    assert c["spread"]["state"] == "NO_PREDICTION" and c["spread"]["numbers"] is None and c["spread"]["findings"]            # no model numbers for an uncovered scenario
    assert c["limit"]["state"] == "MEASURED" and any(f["id"] == "F15" for f in c["limit"]["findings"]) and "does not state the atmosphere" in c["limit"]["note"]
    for k in ("ignition", "detection", "suppression", "materials", "ventilation"):                                              # evidence exists but is not direct for lunar gravity
        assert c[k]["state"] == "INDIRECT", (k, c[k]["state"])
    assert all(v["n_unverified"] == 0 for v in c.values())                           # all items in findings library are now verified
    ev2, c2 = cards_for(SCENARIOS["iss"], P, exp, F)
    assert c2["limit"]["state"] == "MEASURED" and c2["limit"]["findings"][0]["id"] == "F12" and c2["limit"]["n_unverified"] == 0   # microgravity experiment, verified against the paper
    assert c2["spread"]["state"] == "NO_PREDICTION" and "just outside" in c2["spread"]["note"]
    cov = Scenario("c", "Custom covered", 84.0, 28.0, 0.0, ("microgravity",), "test"); ev3, c3 = cards_for(cov, P, exp, F)
    pred = ev3["prediction"]; assert c3["spread"]["state"] == "PREDICTED" and c3["spread"]["numbers"] == dict(rate=pred["rate"], lo=pred["lo"], hi=pred["hi"])
    # a topic without any finding is reported as a data gap, never as safe
    F2 = [f for f in F if "ventilation" not in f["categories"]]; ev4 = evaluate(SCENARIOS["lunar"], P, exp)
    c4 = {x["key"]: x for x in build_cards(ev4, rank_findings(F2, 0.16, 34, 56.5, SCENARIOS["lunar"].tags))}
    assert c4["ventilation"]["state"] == "NONE" and c4["ventilation"]["findings"] == [] and "data gap" in c4["ventilation"]["note"]
    print("RISK CARD TESTS PASSED | lunar:", {k: v["state"] for k, v in c.items()})

if __name__ == "__main__":
    test_all()
