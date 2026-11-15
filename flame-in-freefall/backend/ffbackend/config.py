"""Central configuration for the Flame in Freefall backend (Phase 1)."""
from dataclasses import dataclass

DISCLAIMER = ("Research and educational tool only. Predictions are statistical estimates from "
              "limited NASA experimental data and are not certified fire-safety guidance.")

@dataclass(frozen=True)
class Config:
    # candidate continuous inputs; each group uses those with enough coverage
    cont_feats: tuple = ("o2_pct", "pressure_kpa", "flow_velocity_mm_s", "fuel_coverage")
    min_feature_coverage: float = 0.8     # drop a feature from a group if <80% non-null
    fixed_rel_tol: float = 0.03           # query must be within 3% of a constant feature
    g_tol: float = 0.05                   # g_level match tolerance
    box_feats: tuple = ("fuel_coverage",)  # design parameters: range check only, excluded from the hull
    near_percentile: float = 50.0         # points within this typical 1-NN spacing of a real experiment count as supported
    sparse_percentile: float = 95.0       # density threshold from training data
    sparse_k: int = 3                     # neighbours used for density
    conformal_level: float = 0.90
    sparse_band_multiplier: float = 1.5   # widen interval when status == SPARSE
    cv_max_splits: int = 5
    min_experiments_to_model: int = 15    # must match Phase 0 gate
    model_feats: tuple | None = None      # None = use all varying guard features; else restrict the MODEL only
    simplicity_tolerance: float = 1.10    # pick linear unless GP beats it by more than 10% (CV MAE)
    random_state: int = 0
