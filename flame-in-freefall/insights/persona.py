"""Audience persona adapters for the Flame in Freefall dashboard.

Adapts the presentation layer for:
1. Flight Safety Officer (Operational): Focuses on Go/No-Go envelope status, certified bounds, and risk data gaps.
2. Aerospace Researcher (Academic): Focuses on dimensionless combustion physics (Peclet, Damkohler), convective-diffusive scaling, and GP uncertainty.
3. Student & Educator (Foundational): Focuses on microgravity flame morphology, disappearance of buoyancy, and why gentle drafts accelerate space fires.
"""
from typing import Dict, List, Any, Optional

from domain.physics import evaluate_combustion_physics
from domain.safety import evaluate_safety_officer_verdict

PERSONAS = {
    "All-in-One (Standard)": "all",
    "Flight Safety Officer (Operational)": "safety",
    "Aerospace Researcher (Academic)": "researcher",
    "Student & Educator (Foundational)": "student",
}

def calculate_combustion_physics(
    o2_pct: float,
    pressure_kpa: float,
    flow_mm_s: float,
    v_spread_mm_s: Optional[float] = None,
) -> Dict[str, Any]:
    """Compute non-dimensional combustion physics parameters (delegates to domain.physics)."""
    result = evaluate_combustion_physics(o2_pct, pressure_kpa, flow_mm_s, v_spread_mm_s)
    return result.to_dict()

def get_safety_officer_verdict(eval_result: Dict[str, Any], scenario_name: str) -> Dict[str, Any]:
    """Format an operational flight safety assessment (delegates to domain.safety)."""
    verdict = evaluate_safety_officer_verdict(eval_result, scenario_name)
    return verdict.to_dict()

def get_student_fundamentals() -> List[Dict[str, str]]:
    """Pedagogical fundamentals explaining microgravity combustion phenomena."""
    return [
        {
            "question": "Why is a space flame a soft blue sphere instead of a yellow teardrop?",
            "answer": (
                "On Earth, hot combustion gases become lighter and rise rapidly (buoyancy), drawing in cool air "
                "from below. This upward draft elongates the flame into a flickering teardrop and pushes unburned "
                "carbon particles (soot) into hot zones where they incandesce yellow. In microgravity, buoyancy "
                "vanishes: hot gases cannot rise, so oxygen must slowly diffuse inward from all directions equally, "
                "forming a quiescent blue sphere."
            ),
        },
        {
            "question": "Why does a gentle breeze make fires dramatically worse in space?",
            "answer": (
                "A stationary microgravity flame often chokes on its own exhaust products (CO2 and H2O) because "
                "there is no buoyant draft to clear them away. But when spacecraft cabin air-conditioning or an "
                "astronaut moving past creates a gentle breeze (even just 2 to 5 cm/s), it sweeps away the combustion "
                "products and continually delivers fresh oxygen, causing the flame to spread rapidly."
            ),
        },
        {
            "question": "Why can microgravity fires smolder silently and invisibly?",
            "answer": (
                "Without buoyant draft, solid materials (like wire bundles and foams) can undergo low-temperature "
                "sub-surface pyrolysis without forming a visible open flame. These smoldering reactions produce "
                "dense, slow-moving aerosols that can accumulate unnoticed inside avionics racks until air vents "
                "shift or an hatch opens, triggering explosive transition to flaming."
            ),
        },
    ]
