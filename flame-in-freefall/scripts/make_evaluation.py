"""Generate docs/EVALUATION.md from measurements (run from the repo root: python scripts/make_evaluation.py)."""
import sys, time, hashlib, datetime as dt, re
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT))
from ffbackend.predict import Predictor
from insights.findings import load_findings, rank_findings
from insights.catalog import load_catalog, validate_catalog
from insights.scenarios import SCENARIOS, evaluate
from insights.risk_cards import build_cards
from insights.brief import build_brief
from insights import si_brief as sb
from insights.coverage_map import atmosphere_status, ppo2_gap

# Developer-labelled relevant findings per scenario (one reviewer, small set: independent review is recommended)
LABELS = {"iss": {"F12", "F13", "F14", "F06"}, "transit": {"F14", "F06", "F01", "F12", "F13"}, "lunar_alt": {"F02", "F04", "F05", "F07", "F10", "F15"},
          "lunar": {"F04", "F05", "F07", "F10", "F11", "F15"}, "mars": {"F16", "F04", "F05", "F07", "F15"}}
GOOD = """Scenario: Lunar habitat at 56.5 kPa and 34 percent oxygen, oxygen partial pressure 19.2 kPa, gravity 0.16 g.
Our data: There is no prediction for this environment. Our experiments are microgravity only.
Evidence: Material flammability limits are not expected to meet current requirements at 34% oxygen and 8.2 psi [F07]. LUCI produced the first extended lunar-gravity tests [F15].
Gaps: No measured flame spread at 0.16 g in this atmosphere is in the library."""
MUTATIONS = {"invented number": GOOD.replace("0.16 g.", "0.16 g, spread of 7.3 mm/s."), "unknown citation id": GOOD.replace("[F15]", "[F99]"), "uncited evidence": GOOD.replace(" [F07]", ""),
             "'safe' claim": GOOD.replace("Gaps: No", "Gaps: The habitat is safe. No"), "over length": GOOD + " " + "word " * 260, "missing section": GOOD.replace("Gaps:", "Notes:"),
             "prediction for uncovered scenario": GOOD.replace("There is no prediction for this environment.", "There is no prediction. The model predicts 19.2 mm/s here."),
             "text before first label": "Hello.\n" + GOOD, "malformed citation": GOOD.replace("[F07]", "[F07")}

