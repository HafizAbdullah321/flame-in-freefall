"""Tests for the Terrestrial Spin-offs & Earth Safety module.
Run from repo root: python -m insights.tests.test_terrestrial
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from insights.terrestrial import get_terrestrial_spinoffs, filter_spinoffs, get_spinoff_comparison_dataframe

def test_terrestrial_spinoffs():
    spinoffs = get_terrestrial_spinoffs()
    assert len(spinoffs) >= 4, f"Expected at least 4 spin-offs, got {len(spinoffs)}"
    
    # Check all required fields are populated and verified
    for s in spinoffs:
        assert s["id"].startswith("SPIN-"), f"Invalid id: {s['id']}"
        assert s["title"], "Missing title"
        assert s["category"] in ["Suppression", "Life Support & Crew Safety", "Materials & Protection", "Early Detection"]
        assert s["space_origin"], "Missing space origin"
        assert s["terrestrial_app"], "Missing terrestrial app"
        assert s["psi_connection"], "Missing PSI connection"
        assert len(s["benefits"]) >= 3, "Expected at least 3 benefits"
        assert s["source_url"].startswith("https://"), "source_url must be https"
        assert s["verified"] == "yes", "All terrestrial entries must be verified"
    
    # Check filtering
    supp = filter_spinoffs(category="Suppression")
    assert any(s["id"] == "SPIN-01" for s in supp)
    assert not any(s["id"] == "SPIN-02" for s in supp)
    
    # Search query
    gear = filter_spinoffs(query="turnout")
    assert any("PBI" in s["title"] for s in gear)
    
    # Comparison table
    df = get_spinoff_comparison_dataframe()
    assert len(df) == len(spinoffs)
    assert "Technology Spin-off" in df.columns
    assert "Terrestrial Commercial Application" in df.columns
    
    print(f"TERRESTRIAL SPIN-OFF TESTS PASSED | {len(spinoffs)} verified applications")

if __name__ == "__main__":
    test_terrestrial_spinoffs()

