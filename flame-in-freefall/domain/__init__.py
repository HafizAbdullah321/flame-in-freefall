"""Domain layer package for Flame in Freefall."""
from domain.models import CombustionPhysicsResult, SafetyOfficerVerdict, PredictionBounds, CatalogFilterCriteria
from domain.physics import evaluate_combustion_physics, calculate_thermal_diffusivity
from domain.safety import evaluate_safety_officer_verdict

__all__ = [
    "CombustionPhysicsResult",
    "SafetyOfficerVerdict",
    "PredictionBounds",
    "CatalogFilterCriteria",
    "evaluate_combustion_physics",
    "calculate_thermal_diffusivity",
    "evaluate_safety_officer_verdict",
]

