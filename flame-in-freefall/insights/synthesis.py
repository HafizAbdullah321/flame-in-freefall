"""Topic synthesis: 'What do we know about [topic]?' (REQ-E4).
Built exclusively from verified findings of that topic.
Computes evidence breakdown, gravity coverage, consensus vs conflict, top findings, and explicit data gaps.
Guarantees every statement includes finding citations [Fxx]."""
import collections, re
from pathlib import Path
from .findings import load_findings, EVIDENCE_WEIGHT, EVIDENCE_LABEL

CITE_RE = re.compile(r"\[(F\w+(?:\s*,\s*F\w+)*)\]")

TOPIC_VOCABULARY = [
    "flame-spread",
    "flammability-limit",
    "exploration-atmosphere",
    "extinction",
    "ignition",
    "materials",
    "ventilation",
    "microgravity",
    "lunar-gravity",
    "partial-gravity",
    "fire-detection",
    "soot",
    "physics",
]

def get_available_topics(findings=None):
    if findings is None:
        findings = load_findings()
    topics = set()
    for f in findings:
        for t in f.get("topics", []):
            if t: topics.add(t)
        for c in f.get("categories", []):
            if c: topics.add(c)
    return sorted(topics)

def synthesize_topic(topic, findings=None, max_top=3):
    """Synthesize evidence for a topic using ONLY verified findings.
    Returns structured dict with evidence counts, consensus/conflict, top findings, and gaps."""
    if findings is None:
        findings = load_findings()

    t_norm = topic.strip().lower()
    matching = [
        f for f in findings
        if (t_norm in [t.lower() for t in f.get("topics", [])]
            or t_norm in [c.lower() for c in f.get("categories", [])]
            or t_norm == "all")
    ]
    verified = [f for f in matching if f.get("verified") == "yes"]
    unverified = [f for f in matching if f.get("verified") != "yes"]

    if not verified:
        gaps = [f"Data gap: No verified NASA findings currently cataloged for topic '{topic}'."]
        if unverified:
            unv_ids = ", ".join(f["id"] for f in unverified)
            gaps.append(f"{len(unverified)} candidate finding(s) ({unv_ids}) exist in library but remain unverified.")
        gaps.append("Targeted microgravity experiments or calibrated numerical models are required.")
        return dict(
            topic=topic,
            status="GAP",
            headline=f"Data gap: No verified NASA findings for '{topic}'.",
            verified_count=0,
            unverified_count=len(unverified),
            evidence_counts={},
            gravity_coverage=[],
            consensus="NO_DATA",
            conflict_note=None,
            top_findings=[],
            statements=[],
            gaps=gaps,
        )

    # 1. Evidence counts & gravity coverage
    ev_counts = dict(collections.Counter(f["evidence"] for f in verified))
    grav_coverage = sorted(list({f["gravity"] for f in verified if f.get("gravity")}))

    # 2. Agreement or Conflict Analysis
    inc = [f for f in verified if f.get("direction") == "increases_hazard"]
    dec = [f for f in verified if f.get("direction") == "decreases_hazard"]
    if inc and dec:
        consensus = "CONFLICT"
        conflict_note = (
            f"[{inc[0]['id']}, {dec[0]['id']}] Conflicting physical trends observed: "
            f"[{inc[0]['id']}] indicates increased flammability or spread hazard, whereas "
            f"[{dec[0]['id']}] indicates reduced hazard or earlier blow-off extinction under distinct flow conditions."
        )
    elif inc or dec:
        consensus = "CONSENSUS"
        conflict_note = None
    else:
        consensus = "NEUTRAL"
        conflict_note = None

    # 3. Top findings (sorted by evidence weight hierarchy, then recency)
    sorted_verified = sorted(
        verified,
        key=lambda f: (-EVIDENCE_WEIGHT.get(f.get("evidence"), 0.5), -int(f.get("year") or 0), f["id"])
    )
    top_findings = sorted_verified[:max_top]

    # 4. Formulate verified statements - MUST cite finding IDs
    statements = []
    if conflict_note:
        statements.append(conflict_note)
    for f in top_findings:
        statements.append(f"[{f['id']}] {f['finding']}")
    if len(top_findings) > 1 and not conflict_note:
        top_ids = ", ".join(f["id"] for f in top_findings)
        ev_summary = ", ".join(f"{count} {EVIDENCE_LABEL.get(k, k).lower()}" for k, count in ev_counts.items())
        statements.append(
            f"[{top_ids}] Verified consensus encompasses {len(verified)} finding(s) covering {ev_summary} across {', '.join(grav_coverage)} gravity."
        )

    # 5. Gaps
    gaps = []
    has_partial = any(g in ("lunar", "mars", "reduced") for g in grav_coverage)
    if not has_partial:
        gaps.append("No verified flight data for lunar (0.16 g) or Martian (0.38 g) partial-gravity regimes.")
    has_micro = "micro" in grav_coverage
    if not has_micro:
        gaps.append("No verified microgravity flight experiments for this topic.")
    has_exp = any(k in ("experiment_micro", "experiment_partial_g") for k in ev_counts)
    if not has_exp:
        gaps.append("Evidence is derived from literature reviews or ground models; direct flight test measurements are missing.")
    if unverified:
        unv_ids = ", ".join(f["id"] for f in unverified)
        gaps.append(f"{len(unverified)} candidate finding(s) on this topic ({unv_ids}) require source verification.")

    headline = (
        f"Verified synthesis for '{topic}': {len(verified)} finding(s) with {consensus.lower()}."
        if consensus != "CONFLICT"
        else f"Conflict detected on '{topic}': {len(verified)} verified findings show opposing trends."
    )

    return dict(
        topic=topic,
        status="SYNTHESIZED",
        headline=headline,
        verified_count=len(verified),
        unverified_count=len(unverified),
        evidence_counts=ev_counts,
        gravity_coverage=grav_coverage,
        consensus=consensus,
        conflict_note=conflict_note,
        top_findings=top_findings,
        statements=statements,
        gaps=gaps,
    )

def verify_synthesis(syn):
    """Verify that a topic synthesis adheres to REQ-E4 acceptance criteria:
    - If status is SYNTHESIZED, statements must be present.
    - EVERY statement must contain at least one valid finding citation like [Fxx].
    - If status is CONFLICT, conflict_note must cite finding IDs."""
    errors = []
    if syn["status"] == "SYNTHESIZED":
        if not syn.get("statements"):
            errors.append("No synthesis statements provided for SYNTHESIZED topic.")
        for stmt in syn.get("statements", []):
            if not CITE_RE.search(stmt):
                errors.append(f"Statement lacks finding citation: '{stmt}'")
        if syn.get("consensus") == "CONFLICT":
            if not syn.get("conflict_note") or not CITE_RE.search(syn["conflict_note"]):
                errors.append("Conflict status declared but conflict_note is missing or un-cited.")
    return len(errors) == 0, errors

def all_topic_syntheses(findings=None):
    if findings is None:
        findings = load_findings()
    topics = get_available_topics(findings)
    return {t: synthesize_topic(t, findings) for t in topics}

