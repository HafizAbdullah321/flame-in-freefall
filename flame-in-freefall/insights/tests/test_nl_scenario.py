"""Tests for Natural-Language Scenario Parsing (REQ-E7).
Validates:
- At least 10 diverse natural-language phrasings parse correctly
- Unit conversions (psi, psia, atm, bar, mbar to kPa)
- Gravity mapping (Moon 0.16g, Mars 0.38g, ISS/free fall/microgravity 0g, Earth 1g)
- Range validation and rejection of unphysical inputs
- Ambiguous inputs trigger clarifying questions rather than guessing
- Mock LLM integration and fallback

Run from repo root: python -m insights.tests.test_nl_scenario
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from insights.nl_scenario import (
    parse_scenario_regex,
    parse_scenario_nl,
    _to_kpa,
    P_MIN_KPA,
    P_MAX_KPA,
    O2_MIN_PCT,
    O2_MAX_PCT,
)
from rag.llm import MockLLM, LLMError

# 12 diverse phrasings (exceeds REQ-E7 requirement of at least 10)
TEST_PHRASINGS = [
    ("lunar habitat at 8 psi and 30% oxygen", 55.16, 30.0, 0.16),
    ("Mars base at 56.5 kPa with 34% O2", 56.5, 34.0, 0.38),
    ("ISS cabin at 14.7 psia and 21% oxygen", 101.35, 21.0, 0.0),
    ("Gateway in free fall at 70 kPa and 26.5% oxygen", 70.0, 26.5, 0.0),
    ("Moon surface habitat at 0.3 bar, 32% oxygen", 30.0, 32.0, 0.16),
    ("microgravity transit craft at 0.55 atm with 30% O2", 55.73, 30.0, 0.0),
    ("Earth ground test at 1 atm and 21% O2", 101.32, 21.0, 1.0),
    ("Lunar lander at 0.16 g, 8.2 psi, 34% oxygen", 56.54, 34.0, 0.16),
    ("Deep space vehicle in zero-g at 60 kPa, 28% O2", 60.0, 28.0, 0.0),
    ("Martian colony dome at 10.2 psia and 26.5% O2", 70.33, 26.5, 0.38),
    ("Artemis basecamp with 56.5 kPa and 34 percent oxygen", 56.5, 34.0, 0.16),
    ("Zero gravity module at 800 mbar, 25% oxygen", 80.0, 25.0, 0.0),
]

def test_phrasings_parsing():
    for phrase, exp_p, exp_o2, exp_g in TEST_PHRASINGS:
        r = parse_scenario_regex(phrase)
        assert r["ok"], f"Failed to parse: '{phrase}' | errors: {r['errors']}"
        sc = r["scenario"]
        assert sc is not None
        assert abs(r["pressure_kpa"] - exp_p) <= 0.1, f"P mismatch for '{phrase}': got {r['pressure_kpa']}, exp {exp_p}"
        assert abs(r["o2_pct"] - exp_o2) <= 0.1, f"O2 mismatch for '{phrase}': got {r['o2_pct']}, exp {exp_o2}"
        assert abs(r["gravity_g"] - exp_g) <= 0.01, f"g mismatch for '{phrase}': got {r['gravity_g']}, exp {exp_g}"

def test_unit_conversions():
    assert abs(_to_kpa(14.7, "psi") - 101.35) <= 0.1
    assert abs(_to_kpa(1.0, "atm") - 101.32) <= 0.1
    assert abs(_to_kpa(0.5, "bar") - 50.0) <= 0.1
    assert abs(_to_kpa(600, "mbar") - 60.0) <= 0.1
    assert abs(_to_kpa(56.5, "kpa") - 56.5) <= 0.1

def test_clarifications_on_ambiguity():
    # Missing pressure
    r1 = parse_scenario_regex("lunar habitat with 30% oxygen")
    assert not r1["ok"]
    assert "pressure" in r1["clarification_needed"].lower()

    # Missing oxygen
    r2 = parse_scenario_regex("Mars base at 56.5 kPa")
    assert not r2["ok"]
    assert "oxygen" in r2["clarification_needed"].lower()

    # Missing gravity
    r3 = parse_scenario_regex("cabin at 8 psi and 30% oxygen")
    assert not r3["ok"]
    assert "gravity" in r3["clarification_needed"].lower()

def test_out_of_range_rejection():
    # Unphysically high pressure
    r1 = parse_scenario_regex("lunar habitat at 500 psi and 30% oxygen")
    assert not r1["ok"]
    assert any("pressure" in e.lower() for e in r1["errors"])

    # Unphysically low pressure
    r2 = parse_scenario_regex("lunar habitat at 0.5 psi and 30% oxygen")
    assert not r2["ok"]
    assert any("pressure" in e.lower() for e in r2["errors"])

    # Unphysically high oxygen
    r3 = parse_scenario_regex("lunar habitat at 8 psi and 120% oxygen")
    assert not r3["ok"]
    assert any("oxygen" in e.lower() for e in r3["errors"])

    # Unphysically low oxygen
    r4 = parse_scenario_regex("lunar habitat at 8 psi and 5% oxygen")
    assert not r4["ok"]
    assert any("oxygen" in e.lower() for e in r4["errors"])

def test_mock_llm():
    # Test LLM parsing when given unstructured phrase
    llm_json = '{"pressure": 56.5, "pressure_unit": "kpa", "oxygen_pct": 34.0, "gravity_g": 0.16, "destination": "Lunar base"}'
    llm = MockLLM(llm_json)
    r = parse_scenario_nl("We are designing an Artemis lunar base with 56.5 kPa atmosphere and 34 percent O2.", llm=llm)
    assert r["ok"]
    assert abs(r["pressure_kpa"] - 56.5) <= 0.1
    assert r["gravity_g"] == 0.16

    # Test LLM error falls back to regex
    llm_err = MockLLM(LLMError("Timeout"))
    r_err = parse_scenario_nl("Moon habitat at 8 psi and 30% oxygen", llm=llm_err)
    assert r_err["ok"]
    assert r_err["method"] == "REGEX"

def test_all():
    test_phrasings_parsing()
    test_unit_conversions()
    test_clarifications_on_ambiguity()
    test_out_of_range_rejection()
    test_mock_llm()
    print("NATURAL-LANGUAGE SCENARIO TESTS PASSED | 12 phrasings, unit conversions, clarifications & validations confirmed")

if __name__ == "__main__":
    test_all()

