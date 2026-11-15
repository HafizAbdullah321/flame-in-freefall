"""Train: harmonized table + gate -> guard, per-group model (simplest adequate), oxygen line, CV report."""
import argparse, json, datetime as dt
from pathlib import Path
import joblib, pandas as pd
from .config import Config
from .features import add_derived
from .guard import EnvelopeGuard
from .model import GroupModel, cross_validate, model_feats, KINDS
from .oxygen_line import OxygenLine

def load_table(p: Path):
    for name in ("harmonized.parquet", "harmonized.csv"):
        if (p / name).exists():
            f = p / name
            return pd.read_parquet(f) if name.endswith("parquet") else pd.read_csv(f)
    raise FileNotFoundError(f"No harmonized table in {p}. Run Phase 0 first.")

def train(table: pd.DataFrame, cfg=Config(), out_dir="artifacts"):
    df = table[table["comparable"].astype(bool)].copy()
    df["g_level"] = df["g_level"].astype(float)
    df = add_derived(df)
    guard = EnvelopeGuard(cfg).fit(df)
    models, lines, report = {}, {}, {}
    for (fuel, gl), d in df.groupby(["fuel", "g_level"]):
        key = f"{fuel}|g={gl:g}"
        n_exp = d.assign(k=d["source"].astype(str) + d["experiment_id"].astype(str))["k"].nunique()
        if n_exp < cfg.min_experiments_to_model or (fuel, gl) not in guard.g:
            report[key] = dict(status="DATA_ONLY", n_experiments=int(n_exp)); continue
        varying = guard.g[(fuel, gl)]["varying"]
        chosen = [f for f in cfg.model_feats if f in varying] if cfg.model_feats else list(varying)
        feats = model_feats(chosen)
        if not feats:
            report[key] = dict(status="DATA_ONLY", n_experiments=int(n_exp), note="no varying inputs"); continue
        dd = d.dropna(subset=feats + ["spread_rate_mm_s"])
        results = {k: cross_validate(dd, feats, k, cfg) for k in KINDS}
        if any(m is None for m, _ in results.values()):
            report[key] = dict(status="DATA_ONLY", n_experiments=int(n_exp)); continue
        best = min(m["mae_log"] for m, _ in results.values())
        kind = "linear" if results["linear"][0]["mae_log"] <= cfg.simplicity_tolerance * best else "gp"
        metrics, q = results[kind]
        models[(fuel, gl)] = dict(model=GroupModel(feats, kind, cfg).fit(dd), q=q, feats=feats)
        if {"o2_pct", "pressure_kpa", "flow_velocity_mm_s"} <= set(varying):
            lines[(fuel, gl)] = OxygenLine().fit(d)
        report[key] = dict(status="MODEL_OK", chosen=kind, features=feats, guard_features=list(varying),
                           candidates={k: {a: m[a] for a in ("mae_log", "r2_log", "mae_mm_s")} for k, (m, _) in results.items()},
                           **{a: metrics[a] for a in ("n_experiments", "folds", "mae_log", "r2_log", "mae_mm_s",
                                                      "baseline_mae_log", "beats_baseline", "conformal_q90_log",
                                                      "cross_conformal_coverage")})
    meta = dict(version="0.2.0", trained_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                n_rows=int(len(df)), report=report)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    joblib.dump(dict(guard=guard, models=models, lines=lines, cfg=cfg, meta=meta), out / "ff_model.joblib")
    (out / "cv_report.json").write_text(json.dumps(report, indent=2))
    L = ["# CV Report (grouped by experiment)", ""]
    for k, v in report.items():
        L.append(f"## {k}")
        for a, b in v.items():
            L.append(f"- {a}: {json.dumps(b) if isinstance(b, (dict, list)) else (round(b, 4) if isinstance(b, float) else b)}")
    (out / "CV_REPORT.md").write_text("\n".join(L))
    return meta

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase0-out", default="../phase0/out"); ap.add_argument("--artifacts", default="artifacts")
    ap.add_argument("--model-feats", nargs="*", default=None)
    a = ap.parse_args()
    cfg = Config(model_feats=tuple(a.model_feats)) if a.model_feats else Config()
    print(json.dumps(train(load_table(Path(a.phase0_out)), cfg, a.artifacts)["report"], indent=2))
