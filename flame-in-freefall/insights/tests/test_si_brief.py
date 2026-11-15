"""Tests for the SI brief verifier and fallback with a MOCK LLM (no network). Run from the repo root: python -m insights.tests.test_si_brief"""
import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT))
from ffbackend.predict import Predictor
from insights.findings import load_findings, rank_findings
from insights.scenarios import SCENARIOS, Scenario, evaluate
from insights.risk_cards import build_cards
from insights.brief import build_brief
from insights import si_brief as sb
from rag.llm import MockLLM, LLMError

def setup(sc):
    F = load_findings(); P = Predictor.load(ROOT / "backend/artifacts/ff_model.joblib")
    exp = pd.read_csv(ROOT / "phase0/raw/zarm_experiments_global.csv"); exp["o2_pct"] = exp["o2_frac"] * 100
    ev = evaluate(sc, P, exp); r = rank_findings(F, sc.g, sc.o2_pct, sc.pressure_kpa, sc.tags); inputs = sb.build_inputs(ev, r, build_cards(ev, r))
    return ev, r, inputs, build_brief(ev, r)

GOOD_LUNAR = """Scenario: Lunar habitat at 56.5 kPa and 34 percent oxygen, oxygen partial pressure 19.2 kPa, gravity 0.16 g.
Our data: There is no prediction for this environment. Our experiments are microgravity only and pressure 56.5 kPa is below the tested 61.6 kPa.
Evidence: Material flammability limits are not expected to meet current requirements at 34% oxygen and 8.2 psi, and reduced gravity is expected to change flame spread [F07]. LUCI produced the first extended lunar-gravity combustion tests, though these findings are not yet verified [F15].
Gaps: No measured flame spread at 0.16 g in this atmosphere is in the library.
Follow-up: Which materials need testing first at lunar gravity?"""

def run_with(reply, inputs, fb, daily=None):
    sb._CACHE.clear(); llm = MockLLM(reply); return sb.generate_brief(llm, inputs, fb, daily), llm

def test_all():
    ev, r, inp, fb = setup(SCENARIOS["lunar"])
    assert inp["model"] is None and inp["scenario"]["verdict"] == "NOT_COVERED" and len(inp["findings"]) == 5
    res, llm = run_with(GOOD_LUNAR, inp, fb); assert res["tier"] == "SI" and "Not certified fire-safety guidance" in res["text"] and len(llm.calls) == 1, res["reasons"]
    s, u = llm.calls[0]; assert s == sb.SYSTEM_PROMPT and "Use ONLY" in s and "<facts>" in u and "F07" in u and "reasons" in u
    # each kind of bad output is caught and replaced by the rule-based brief
    bad = {   # name: (text, substring that the verifier must report: each rule is tested on its own)
      "hallucinated number": (GOOD_LUNAR.replace("0.16 g.", "0.16 g, flame spread of 7.3 mm/s."), "number 7.3"),
      "unknown id": (GOOD_LUNAR.replace("[F15]", "[F99]"), "unknown finding id F99"),
      "uncited evidence": (GOOD_LUNAR.replace(" [F07]", ""), "no citation"),
      "banned phrase": (GOOD_LUNAR.replace("Gaps: No measured", "Gaps: The habitat is safe. No measured"), "banned phrase"),
      "too long": (GOOD_LUNAR + " " + "word " * 260, "longer than"),
      "missing section": (GOOD_LUNAR.replace("Gaps:", "Notes:"), "missing section Gaps"),
      "prediction for uncovered (allowed number)": (GOOD_LUNAR.replace("There is no prediction for this environment.", "There is no prediction. The model predicts 19.2 mm/s here."), "states a prediction"),
      "no-prediction statement missing": (GOOD_LUNAR.replace("There is no prediction for this environment.", "Our experiments are limited."), "no prediction"),
      "too many follow-ups": (GOOD_LUNAR + "\nWhat about Mars?\nAnd the EVA suit?", "more than two follow-up"),
      "text before label": ("Hello.\n" + GOOD_LUNAR, "before the first label"),
      "malformed citation": (GOOD_LUNAR.replace("[F07]", "[F07"), "no citation"),
    }
    for name, (text, expect) in bad.items():
        ok, why = sb.verify_brief(text, inp); assert not ok and any(expect in w for w in why), (name, why)
        res, _ = run_with(text, inp, fb); assert res["tier"] == "RULE_BASED" and res["text"] == fb and "failed verification" in res["reasons"][0], (name, res["reasons"])
    # numbers: rounding allowed, invention not
    ok, _ = sb.verify_brief(GOOD_LUNAR.replace("19.2 kPa", "19 kPa"), inp); assert ok
    ok, why = sb.verify_brief(GOOD_LUNAR.replace("19.2 kPa", "21.2 kPa"), inp); assert not ok and any("21.2" in w for w in why)
    # LLM failure, no key, daily cap
    sb._CACHE.clear(); r1 = sb.generate_brief(MockLLM(LLMError("APITimeoutError")), inp, fb); assert r1["tier"] == "RULE_BASED" and "unavailable" in r1["reasons"][0]
    r2 = sb.generate_brief(None, inp, fb); assert r2["tier"] == "RULE_BASED" and "no API key" in r2["reasons"][0]
    class Cap:  # daily cap exhausted
        def available(self): return False
        def record(self): raise AssertionError("must not call")
    llm = MockLLM(GOOD_LUNAR); r3 = sb.generate_brief(llm, inp, fb, Cap()); assert r3["tier"] == "RULE_BASED" and llm.calls == []
    # caching: identical facts do not call the LLM twice; changed facts do
    sb._CACHE.clear(); llm = MockLLM(GOOD_LUNAR); a = sb.generate_brief(llm, inp, fb); b = sb.generate_brief(llm, inp, fb); assert len(llm.calls) == 1 and b["cached"] and not a["cached"]
    # covered scenario: model numbers allowed (and only those)
    cov = Scenario("c", "Custom covered", 84.0, 28.0, 0.0, ("microgravity",), "test"); ev2, r2_, inp2, fb2 = setup(cov); p = inp2["model"]; assert p
    text = (f"Scenario: Microgravity at 84.0 kPa and 28 percent oxygen.\nOur data: This environment is inside the tested range; the model estimates {p['rate_mm_s']} mm/s for thin PMMA "
            f"(90% interval {p['interval_90_mm_s'][0]} to {p['interval_90_mm_s'][1]}).\nEvidence: Spread over PMMA first rises then falls with opposed flow [F12].\nGaps: No data at partial gravity.")
    ok, why = sb.verify_brief(text, inp2); assert ok, why
    ok, why = sb.verify_brief(text.replace(str(p["rate_mm_s"]), "9.99"), inp2); assert not ok
    print("SI BRIEF TESTS PASSED | 11 bad outputs rejected, each by its own rule, rounding allowed, fallback/cap/cache verified")

if __name__ == "__main__":
    test_all()
