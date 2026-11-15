"""Per-group models on log(spread rate): linear or Gaussian Process, grouped CV, split-conformal bands."""
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor as GPR
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel as C
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
from .config import Config
from .features import log_target, exp_group_id

KINDS = ("linear", "gp")

def model_feats(chosen):
    f = list(chosen)
    if "o2_pct" in chosen and "pressure_kpa" in chosen:
        f.append("ppo2_kpa")
    return f

def _estimator(kind, d, cfg):
    if kind == "linear":
        return LinearRegression()
    k = C(1.0, (1e-2, 1e3)) * Matern([1.0] * d, (0.1, 1e3), nu=2.5) + WhiteKernel(0.05, (1e-4, 1.0))
    return GPR(k, normalize_y=True, n_restarts_optimizer=2, random_state=cfg.random_state)

class GroupModel:
    def __init__(self, feats, kind="gp", cfg=Config()):
        self.feats, self.kind, self.cfg = feats, kind, cfg

    def fit(self, df):
        X, y = df[self.feats].to_numpy(float), log_target(df["spread_rate_mm_s"])
        self.sc = StandardScaler().fit(X)
        self.est = _estimator(self.kind, len(self.feats), self.cfg).fit(self.sc.transform(X), y)
        return self

    def predict_log(self, x_row):
        Z = self.sc.transform(np.asarray(x_row, float)[None])
        if self.kind == "gp":
            mu, sd = self.est.predict(Z, return_std=True)
            return float(mu[0]), float(sd[0])
        return float(self.est.predict(Z)[0]), 0.0

def cross_validate(df, feats, kind, cfg=Config()):
    """Grouped CV by experiment. Returns (metrics, conformal quantile in log space)."""
    df = df.reset_index(drop=True)
    X, y = df[feats].to_numpy(float), log_target(df["spread_rate_mm_s"])
    groups = exp_group_id(df).to_numpy()
    n_groups = len(np.unique(groups))
    k = min(cfg.cv_max_splits, n_groups)
    if k < 2:
        return None, None
    oof, base, fold = np.full(len(y), np.nan), np.full(len(y), np.nan), np.full(len(y), -1)
    for i, (tr, te) in enumerate(GroupKFold(k).split(X, y, groups)):
        sc = StandardScaler().fit(X[tr])
        est = _estimator(kind, len(feats), cfg).fit(sc.transform(X[tr]), y[tr])
        oof[te] = est.predict(sc.transform(X[te])); base[te] = y[tr].mean(); fold[te] = i
    res = np.abs(y - oof)
    lvl = min(1.0, np.ceil((len(res) + 1) * cfg.conformal_level) / len(res))
    q = float(np.quantile(res, lvl))
    cov = np.mean([np.mean(res[fold == i] <= np.quantile(res[fold != i], cfg.conformal_level)) for i in range(k)])
    metrics = dict(kind=kind, n_rows=int(len(y)), n_experiments=int(n_groups), folds=int(k),
                   mae_log=float(res.mean()), r2_log=float(r2_score(y, oof)),
                   mae_mm_s=float(np.mean(np.abs(np.exp(y) - np.exp(oof)))),
                   baseline_mae_log=float(np.abs(y - base).mean()),
                   beats_baseline=bool(res.mean() < np.abs(y - base).mean()),
                   conformal_q90_log=q, cross_conformal_coverage=float(cov))
    return metrics, q
