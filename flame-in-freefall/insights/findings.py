"""Findings library: load, rank (relevance to a scenario x strength of evidence), with transparent score components."""
import csv
from pathlib import Path

EVIDENCE_WEIGHT = {"experiment_partial_g": 1.0, "experiment_micro": 0.9, "ground_test": 0.8, "review": 0.6, "planning": 0.4}
EVIDENCE_LABEL = {"experiment_partial_g": "Experiment, partial gravity", "experiment_micro": "Experiment, microgravity", "ground_test": "Ground test",
                  "review": "Review or analysis", "planning": "Planning or context"}

def gravity_class(g):
    return "micro" if g < 0.05 else "lunar" if g < 0.25 else "mars" if g < 0.6 else "earth"

def load_findings(path=None):
    p = Path(path) if path else Path(__file__).with_name("findings_seed.csv")
    rows = []
    for r in csv.DictReader(open(p, newline="", encoding="utf-8")):
        for k in ("o2_min", "o2_max", "p_min_kpa", "p_max_kpa"): r[k] = float(r[k]) if r[k] != "" else None
        r["topics"] = [t.strip() for t in r["topics"].split(";") if t.strip()]
        r["categories"] = [t.strip() for t in (r.get("categories") or "").split(";") if t.strip()]
        r["verified"] = r.get("verified") or "no"
        r["direction"] = (r.get("direction") or "neutral").strip()
        rows.append(r)
    return rows

def _gravity_score(f_g, s_class):
    if f_g == "any": return 0.5
    if f_g == s_class: return 1.0
    if f_g == "reduced" and s_class in ("lunar", "mars", "micro"): return 0.8
    if {f_g, s_class} <= {"lunar", "mars"}: return 0.6
    if {f_g, s_class} == {"micro", "reduced"}: return 0.8
    return 0.15

def _atmos_score(f, o2, p):
    if f["o2_min"] is None and f["p_min_kpa"] is None: return 0.6          # finding states no atmosphere: a general statement, mildly applicable
    parts = []
    if f["o2_min"] is not None:
        d = max(f["o2_min"] - o2, o2 - f["o2_max"], 0.0); parts.append(max(0.0, 1 - d / 10.0))
    if f["p_min_kpa"] is not None:
        d = max(f["p_min_kpa"] - p, p - f["p_max_kpa"], 0.0); parts.append(max(0.0, 1 - d / 40.0))
    return sum(parts) / len(parts)

def _topic_score(f, tags):
    if not tags: return 0.4
    return min(1.0, len(set(f["topics"]) & set(tags)) / 2.0 + (0.0 if set(f["topics"]) & set(tags) else 0.1))

def rank_findings(findings, g, o2, p, tags=(), top=None):
    """score = 0.7 * relevance + 0.3 * evidence strength. relevance = 0.45 gravity + 0.30 atmosphere + 0.25 topic."""
    s_class, out = gravity_class(g), []
    for f in findings:
        comp = dict(gravity=_gravity_score(f["gravity"], s_class), atmosphere=_atmos_score(f, o2, p), topic=_topic_score(f, tags))
        rel = 0.45 * comp["gravity"] + 0.30 * comp["atmosphere"] + 0.25 * comp["topic"]
        ev = EVIDENCE_WEIGHT[f["evidence"]]
        out.append(dict(f, relevance=round(rel, 3), evidence_weight=ev, score=round(0.7 * rel + 0.3 * ev, 3), components={k: round(v, 2) for k, v in comp.items()}))
    out.sort(key=lambda r: (-r["score"], r["id"]))
    return out[:top] if top else out
