"""Tests for Topic Synthesis (REQ-E4).
Validates:
- Synthesis built ONLY from verified findings
- Consensus vs conflict detection
- Conflicting directions flagged on a fixture
- Acceptance rule: every statement must contain a finding ID citation [Fxx]
- Proper gap reporting when verified data is missing

Run from repo root: python -m insights.tests.test_synthesis
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from insights.findings import load_findings
from insights.synthesis import synthesize_topic, verify_synthesis, all_topic_syntheses, get_available_topics

def test_synthesis_verified():
    # 1. Topic with verified findings (flame-spread: F12, F14 in seed)
    syn = synthesize_topic("flame-spread")
    assert syn["status"] == "SYNTHESIZED"
    assert syn["verified_count"] >= 2
    assert "micro" in syn["gravity_coverage"]
    assert len(syn["top_findings"]) <= 3
    assert len(syn["statements"]) >= 1
    
    # Check acceptance: every statement has a citation
    ok, errs = verify_synthesis(syn)
    assert ok, f"verify_synthesis failed: {errs}"
    for stmt in syn["statements"]:
        assert "[" in stmt and "]" in stmt

def test_synthesis_gap():
    # 2. Topic without verified findings in seed (radiation)
    syn = synthesize_topic("radiation")
    assert syn["status"] == "GAP"
    assert syn["verified_count"] == 0
    assert syn["consensus"] == "NO_DATA"
    assert len(syn["top_findings"]) == 0
    assert any("gap" in g.lower() for g in syn["gaps"])
    ok, errs = verify_synthesis(syn)
    assert ok

def test_conflicting_directions_fixture():
    # 3. Fixture with conflicting directions (REQ-E4 requirement: conflicting directions flagged on a fixture)
    fixture = [
        dict(
            id="F91",
            finding="Under low pressure, flame spread accelerates due to enhanced gas-phase diffusion.",
            topics=["pressure-effects"],
            categories=["physics"],
            gravity="micro",
            evidence="experiment_micro",
            direction="increases_hazard",
            verified="yes",
            year=2024,
            source_url="https://ntrs.nasa.gov/1",
            source_title="Study 1",
        ),
        dict(
            id="F92",
            finding="Under low pressure, reduced chemical reaction rates cause earlier blow-off extinction.",
            topics=["pressure-effects"],
            categories=["physics"],
            gravity="micro",
            evidence="experiment_micro",
            direction="decreases_hazard",
            verified="yes",
            year=2025,
            source_url="https://ntrs.nasa.gov/2",
            source_title="Study 2",
        ),
    ]
    syn = synthesize_topic("pressure-effects", findings=fixture)
    assert syn["status"] == "SYNTHESIZED"
    assert syn["consensus"] == "CONFLICT", f"Expected CONFLICT, got {syn['consensus']}"
    assert syn["conflict_note"] is not None
    assert "F91" in syn["conflict_note"] and "F92" in syn["conflict_note"]
    assert any("Conflicting" in s or "opposing" in s.lower() for s in syn["statements"])
    
    ok, errs = verify_synthesis(syn)
    assert ok, f"Fixture failed verify_synthesis: {errs}"

def test_verifier_catches_uncited_statement():
    # 4. Verifier must reject statements missing finding IDs
    bad_syn = dict(
        status="SYNTHESIZED",
        consensus="CONSENSUS",
        statements=["Flames will spread faster at lower pressures without any citation."],
        conflict_note=None,
    )
    ok, errs = verify_synthesis(bad_syn)
    assert not ok
    assert any("lacks finding citation" in e for e in errs)

def test_all_syntheses():
    all_syn = all_topic_syntheses()
    assert len(all_syn) >= 5
    topics = get_available_topics()
    assert set(topics) == set(all_syn.keys())

def test_all():
    test_synthesis_verified()
    test_synthesis_gap()
    test_conflicting_directions_fixture()
    test_verifier_catches_uncited_statement()
    test_all_syntheses()
    print("TOPIC SYNTHESIS TESTS PASSED | Verified flame-spread synthesis & conflicting directions fixture validated")

if __name__ == "__main__":
    test_all()

