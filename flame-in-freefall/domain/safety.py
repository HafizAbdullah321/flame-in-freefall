"""Flight Safety Domain Module.

Operational Go/No-Go rules, flight envelope boundary enforcement, and normoxic
partial pressure margin calculations. Zero dependencies on UI.
"""
from typing import Dict, Any
from domain.models import SafetyOfficerVerdict

NORMOXIC_PPO2_KPA = 21.3

def evaluate_safety_officer_verdict(eval_result: Dict[str, Any], scenario_name: str) -> SafetyOfficerVerdict:
    """Evaluate operational flight safety posture for a mission scenario."""
    verdict = eval_result.get("verdict", "UNKNOWN")
    ppo2 = eval_result.get("ppo2", 0.0)

    if verdict == "COVERED":
        status_banner = "FLIGHT ENVELOPE STATUS: [● GO / VERIFIED]"
        badge_color = "green"
        action = "Operationally validated within drop-tower test matrix. Conformal spread rate bounds apply."
    elif verdict == "NEAR":
        status_banner = "FLIGHT ENVELOPE STATUS: [▲ CAUTION / ADVISORY]"
        badge_color = "orange"
        action = "Atmosphere borders experimental hull. Conservative margin required; flight extrapolation prohibited."
    else:
        status_banner = "FLIGHT ENVELOPE STATUS: [■ NO-GO / UNVERIFIED]"
        badge_color = "red"
        action = "Zero flight prediction permitted. Physical model cannot extrapolate to exploration partial-g or reduced pressures."

    normoxic_delta = round(ppo2 - NORMOXIC_PPO2_KPA, 1)
    gaps_count = len(eval_result.get("reasons", []))

    return SafetyOfficerVerdict(
        status_banner=status_banner,
        badge_color=badge_color,
        action=action,
        scenario_name=scenario_name,
        ppo2_kpa=ppo2,
        normoxic_delta=normoxic_delta,
        gaps_count=gaps_count,
    )

