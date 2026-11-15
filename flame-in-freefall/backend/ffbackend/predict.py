"""Predictor: guard -> model -> Prediction contract. Stateless and thread-safe."""
import numpy as np, pandas as pd, joblib
from .features import add_derived
from .schema import Prediction

class Predictor:
    def __init__(self, bundle):
        self.guard, self.models = bundle["guard"], bundle["models"]
        self.lines = bundle.get("lines", {})
        self.cfg, self.meta = bundle["cfg"], bundle["meta"]
        self._safe = {}                                   # memo for safe_o2_range (the scan is ~150 predictions)

    @classmethod
    def load(cls, path="artifacts/ff_model.joblib"):
        p = cls(joblib.load(path))
        p.safe_o2_range("PMMA", 0.0, 1.0)
        return p

    def predict(self, fuel, g_level, o2_pct, pressure_kpa, flow_velocity_mm_s=None, fuel_coverage=1.0):
        out = Prediction()
        try:
            x = dict(o2_pct=float(o2_pct), pressure_kpa=float(pressure_kpa),
                     flow_velocity_mm_s=None if flow_velocity_mm_s is None else float(flow_velocity_mm_s),
                     fuel_coverage=None if fuel_coverage is None else float(fuel_coverage))
            if not all(np.isfinite(v) for v in x.values() if v is not None):
                raise ValueError
        except (TypeError, ValueError):
            out.message = "Invalid numeric input."; return out.to_dict()
        status, msg = self.guard.check(fuel, g_level, x)
        if status == "OUT":
            out.message = msg; return out.to_dict()
        k, _ = self.guard.group_info(fuel, g_level)
        entry = self.models.get(k)
        if entry is None:
            out.status, out.message = "DATA_ONLY", "Too few experiments for a model; baseline data shown only."
            return out.to_dict()
        row = add_derived(pd.DataFrame([{**x, "g_level": g_level}]))
        mu, _ = entry["model"].predict_log(row[entry["feats"]].iloc[0].to_numpy(float))
        q = entry["q"] * (self.cfg.sparse_band_multiplier if status == "SPARSE" else 1.0)
        out.rate, out.lo, out.hi = float(np.exp(mu)), float(np.exp(mu - q)), float(np.exp(mu + q))
        out.status, out.message = status, msg
        return out.to_dict()

    # ---- single-oxygen-control helpers (REQ-B3) ----
    def conditions_for(self, fuel, g_level, o2_pct):
        k, _ = self.guard.group_info(fuel, g_level)
        line = self.lines.get(k)
        return None if line is None else line.conditions_for(o2_pct)

    def predict_on_line(self, fuel, g_level, o2_pct, fuel_coverage=1.0):
        c = self.conditions_for(fuel, g_level, o2_pct)
        if c is None:
            r = Prediction(message="No oxygen line for this group.").to_dict(); r["conditions"] = None; return r
        r = self.predict(fuel, g_level, o2_pct, c[0], c[1], fuel_coverage)
        r["conditions"] = dict(pressure_kpa=c[0], flow_velocity_mm_s=c[1])
        return r

    def safe_o2_range(self, fuel, g_level, fuel_coverage=1.0, step=0.1):
        key = (fuel, round(float(g_level), 3), round(float(fuel_coverage), 3), step)
        if key not in self._safe: self._safe[key] = self._safe_o2_range(fuel, g_level, fuel_coverage, step)
        return self._safe[key]

    def _safe_o2_range(self, fuel, g_level, fuel_coverage, step):
        k, _ = self.guard.group_info(fuel, g_level)
        line = self.lines.get(k)
        if line is None:
            return None
        grid = np.arange(line.lo, line.hi + 1e-9, step)
        ok = []
        for o in grid:
            c = self.conditions_for(fuel, g_level, o)
            if c is not None:
                x = dict(o2_pct=float(o), pressure_kpa=float(c[0]), flow_velocity_mm_s=float(c[1]), fuel_coverage=fuel_coverage)
                if self.guard.check(fuel, g_level, x)[0] in ("IN", "SPARSE"):
                    ok.append(o)
        return (float(min(ok)), float(max(ok))) if ok else None

    def predict_curve(self, fuel, g_level, lo, hi, fuel_coverage=1.0, step=0.25):
        """Vectorized computation of the model curve across an oxygen grid."""
        k, _ = self.guard.group_info(fuel, g_level)
        entry = self.models.get(k)
        if entry is None:
            return pd.DataFrame(columns=["o2", "rate", "lo", "hi"])
        xs = np.round(np.arange(lo, hi + 1e-9, step), 2)
        conds = [self.conditions_for(fuel, g_level, o) for o in xs]
        items = [
            {"o2_pct": float(o), "pressure_kpa": float(c[0]), "flow_velocity_mm_s": float(c[1]),
             "fuel_coverage": float(fuel_coverage), "g_level": float(g_level)}
            for o, c in zip(xs, conds) if c is not None
        ]
        if not items:
            return pd.DataFrame(columns=["o2", "rate", "lo", "hi"])
        df_derived = add_derived(pd.DataFrame(items))
        X = df_derived[entry["feats"]].to_numpy(float)
        Z = entry["model"].sc.transform(X)
        mu, _ = entry["model"].est.predict(Z, return_std=True)
        multipliers = np.array([
            (self.cfg.sparse_band_multiplier if self.guard.check(fuel, g_level, item)[0] == "SPARSE" else 1.0)
            for item in items
        ])
        qs = entry["q"] * multipliers
        return pd.DataFrame({"o2": xs, "rate": np.exp(mu), "lo": np.exp(mu - qs), "hi": np.exp(mu + qs)}).dropna()
