"""Scan a folder of downloaded data and report what can feed which part of the project.

  python inventory.py /path/to/downloads --out inventory_out

Writes INVENTORY.md and suggested_maps/*.map.json (drafts for phase0_audit.py; confirm units!).
"""
import argparse, json, re
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd

CATS = {"tabular": {".csv", ".tsv", ".xlsx", ".xls"}, "hdf5/netcdf": {".h5", ".hdf5", ".nc", ".mat"},
        "video": {".mp4", ".avi", ".mov", ".mkv", ".wmv"},
        "image": {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"},
        "document": {".pdf", ".txt", ".md", ".docx", ".html"},
        "archive": {".zip", ".tar", ".gz", ".7z", ".rar"}}
KEYS = {  # canonical field -> header regex
    "experiment_id": r"test.?id|exp\w*.?id|run.?id|^id$",
    "spread_rate_mm_s": r"spread|flame.?speed|\bv_?f\b|propagation",
    "o2_pct": r"o2|oxygen",
    "pressure_kpa": r"press|kpa|\batm\b|\bpsi\b",
    "flow_velocity_mm_s": r"flow|velocity|\bu_?\w*(cm|mm|m)_?s",
    "thickness_mm": r"thick",
    "g_level": r"gravity|\bg_?level|microg|\b0g\b",
    "fuel": r"fuel|material|sample|pmma|cellulose",
    "time": r"time|\bt_?s\b|frame",
    "position": r"position|front|\bx_?(mm|cm|m)\b|length"}
UNIT_GUESS = {"spread_rate_mm_s": [("cm/s", "spread_rate"), ("mm/s", "spread_rate"), ("m/s", "spread_rate")],
              "flow_velocity_mm_s": [("cm/s", "velocity"), ("mm/s", "velocity"), ("m/s", "velocity")],
              "pressure_kpa": [("kpa", "pressure"), ("atm", "pressure"), ("psi", "pressure"), ("pa", "pressure")],
              "thickness_mm": [("um", "length"), ("µm", "length"), ("mm", "length"), ("cm", "length")]}

def category(p):
    for c, exts in CATS.items():
        if p.suffix.lower() in exts: return c
    return "other"

def read_head(p):
    if p.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(p, nrows=200)
    return pd.read_csv(p, nrows=200, sep=None, engine="python")

def match_columns(cols):
    out = {}
    for field, rx in KEYS.items():
        for c in cols:
            if re.search(rx, str(c), re.I): out[field] = str(c); break
    return out

def guess_unit(field, col):
    low = col.lower()
    for tok, kind in UNIT_GUESS.get(field, []):
        if re.search(rf"(?<![a-z]){re.escape(tok)}(?![a-z])", low) or tok in low.replace("_", "/"):
            return tok if tok != "kpa" else "kPa", kind
    return "CONFIRM_UNIT", {"spread_rate_mm_s": "spread_rate", "flow_velocity_mm_s": "velocity",
                            "pressure_kpa": "pressure", "thickness_mm": "length"}.get(field)

def classify_table(m):
    if "spread_rate_mm_s" in m and "o2_pct" in m and ("pressure_kpa" in m or "flow_velocity_mm_s" in m):
        return "TRAIN_READY_CANDIDATE: has spread rate + O2 + pressure/flow"
    if "time" in m and "position" in m:
        return "TIME_SERIES: flame-front position vs time -> compute spread rate by slope"
    if "spread_rate_mm_s" in m: return "PARTIAL: spread rate but missing conditions (find them in the paper/metadata)"
    return "CONTEXT_ONLY: no spread-rate columns detected"

def main(root, out):
    root, out = Path(root), Path(out); (out / "suggested_maps").mkdir(parents=True, exist_ok=True)
    files = [p for p in root.rglob("*") if p.is_file()]
    by_cat, size = defaultdict(list), Counter()
    for p in files: by_cat[category(p)].append(p); size[category(p)] += p.stat().st_size
    L = ["# Data Inventory", f"Folder: `{root}` | files: {len(files)}", "",
         "| Category | Files | Size (MB) | Use in project |", "|---|---|---|---|"]
    use = {"tabular": "Phase 0 -> regression (if columns fit)", "hdf5/netcdf": "inspect keys; may hold tables or images",
           "video": "flame-front tracking -> spread rate; reference for visuals", "image": "visual realism / tracking frames",
           "document": "RAG corpus (cite the source)", "archive": "unzip first", "other": "review manually"}
    for c, fl in sorted(by_cat.items()):
        L.append(f"| {c} | {len(fl)} | {size[c]/1e6:.1f} | {use[c]} |")
    L += ["", "## Tabular files", ""]
    ready = 0
    for p in by_cat.get("tabular", []):
        try: df = read_head(p)
        except Exception as e:
            L.append(f"- `{p.relative_to(root)}`: could not read ({type(e).__name__})"); continue
        m = match_columns(df.columns); verdict = classify_table(m); ready += verdict.startswith("TRAIN")
        L.append(f"- `{p.relative_to(root)}` ({len(df.columns)} cols): **{verdict}**  matched: {m}")
        if verdict.startswith("TRAIN"):
            cols = {"experiment_id": m.get("experiment_id", "TODO_unique_id_column")}
            for f in ("o2_pct", "pressure_kpa", "flow_velocity_mm_s", "thickness_mm", "spread_rate_mm_s"):
                if f in m:
                    unit, kind = guess_unit(f, m[f])
                    cols[f] = {"col": m[f], "unit": unit, "kind": kind}
            if "o2_pct" in m: cols["o2_pct"] = {"col": m["o2_pct"], "unit": "percent", "kind": "o2"}
            const = {"source": "literature", "fuel": "TODO", "geometry": "TODO", "g_level": "TODO_0_or_1",
                     "spread_rate_definition": "TODO_steady_opposed_flat", "provenance": "TODO_DOI_or_PSI_id"}
            if "fuel" in m: const.pop("fuel"); cols["fuel"] = m["fuel"]
            name = re.sub(r"[^A-Za-z0-9_.-]", "_", str(p.relative_to(root))) + ".map.json"
            (out / "suggested_maps" / name).write_text(json.dumps({"notes": "DRAFT: confirm units, fill TODOs",
                                                                  "constants": const, "columns": cols}, indent=2))
    L += ["", f"Train-ready candidates: **{ready}**. Drafts in `suggested_maps/` (fix every TODO / CONFIRM_UNIT).", "",
          "## Other categories (first 20 each)", ""]
    for c in ("hdf5/netcdf", "video", "image", "document", "archive", "other"):
        for p in by_cat.get(c, [])[:20]: L.append(f"- [{c}] `{p.relative_to(root)}`")
    (out / "INVENTORY.md").write_text("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("root"); ap.add_argument("--out", default="inventory_out")
    a = ap.parse_args(); main(a.root, a.out)
