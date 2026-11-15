"""Phase 0: Data Audit for Flame in Freefall.

Usage:
  python phase0_audit.py --raw raw/ --out out/ [--min-exp 15]

Each file in raw/ is a CSV you extracted from PSI / a paper, plus a sidecar
<name>.map.json that maps its columns/units to the canonical schema (see
sources_template.map.json). Nothing here fabricates data: rows missing required
fields are rejected and counted in the audit report.
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

CANON = ["experiment_id", "source", "fuel", "geometry", "thickness_mm", "o2_pct",
         "pressure_kpa", "g_level", "flow_velocity_mm_s", "ignition_type",
         "spread_rate_mm_s", "spread_rate_definition", "n_replicates", "fuel_coverage",
         "provenance", "provenance_file"]
REQUIRED = ["experiment_id", "source", "fuel", "o2_pct", "pressure_kpa", "g_level",
            "spread_rate_mm_s", "spread_rate_definition"]
SOURCES = {"BASS", "BASS-II", "ACME", "SoFIE", "Saffire", "LUCI", "literature"}
# spread_rate_definition values accepted for the regression target
COMPARABLE = {"steady_opposed_flat", "steady_concurrent_flat", "steady_opposed_cylinder", "global_opposed_flat"}

# unit factors -> canonical (mm/s, kPa, mm, percent)
UNITS = {
    "spread_rate": {"mm/s": 1.0, "cm/s": 10.0, "m/s": 1000.0},
    "pressure": {"kPa": 1.0, "Pa": 1e-3, "atm": 101.325, "psi": 6.894757, "bar": 100.0},
    "length": {"mm": 1.0, "um": 1e-3, "cm": 10.0, "m": 1000.0},
    "velocity": {"mm/s": 1.0, "cm/s": 10.0, "m/s": 1000.0},
    "o2": {"percent": 1.0, "fraction": 100.0},
}

def load_one(csv: Path):
    mp = json.loads(csv.with_suffix(".map.json").read_text())
    df = pd.read_csv(csv)
    out = pd.DataFrame(index=df.index)
    for canon, spec in mp["columns"].items():
        if isinstance(spec, str):
            out[canon] = df[spec] if spec in df.columns else np.nan
        else:  # {"col": "...", "unit": "cm/s", "kind": "velocity"}
            col = df[spec["col"]].astype(float)
            out[canon] = col * UNITS[spec["kind"]][spec["unit"]]
    for k, v in mp.get("constants", {}).items():
        out[k] = v
    for c in CANON:
        if c not in out: out[c] = np.nan
    out["provenance_file"] = csv.name
    return out[CANON], mp.get("notes", "")

def validate(df):
    """Return (clean, rejected_with_reason)."""
    reasons = pd.Series("", index=df.index)
    for c in REQUIRED:
        reasons[df[c].isna()] += f"missing:{c};"
    reasons[~df["source"].isin(SOURCES) & df["source"].notna()] += "bad_source;"
    for c, lo, hi in [("o2_pct", 0, 100), ("pressure_kpa", 0.1, 1000),
                      ("spread_rate_mm_s", 0, 1e3), ("g_level", 0, 20)]:
        bad = df[c].notna() & ~df[c].between(lo, hi)
        reasons[bad] += f"range:{c};"
    return df[reasons == ""].copy(), df.assign(reject_reason=reasons)[reasons != ""]

def audit(raw: Path, out: Path, min_exp: int, extra=()):
    frames, notes = [], {}
    for csv in sorted(raw.glob("*.csv")):
        if not csv.with_suffix(".map.json").exists():
            print(f"SKIP {csv.name}: no .map.json sidecar", file=sys.stderr); continue
        d, n = load_one(csv); frames.append(d); notes[csv.name] = n
    if not frames:
        sys.exit("No usable inputs in raw/. Add CSV + .map.json files first.")
    allrows = pd.concat(frames, ignore_index=True)
    clean, rejected = validate(allrows)
    clean["comparable"] = clean["spread_rate_definition"].isin(COMPARABLE | set(extra))
    clean["g_level"] = clean["g_level"].astype(float)

    # duplicates by experiment_id within source
    dups = clean.duplicated(["source", "experiment_id"], keep=False).sum()

    # gate: per (fuel, g_level) distinct comparable experiments
    tgt = clean[clean.comparable]
    gate = (tgt.groupby(["fuel", "g_level"])["experiment_id"].nunique()
              .rename("n_experiments").reset_index())
    gate["status"] = np.where(gate.n_experiments >= min_exp, "MODEL_OK", "DATA_ONLY")

    # per-source report
    cont = ["o2_pct", "pressure_kpa", "flow_velocity_mm_s", "thickness_mm"]
    lines = ["# Phase 0 Audit Report", "",
             f"Rows read: {len(allrows)} | accepted: {len(clean)} | rejected: {len(rejected)} | duplicate keys: {dups}", ""]
    for src, g in clean.groupby("source"):
        lines += [f"## {src}", f"- experiments: {g.experiment_id.nunique()}, rows: {len(g)}",
                  f"- comparable-target rows: {int(g.comparable.sum())}",
                  f"- fuels: {sorted(g.fuel.dropna().unique())}",
                  f"- spread definitions: {g.spread_rate_definition.value_counts().to_dict()}",
                  f"- g_levels: {[float(x) for x in sorted(g.g_level.unique())]}"]
        for c in cont:
            s = g[c].dropna()
            lines.append(f"- {c}: " + (f"n={len(s)}, min={s.min():.3g}, max={s.max():.3g}" if len(s) else "NO DATA"))
        miss = (g[REQUIRED + cont].isna().mean() * 100).round(1)
        lines.append(f"- missing % (required+continuous): {miss[miss > 0].to_dict()}")
        lines.append("")
    lines += ["## Gate: (fuel, g_level) groups", f"Threshold: >= {min_exp} distinct comparable experiments", "",
              gate.to_markdown(index=False) if len(gate) else "_no comparable rows_", ""]
    go = bool((gate.status == "MODEL_OK").any())
    lines.append(f"## GO / NO-GO: {'GO (at least one modelable group)' if go else 'NO-GO: no group meets the gate. Ship data-only mode or acquire more data.'}")
    if (tgt.groupby("g_level")["experiment_id"].nunique() < min_exp).any():
        lines.append("- WARNING: at least one gravity level has too few comparable experiments overall.")
    if tgt["g_level"].nunique() < 2:
        lines.append("- WARNING: only one gravity level present among comparable rows; the 0g-vs-1g comparison cannot be modeled.")
    out.mkdir(parents=True, exist_ok=True)
    clean.to_parquet(out / "harmonized.parquet") if _has_pa() else clean.to_csv(out / "harmonized.csv", index=False)
    rejected.to_csv(out / "rejected_rows.csv", index=False)
    gate.to_csv(out / "gate.csv", index=False)
    (out / "AUDIT_REPORT.md").write_text("\n".join(lines))
    print("\n".join(lines))

def _has_pa():
    try: import pyarrow; return True
    except ImportError: return False

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default="raw"); ap.add_argument("--out", default="out")
    ap.add_argument("--min-exp", type=int, default=15); ap.add_argument("--comparable-extra", nargs="*", default=[])
    a = ap.parse_args(); audit(Path(a.raw), Path(a.out), a.min_exp, a.comparable_extra)
