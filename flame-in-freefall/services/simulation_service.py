"""Simulation & Prediction Application Service.

Encapsulates machine learning surrogate prediction, uncertainty evaluation,
and non-dimensional combustion physics calculations.
"""
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from ffbackend.predict import Predictor
from domain.physics import evaluate_combustion_physics
from domain.models import CombustionPhysicsResult

class SimulationService:
    """Service orchestrating flame spread prediction and physical diagnostics."""

    def __init__(self, model_path: Path):
        self.model_path = model_path
        self._predictor: Optional[Predictor] = None

    @property
    def predictor(self) -> Predictor:
        if self._predictor is None:
            self._predictor = Predictor.load(self.model_path)
        return self._predictor

    def get_safe_o2_range(self, fuel: str = "PMMA", g: float = 0.0, f_star: float = 1.0) -> Tuple[float, float]:
        """Return experimental oxygen envelope limits."""
        return self.predictor.safe_o2_range(fuel, g, f_star)

    def get_chamber_conditions(self, fuel: str, g: float, o2_pct: float) -> Tuple[float, float]:
        """Return (pressure_kpa, opposed_flow_mm_s) associated with oxygen level."""
        return self.predictor.conditions_for(fuel, g, o2_pct)

    def predict_spread_rate(
        self,
        o2_pct: float,
        f_star: float = 1.0,
        fuel: str = "PMMA",
        g: float = 0.0,
    ) -> Dict[str, Any]:
        """Evaluate GP surrogate model with conformal 90% confidence intervals."""
        return self.predictor.predict_on_line(fuel, g, o2_pct, f_star)

    def compute_physics_diagnostics(
        self,
        o2_pct: float,
        pressure_kpa: float,
        flow_mm_s: float,
        rate_mm_s: Optional[float] = None,
    ) -> CombustionPhysicsResult:
        """Compute non-dimensional transport scales and flame regime."""
        return evaluate_combustion_physics(o2_pct, pressure_kpa, flow_mm_s, rate_mm_s)

    def compute_spread_curve(
        self,
        f_star: float,
        lo_o2: float,
        hi_o2: float,
        fuel: str = "PMMA",
        g: float = 0.0,
    ) -> pd.DataFrame:
        """Evaluate continuous prediction curve across oxygen range."""
        xs = np.round(np.arange(lo_o2, hi_o2 + 1e-9, 0.25), 2)
        rows = [
            (
                o,
                *(lambda r: (r["rate"], r["lo"], r["hi"]))(
                    self.predictor.predict_on_line(fuel, g, o, f_star)
                ),
            )
            for o in xs
        ]
        return pd.DataFrame(rows, columns=["o2", "rate", "lo", "hi"]).dropna()

