"""Envelope guard: convex hull + density check, per (fuel, g_level) group.

Statuses: IN, SPARSE, OUT, DATA_ONLY (DATA_ONLY is assigned by the Predictor).
Features that are constant within a group (e.g. ISS cabin pressure) are treated as
FIXED: a query must match them within a tolerance, otherwise OUT. Only varying
features enter the hull.
"""
import numpy as np, pandas as pd
from scipy.spatial import Delaunay, QhullError
from .config import Config

class EnvelopeGuard:
    def __init__(self, cfg: Config = Config()):
        self.cfg, self.g = cfg, {}

    def fit(self, df: pd.DataFrame):
        c = self.cfg
        for (fuel, gl), d in df.groupby(["fuel", "g_level"]):
            feats = [f for f in c.cont_feats
                     if f in d and d[f].notna().mean() >= c.min_feature_coverage]
            d = d.dropna(subset=feats)
            if d.empty or not feats:
                continue
            varying, fixed = [], {}
            for f in feats:
                v = d[f].to_numpy(float)
                if d[f].nunique() >= 3 and np.ptp(v) > 0:
                    varying.append(f)
                else:
                    fixed[f] = float(np.median(v))
            entry = dict(feats=feats, varying=varying, fixed=fixed,
                         n_exp=int((d["source"].astype(str) + d["experiment_id"].astype(str)).nunique()),
                         hull=None, Z=None, mu=None, sd=None, lo=None, hi=None, tau=np.inf)
            if varying:
                X = d[varying].to_numpy(float)
                mu, sd = X.mean(0), X.std(0) + 1e-12
                Z = (X - mu) / sd
                hidx = [i for i, f in enumerate(varying) if f not in c.box_feats]
                entry.update(mu=mu, sd=sd, Z=Z, lo=Z.min(0), hi=Z.max(0), hidx=hidx)
                Zh = Z[:, hidx] if hidx else None
                if Zh is not None and len(hidx) >= 2:
                    Uh = np.unique(Zh, axis=0)
                    if len(Uh) > len(hidx):
                        try:
                            entry["hull"] = Delaunay(Zh)
                        except QhullError:
                            pass
                if Zh is not None:
                    Uh = np.unique(Zh, axis=0)
                    if len(Uh) > 1:
                        Dh = np.linalg.norm(Uh[:, None] - Uh[None], axis=2); np.fill_diagonal(Dh, np.inf)
                        entry["tau_near"] = float(np.percentile(Dh.min(1), c.near_percentile))
                        entry["Zh"] = Uh
                U = np.unique(Z, axis=0)
                if len(U) > c.sparse_k:
                    D = np.linalg.norm(U[:, None] - U[None], axis=2)
                    np.fill_diagonal(D, np.inf)
                    knn = np.sort(D, 1)[:, :c.sparse_k].mean(1)
                    entry["tau"] = float(np.percentile(knn, c.sparse_percentile))
            self.g[(fuel, float(gl))] = entry
        return self

    def _key(self, fuel, g):
        best = None
        for (f, gl) in self.g:
            if f == fuel and abs(gl - g) <= self.cfg.g_tol:
                if best is None or abs(gl - g) < abs(best[1] - g):
                    best = (f, gl)
        return best

    def groups(self):
        return list(self.g.keys())

    def group_info(self, fuel, g):
        k = self._key(fuel, g)
        return (k, self.g[k]) if k else (None, None)

    def check(self, fuel, g_level, x: dict):
        k, m = self.group_info(fuel, g_level)
        if m is None:
            return "OUT", f"No experiments for fuel='{fuel}' at g={g_level}."
        for f in m["feats"]:
            if f not in x or x[f] is None:
                return "OUT", f"Missing required input '{f}'."
        for f, val in m["fixed"].items():
            tol = self.cfg.fixed_rel_tol * max(abs(val), 1e-9)
            if abs(x[f] - val) > tol:
                return "OUT", f"'{f}' was only tested near {val:.4g}; requested {x[f]:.4g}."
        if not m["varying"]:
            return "IN", ""
        z = (np.array([x[f] for f in m["varying"]], float) - m["mu"]) / m["sd"]
        eps = 1e-9
        box_ok = bool(np.all((z >= m["lo"] - eps) & (z <= m["hi"] + eps)))
        if m["hull"] is not None:
            boxf = bool(np.all([(m["lo"][i] - eps <= z[i] <= m["hi"][i] + eps) for i, f in enumerate(m["varying"])
                                if f in self.cfg.box_feats]))
            zh = z[m["hidx"]]
            in_hull = bool(m["hull"].find_simplex(zh) >= 0)
            near = (m.get("Zh") is not None and np.linalg.norm(m["Zh"] - zh, axis=1).min() <= m.get("tau_near", 0.0))
            inside = boxf and (in_hull or near)
        else:
            inside = box_ok
        if not inside:
            return "OUT", "Experimental Bounds Exceeded: outside the tested envelope."
        d = np.sort(np.linalg.norm(m["Z"] - z, axis=1))[:self.cfg.sparse_k].mean()
        if d > m["tau"]:
            return "SPARSE", "Inside the envelope but far from any experiment."
        return "IN", ""
