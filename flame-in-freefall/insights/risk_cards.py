"""Risk cards (REQ-E8): per-scenario safety insight by topic, strictly evidence-based. No numbers are created here:
the spread card only repeats model output (when the scenario is covered); every other card lists cited findings and states the evidence level."""
from .findings import _gravity_score, _atmos_score, gravity_class

CARDS = [("spread", "Flame spread tendency"), ("limit", "Flammability limits"), ("ignition", "Ignition"), ("detection", "Fire detection"),
         ("suppression", "Fire suppression"), ("materials", "Materials and hardware"), ("ventilation", "Ventilation and flow")]
DIRECT = {"experiment_partial_g", "experiment_micro", "ground_test"}
STATES = {"PREDICTED": "Model prediction", "NO_PREDICTION": "No prediction", "MEASURED": "Measured evidence", "INDIRECT": "Indirect evidence only", "NONE": "No evidence found"}

def build_cards(ev, ranked, findings_all=None, top=2):
    """ev: output of scenarios.evaluate; ranked: output of findings.rank_findings (each item has components and score)."""
    sc = ev["scenario"]; s_class = gravity_class(sc.g); out = []
    for key, label in CARDS:
        mine = [f for f in ranked if key in f.get("categories", [])]
        card = dict(key=key, label=label, findings=mine[:top], note="", numbers=None)
        if key == "spread" and ev["verdict"] == "COVERED":
            p = ev["prediction"]; card.update(state="PREDICTED", numbers=dict(rate=p["rate"], lo=p["lo"], hi=p["hi"]),
                                              note="From our microgravity experiments; thin PMMA only.")
        else:
            direct = [f for f in mine if f["evidence"] in DIRECT and _gravity_score(f["gravity"], s_class) >= 0.8 and _atmos_score(f, sc.o2_pct, sc.pressure_kpa) >= 0.5]
            if key == "spread":
                card["state"] = "NO_PREDICTION"
                card["note"] = "This environment is " + ("just outside" if ev["verdict"] == "NEAR" else "outside") + " what our experiments cover; see the findings below for context." if mine else \
                               "This environment is outside what our experiments cover, and no related findings are in the library."
            elif direct:
                best = direct[0]; card["state"] = "MEASURED"; card["findings"] = direct[:top]
                if best["o2_min"] is None: card["note"] = "The finding does not state the atmosphere; check the source before applying it to this scenario."
            elif mine and any(f["relevance"] >= 0.4 for f in mine):
                card["state"] = "INDIRECT"; card["note"] = "Only reviews, plans, or tests in a different gravity or atmosphere; no direct measurement for this scenario."
            else:
                card["state"] = "NONE"; card["findings"] = []; card["note"] = "No finding in the library covers this topic for this scenario. This is a data gap, not a sign of low risk."
        card["n_unverified"] = sum(1 for f in card["findings"] if f.get("verified") != "yes")
        out.append(card)
    return out
