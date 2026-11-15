"""Pressure and flow are tied to oxygen in the experiments (one-dimensional design).
This helper follows that curve (binned means, linearly interpolated) so the dashboard
can expose a single oxygen control."""
import numpy as np

class OxygenLine:
    def __init__(self, bin_width=1.0):
        self.bin_width = bin_width

    def fit(self, df):
        e = df.groupby(["source", "experiment_id"])[["o2_pct", "pressure_kpa", "flow_velocity_mm_s"]].mean()
        o = e["o2_pct"].to_numpy(float)
        self.lo, self.hi = float(o.min()), float(o.max())
        edges = np.arange(np.floor(self.lo), np.ceil(self.hi) + self.bin_width, self.bin_width)
        idx = np.digitize(o, edges)
        cx, cp, cu = [], [], []
        for b in np.unique(idx):
            m = idx == b
            cx.append(o[m].mean()); cp.append(e["pressure_kpa"].to_numpy(float)[m].mean())
            cu.append(e["flow_velocity_mm_s"].to_numpy(float)[m].mean())
        self.x, self.p, self.u = np.array(cx), np.array(cp), np.array(cu)
        self.r2_p = float(np.corrcoef(o, e["pressure_kpa"])[0, 1] ** 2)
        return self

    def conditions_for(self, o2_pct):
        return float(np.interp(o2_pct, self.x, self.p)), float(np.interp(o2_pct, self.x, self.u))
