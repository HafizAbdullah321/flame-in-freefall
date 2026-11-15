"""Domain Models and Data Transfer Objects for Flame in Freefall.

Pure Python dataclasses representing core entities in microgravity combustion,
flight safety assessment, and experimental diagnostics.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass(frozen=True)
class CombustionPhysicsResult:
    """Non-dimensional fluid and combustion physics scales."""
    peclet_number: float
    damkohler_number: float
    thermal_diffusivity_cm2_s: float
    flow_regime: str
    tau_flow_ms: float
    tau_chem_ms: float
    conformal_q90_margin_mm_s: float
    gp_r2_log: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "peclet_number": self.peclet_number,
            "damkohler_number": self.damkohler_number,
            "thermal_diffusivity_cm2_s": self.thermal_diffusivity_cm2_s,
            "flow_regime": self.flow_regime,
            "tau_flow_ms": self.tau_flow_ms,
            "tau_chem_ms": self.tau_chem_ms,
            "conformal_q90_margin_mm_s": self.conformal_q90_margin_mm_s,
            "gp_r2_log": self.gp_r2_log,
        }

@dataclass(frozen=True)
class SafetyOfficerVerdict:
    """Operational flight safety Go/No-Go assessment."""
    status_banner: str
    badge_color: str
    action: str
    scenario_name: str
    ppo2_kpa: float
    normoxic_delta: float
    gaps_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_banner": self.status_banner,
            "badge_color": self.badge_color,
            "action": self.action,
            "scenario_name": self.scenario_name,
            "ppo2_kpa": self.ppo2_kpa,
            "normoxic_delta": self.normoxic_delta,
            "gaps_count": self.gaps_count,
        }

@dataclass(frozen=True)
class PredictionBounds:
    """Surrogate model point estimate with conformal 90% confidence interval."""
    rate: float
    lo: float
    hi: float
    status: str
    message: str = ""

@dataclass(frozen=True)
class CatalogFilterCriteria:
    """Search and filter parameters for PSI microgravity investigations."""
    types: Optional[List[str]] = None
    gravity: Optional[List[str]] = None
    status: Optional[List[str]] = None
    text: Optional[str] = None
    verified_only: bool = False
    geometry: Optional[List[str]] = None
    fuel_cat: Optional[List[str]] = None
    sensor_cat: Optional[List[str]] = None

