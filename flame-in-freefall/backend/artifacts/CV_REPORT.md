# CV Report (grouped by experiment)

## PMMA|g=0
- status: MODEL_OK
- chosen: gp
- features: ["o2_pct", "fuel_coverage"]
- guard_features: ["o2_pct", "pressure_kpa", "flow_velocity_mm_s", "fuel_coverage"]
- candidates: {"linear": {"mae_log": 0.061341608668844, "r2_log": 0.9113663995686997, "mae_mm_s": 0.23093374512342973}, "gp": {"mae_log": 0.05519046455127021, "r2_log": 0.9336574618461688, "mae_mm_s": 0.2207358511386777}}
- n_experiments: 22
- folds: 5
- mae_log: 0.0552
- r2_log: 0.9337
- mae_mm_s: 0.2207
- baseline_mae_log: 0.2321
- beats_baseline: True
- conformal_q90_log: 0.1297
- cross_conformal_coverage: 0.9