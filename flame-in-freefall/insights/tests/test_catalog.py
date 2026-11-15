"""Tests for the experiment catalog. Run from the repo root: python -m insights.tests.test_catalog"""
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from insights.catalog import load_catalog, validate_catalog, filter_catalog, compare, evidence_matrix, gravity_class, FIELDS

def test_all():
    C = load_catalog(); assert validate_catalog(C) == [], validate_catalog(C)
    assert len(C) >= 11 and len({r["id"] for r in C}) == len(C) and all(r["source_url"].startswith("https://") for r in C)
    ver = [r["id"] for r in C if r["verified"] == "yes"]; assert len(ver) == len(C), ver          # all entries are verified against NASA sources
    # filters
    micro = {r["id"] for r in filter_catalog(C, gravity=["micro"])}; assert {"E01", "E02", "E03", "E04", "E06", "E07", "E12", "E13", "E14"} <= micro and "E08" not in micro and "E10" not in micro
    assert {r["id"] for r in filter_catalog(C, gravity=["earth"])} == {"E08", "E09"}
    assert {r["id"] for r in filter_catalog(C, status=["planned"])} == {"E10", "E11", "E15"}
    assert {r["id"] for r in filter_catalog(C, types=["Drop tower"])} == {"E07"}
    # fuel and sensor filters
    droplets = {r["id"] for r in filter_catalog(C, geometry=["Liquid droplet"])}; assert droplets == {"E12"}, droplets
    aerosol = {r["id"] for r in filter_catalog(C, geometry=["Particulate aerosol"])}; assert aerosol == {"E13"}, aerosol
    burners = {r["id"] for r in filter_catalog(C, fuel_cat=["Gaseous fuels & burners"])}; assert {"E06", "E14"} <= burners, burners
    temp_sensors = {r["id"] for r in filter_catalog(C, sensor_cat=["Temperature & heat flux"])}; assert {"E06", "E07"} <= temp_sensors, temp_sensors
    near_expl = {r["id"] for r in filter_catalog(C, o2=(33, 35), pressure=(55, 58))}; assert near_expl == {"E09", "E10"}, near_expl           # exploration atmosphere: ground and planned only
    assert "E07" not in near_expl, "microgravity data does not reach the exploration atmosphere"
    assert [r["id"] for r in filter_catalog(C, text="lunar")][:1] and len(filter_catalog(C, verified_only=True)) == len(C)
    assert gravity_class(C[4]) == "unknown" and gravity_class(C[9]) == "lunar"
    # comparison table: same fields for every entry, blanks shown explicitly
    t = compare(C, ["E02", "E07", "E05"]); assert list(t.index) == [n for n, _ in FIELDS] and t.shape == (len(FIELDS), 3)
    assert t.loc["Oxygen (%)"].tolist() == ["16 to 21", "21.6 to 36", "not reported"], t.loc["Oxygen (%)"].tolist()
    assert t.loc["Verified against source"].iloc[2].startswith("Yes") and "not reported" in t.loc["Gravity (g)"].iloc[2]
    assert compare(C, []).empty
    # evidence matrix shows the gap: no partial-gravity experiments flown yet in this catalog
    m = evidence_matrix(C); assert "lunar" in m.index and m.loc["lunar", "planned"] >= 1 and m.get("flown", pd.Series(dtype=int)).get("lunar", 0) == 0
    # validator catches bad data
    bad = [dict(C[0], source_url="http://x"), dict(C[1], type="Moon"), dict(C[2], o2_min=30.0, o2_max=20.0), dict(C[3], id="E01"), dict(C[4], key_result="")]
    errs = " | ".join(validate_catalog(bad)); assert all(s in errs for s in ("https", "bad type", "greater than", "duplicate", "key_result"))
    print(f"CATALOG TESTS PASSED | {len(C)} entries, {len(ver)} verified | exploration-atmosphere evidence: {sorted(near_expl)} (no microgravity data)")

if __name__ == "__main__":
    test_all()
