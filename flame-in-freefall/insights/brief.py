"""Rule-based insight brief: every sentence is traceable to a model output, a tested range, or a cited finding."""
from .findings import EVIDENCE_LABEL

def build_brief(ev, ranked, top=3):
    sc = ev["scenario"]; L = []
    L.append(f"**Scenario:** {sc.name}: {sc.pressure_kpa:.1f} kPa total pressure, {sc.o2_pct:.1f}% oxygen (oxygen partial pressure {ev['ppo2']:.1f} kPa), gravity {sc.g:g} g. {sc.basis}")
    v = ev["verdict"]
    if v == "COVERED":
        p = ev["prediction"]
        L.append(f"**What our experiments say:** this atmosphere is inside the tested range. Predicted flame spread rate over thin PMMA: {p['rate']:.2f} mm/s (90% interval {p['lo']:.2f} to {p['hi']:.2f}).")
    else:
        why = " ".join(ev["reasons"]) or "The envelope guard refused this combination."
        L.append(("**What our experiments say:** this atmosphere is just outside the tested range, so no prediction is made. " if v == "NEAR" else
                  "**What our experiments say:** this scenario is outside what our 22 microgravity experiments cover, so we make no prediction. ") + why)
        c = ev["comparator"]
        if c: L.append(f"For orientation only: at {c['o2_pct']:.1f}% oxygen the nearest tested atmosphere ({c['pressure_kpa']:.0f} kPa, microgravity) spread at about {c['rate']:.1f} mm/s ({c['lo']:.1f} to {c['hi']:.1f}). This is not a prediction for the scenario.")
    L.append("**What NASA's documents say (ranked by relevance and strength of evidence):**")
    for i, f in enumerate(ranked[:top], 1):
        L.append(f"{i}. {f['finding']} [{EVIDENCE_LABEL[f['evidence']]}; {f['source_title']}]({f['source_url']})")
    gaps = []
    if ev["scenario"].g > 0.05: gaps.append(f"flame spread and flammability-limit measurements at {sc.g:g} g in this atmosphere")
    if v != "COVERED": gaps.append(f"microgravity spread data at {sc.pressure_kpa:.0f} kPa with {sc.o2_pct:.0f}% oxygen")
    if gaps: L.append("**Data gaps that limit confidence:** " + "; ".join(gaps) + ".")
    L.append("*Research and educational summary. Not certified fire-safety guidance.*")
    return "\n\n".join(L)