def main():
    F = load_findings(); C = load_catalog(); P = Predictor.load(ROOT / "backend/artifacts/ff_model.joblib")
    exp = pd.read_csv(ROOT / "phase0/raw/zarm_experiments_global.csv"); exp["o2_pct"] = exp["o2_frac"] * 100
    L = ["# Evaluation report", "", f"Generated {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by `scripts/make_evaluation.py`. All numbers below were measured by that script.", ""]
    # 1 data status
    nv, nc = sum(f["verified"] == "yes" for f in F), sum(r["verified"] == "yes" for r in C)
    L += ["## 1. Evidence base and verification status", "", f"- Findings library: {len(F)} entries, **{nv} verified** against their sources, {len(F) - nv} unverified (paraphrased from source excerpts; check before quoting).",
          f"- Experiment catalog: {len(C)} entries, **{nc} verified**, {len(C) - nc} unverified; schema validation errors: {len(validate_catalog(C))}.",
          "- Every entry has an https source link. The dashboard marks unverified items.", ""]
    # 2 coverage honesty
    L += ["## 2. What our experiments cover (honesty check)", "", "| Scenario | Gravity | Pressure kPa | O2 % | O2 partial kPa | Atmosphere vs tested band | Verdict |", "|---|---|---|---|---|---|---|"]
    for k, s in SCENARIOS.items():
        e = evaluate(s, P, exp); L.append(f"| {s.name} | {s.g:g} g | {s.pressure_kpa} | {s.o2_pct} | {e['ppo2']:.1f} | {atmosphere_status(s.pressure_kpa, s.o2_pct, exp).lower()} (gap {ppo2_gap(s.pressure_kpa, s.o2_pct, exp):.1f} kPa) | {e['verdict']} |")
    L += ["", f"Predictions are produced for {sum(evaluate(s, P, exp)['prediction'] is not None for s in SCENARIOS.values())} of {len(SCENARIOS)} planned scenarios: the rest are refused with specific reasons.", ""]
    # 3 ranking
    L += ["## 3. Ranking quality (precision at 3)", "", "Labels: one reviewer (the developer), small set; treat as a sanity check, not a benchmark.", "", "| Scenario | Top 3 | Relevant in top 3 | Precision@3 |", "|---|---|---|---|"]; ps = []
    for k, s in SCENARIOS.items():
        top = [f["id"] for f in rank_findings(F, s.g, s.o2_pct, s.pressure_kpa, s.tags)[:3]]; hit = len(set(top) & LABELS[k]); ps.append(hit / 3)
        L.append(f"| {s.name} | {', '.join(top)} | {hit} | {hit / 3:.2f} |")
    L += ["", f"**Mean precision@3: {np.mean(ps):.2f}**", ""]
    # 4 brief verifier
    inputs = None
    for k in ("lunar",):
        s = SCENARIOS[k]; e = evaluate(s, P, exp); r = rank_findings(F, s.g, s.o2_pct, s.pressure_kpa, s.tags); inputs = sb.build_inputs(e, r, build_cards(e, r))
    ok_good, _ = sb.verify_brief(GOOD, inputs); rej = {n: not sb.verify_brief(t, inputs)[0] for n, t in MUTATIONS.items()}
    L += ["## 4. AI brief verifier (no model needed)", "", f"- A correct brief passes: **{ok_good}**.", f"- Corrupted briefs rejected: **{sum(rej.values())} of {len(rej)}**.", ""] + [f"  - {n}: {'rejected' if v else 'ACCEPTED'}" for n, v in rej.items()] + [""]
    # 5 citation validity of the rule-based brief
    urls = {f["source_url"] for f in F}; bad = 0; tot = 0
    for k, s in SCENARIOS.items():
        e = evaluate(s, P, exp); r = rank_findings(F, s.g, s.o2_pct, s.pressure_kpa, s.tags); t = build_brief(e, r)
        for u in re.findall(r"\]\((https://[^)]+)\)", t): tot += 1; bad += u not in urls
    L += ["## 5. Citation validity (rule-based brief)", "", f"- {tot} links across {len(SCENARIOS)} scenario briefs; links not in the findings library: **{bad}**.", ""]
    # 6 latency
    ts = []
    for _ in range(40):
        for k, s in SCENARIOS.items():
            t0 = time.perf_counter(); e = evaluate(s, P, exp); r = rank_findings(F, s.g, s.o2_pct, s.pressure_kpa, s.tags); c = build_cards(e, r); build_brief(e, r); ts.append((time.perf_counter() - t0) * 1000)
    L += ["## 6. Latency (no AI call)", "", f"- Scenario evaluation + ranking + risk cards + brief: p50 {np.percentile(ts, 50):.1f} ms, p95 {np.percentile(ts, 95):.1f} ms ({len(ts)} runs).", ""]
    L += ["## 7. Not measured here", "", "- Real AI brief quality and cost (needs your API key).", "- Findings extraction at scale (not built yet).", "- Frame rate on a real graphics card.", "- Ranking against an independent reviewer's labels.", ""]
    L += ["## Data signature", "", "`" + hashlib.sha256((ROOT / "insights/findings_seed.csv").read_bytes() + (ROOT / "insights/experiments_catalog.csv").read_bytes()).hexdigest()[:16] + "` (findings + catalog files)", ""]
    (ROOT / "docs/EVALUATION.md").write_text("\n".join(L)); print("\n".join(L))

if __name__ == "__main__":
    main()
