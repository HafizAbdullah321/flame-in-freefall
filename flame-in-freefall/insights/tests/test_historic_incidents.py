"""Tests for the Historic Incidents & NASA Lessons Learned module.
Run from repo root: python -m insights.tests.test_historic_incidents
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from insights.historic_incidents import get_historic_incidents, filter_incidents, get_incident_comparison_table

def test_historic_incidents():
    incidents = get_historic_incidents()
    assert len(incidents) == 4, f"Expected 4 historic incidents, got {len(incidents)}"
    
    # Check structure and verification
    expected_ids = {"INC-01", "INC-02", "INC-03", "INC-04"}
    assert {x["id"] for x in incidents} == expected_ids
    
    for inc in incidents:
        assert inc["title"], "Missing title"
        assert inc["date"], "Missing date"
        assert inc["mission"], "Missing mission"
        assert inc["cause"], "Missing cause"
        assert inc["consequence"], "Missing consequence"
        assert inc["engineering_lessons"], "Missing engineering lessons"
        assert inc["psi_connection"], "Missing PSI connection"
        assert inc["source_url"].startswith("https://"), "source_url must be https"
        assert inc["verified"] == "yes", "All entries must be marked verified"
    
    # Test filtering by ID
    ap1 = filter_incidents(incident_id="INC-01")
    assert len(ap1) == 1 and "Apollo 1" in ap1[0]["title"]
    
    # Test filtering by query
    mir = filter_incidents(query="Mir")
    assert len(mir) >= 1 and "Mir" in mir[0]["title"]
    
    # Test comparison table
    df = get_incident_comparison_table()
    assert len(df) == 4
    assert "Incident" in df.columns
    assert "Root Cause" in df.columns
    assert "Modern NASA Mitigation & PSI Link" in df.columns
    
    print("HISTORIC INCIDENTS TESTS PASSED")

if __name__ == "__main__":
    test_historic_incidents()

