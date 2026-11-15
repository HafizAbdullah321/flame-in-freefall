"""Tests for the Audience Persona adapters.
Run from repo root: python -m insights.tests.test_persona
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from insights.persona import (
    PERSONAS,
    calculate_combustion_physics,
    get_safety_officer_verdict,
    get_student_fundamentals,
)

def test_persona_functions():
    assert len(PERSONAS) == 4
    assert "All-in-One (Standard)" in PERSONAS
    assert "Flight Safety Officer (Operational)" in PERSONAS
    assert "Aerospace Researcher (Academic)" in PERSONAS
    assert "Student & Educator (Foundational)" in PERSONAS

    # Physics calculations
    phys = calculate_combustion_physics(o2_pct=28.0, pressure_kpa=84.0, flow_mm_s=96.0, v_spread_mm_s=3.5)
    assert phys["peclet_number"] > 0
    assert phys["damkohler_number"] > 0
    assert "flow_regime" in phys
    assert phys["thermal_diffusivity_cm2_s"] > 0
    assert phys["conformal_q90_margin_mm_s"] == 0.22

    # Safety officer verdict
    safe_mock = {"verdict": "COVERED", "ppo2": 23.5, "reasons": []}
    v_safe = get_safety_officer_verdict(safe_mock, "Custom Covered")
    assert "GO" in v_safe["status_banner"]
    assert v_safe["badge_color"] == "green"

    outside_mock = {"verdict": "NOT_COVERED", "ppo2": 19.2, "reasons": ["Pressure outside", "0.16g not tested"]}
    v_out = get_safety_officer_verdict(outside_mock, "Lunar Habitat")
    assert "NO-GO" in v_out["status_banner"]
    assert v_out["badge_color"] == "red"
    assert v_out["gaps_count"] == 2

    # Student fundamentals
    funds = get_student_fundamentals()
    assert len(funds) >= 3
    for f in funds:
        assert f["question"]
        assert f["answer"]

    print("PERSONA TESTS PASSED")

if __name__ == "__main__":
    test_persona_functions()

