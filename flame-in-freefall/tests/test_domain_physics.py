"""Unit tests for the clean Domain Physics layer.

Tests pure combustion calculations, Péclet numbers, Damköhler numbers, and
thermal diffusivities with zero framework/Streamlit dependencies.
"""
from pathlib import Path
import os, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from domain.physics import (
    calculate_thermal_diffusivity,
    compute_peclet_number,
    compute_damkohler_number,
    classify_combustion_regime,
    evaluate_combustion_physics,
)
from domain.safety import evaluate_safety_officer_verdict
from domain.models import CombustionPhysicsResult, SafetyOfficerVerdict

def test_thermal_diffusivity_pressure_scaling():
    # At standard 101.325 kPa, alpha should equal base ~ 2.2e-5 m^2/s
    alpha_101 = calculate_thermal_diffusivity(101.325)
    assert abs(alpha_101 - 2.2e-5) < 1e-7

    # At half pressure (50.66 kPa), alpha should double
    alpha_50 = calculate_thermal_diffusivity(50.6625)
    assert abs(alpha_50 - 4.4e-5) < 1e-6

def test_peclet_number_and_regimes():
    # Low flow velocity -> Pe < 1 -> diffusion dominated
    pe_low = compute_peclet_number(flow_velocity_m_s=0.001, char_length_m=0.010, thermal_diffusivity_m2_s=2.2e-5)
    assert pe_low < 1.0
    assert "Diffusion-dominated" in classify_combustion_regime(pe_low)

    # Moderate flow -> 1 <= Pe < 5 -> transitional
    pe_mid = compute_peclet_number(flow_velocity_m_s=0.005, char_length_m=0.010, thermal_diffusivity_m2_s=2.2e-5)
    assert 1.0 <= pe_mid < 5.0
    assert "Transitional" in classify_combustion_regime(pe_mid)

    # High flow -> Pe >= 5 -> convection dominated
    pe_high = compute_peclet_number(flow_velocity_m_s=0.020, char_length_m=0.010, thermal_diffusivity_m2_s=2.2e-5)
    assert pe_high >= 5.0
    assert "Convection-dominated" in classify_combustion_regime(pe_high)

def test_evaluate_combustion_physics_dto():
    res = evaluate_combustion_physics(o2_pct=28.0, pressure_kpa=100.0, flow_mm_s=97.0)
    assert isinstance(res, CombustionPhysicsResult)
    assert res.peclet_number > 0
    assert res.damkohler_number > 0
    assert res.thermal_diffusivity_cm2_s > 0
    d = res.to_dict()
    assert "peclet_number" in d
    assert "flow_regime" in d

def test_evaluate_safety_officer_verdict():
    # Covered
    cov = evaluate_safety_officer_verdict({"verdict": "COVERED", "ppo2": 21.3}, "ISS Standard")
    assert isinstance(cov, SafetyOfficerVerdict)
    assert "GO" in cov.status_banner
    assert cov.badge_color == "green"
    assert cov.normoxic_delta == 0.0

    # Near
    near = evaluate_safety_officer_verdict({"verdict": "NEAR", "ppo2": 24.5}, "Lunar Alt")
    assert "CAUTION" in near.status_banner
    assert near.badge_color == "orange"

    # Not Covered
    out = evaluate_safety_officer_verdict({"verdict": "NOT_COVERED", "ppo2": 28.0, "reasons": ["partial-g gap"]}, "Lunar Base")
    assert "NO-GO" in out.status_banner
    assert out.badge_color == "red"
    assert out.gaps_count == 1

if __name__ == "__main__":
    test_thermal_diffusivity_pressure_scaling()
    test_peclet_number_and_regimes()
    test_evaluate_combustion_physics_dto()
    test_evaluate_safety_officer_verdict()
    print("DOMAIN LAYER TESTS PASSED")
