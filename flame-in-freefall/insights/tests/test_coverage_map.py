"""Tests for the evidence coverage map on the REAL experiments table. Run from the repo root: python -m insights.tests.test_coverage_map"""
import sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
from scipy.spatial import Delaunay
from insights.scenarios import SCENARIOS
from insights.catalog import load_catalog
from insights.coverage_map import (hull_polygon, ppo2_range, ppo2_gap, atmosphere_status, planned_points, coverage_table, coverage_figure, STATUS_TEXT)

def test_all():
    exp = pd.read_csv(ROOT / "phase0/raw/zarm_experiments_global.csv"); exp["o2_pct"] = exp["o2_frac"] * 100
    poly = hull_polygon(exp); assert np.allclose(poly[0], poly[-1])
    tri = Delaunay(poly[:-1])
    pts = np.c_[exp["p_kpa"], exp["o2_pct"]]; assert all(tri.find_simplex(p, tol=1e-6) >= 0 for p in pts), "every experiment must lie inside the hull"
    lo, hi = ppo2_range(exp); assert 21.0 < lo < 22.0 and 24.5 < hi < 26.0
    # planned environments: statuses and gaps (the heart of the insight)
    assert atmosphere_status(56.5, 34.0, exp) == "OUTSIDE" and 1.5 < ppo2_gap(56.5, 34.0, exp) < 3.5      # exploration atmosphere: below the tested O2 partial pressure
    assert atmosphere_status(70.3, 26.5, exp) == "OUTSIDE" and ppo2_gap(70.3, 26.5, exp) > 2.0
    assert atmosphere_status(101.3, 21.0, exp) == "NEAR"                                                    # ISS-like: on the edge
    assert atmosphere_status(84.0, 28.0, exp) == "INSIDE" and ppo2_gap(84.0, 28.0, exp) == 0.0
    assert atmosphere_status(30.0, 40.0, exp) == "OUTSIDE"
    pp = planned_points(SCENARIOS); assert (56.5, 34.0) in pp and len(pp[(56.5, 34.0)]) == 3 and len(pp) == 3     # transit, lunar, mars share one atmosphere
    # table (text alternative) lists everything with consistent partial pressures
    t = coverage_table(exp, SCENARIOS); assert len(t) == len(exp) + 3 and set(t["Type"]) == {"Experiment", "Planned environment"}
    assert np.allclose(t["O2_partial_kPa"], (t["Pressure_kPa"] * t["Oxygen_pct"] / 100).round(1), atol=0.11)
    assert STATUS_TEXT["OUTSIDE"] in set(t["Status"]) and "Near the tested band" in set(t["Status"])
    # figure structure
    fig = coverage_figure(exp, SCENARIOS, selected="lunar"); names = [tr.name for tr in fig.data]
    assert names[0].startswith("Tested band") and sum(n == "Constant O2 partial pressure" for n in names) == 5
    assert sum(1 for tr in fig.data if tr.marker.symbol == "star" and tr.x[0] is not None) == 3                # three planned atmospheres
    syms = {tr.marker.symbol for tr in fig.data if tr.name and tr.name.startswith("Experiment")}; assert syms == {"circle", "diamond", "triangle-up"}
    sel = [tr for tr in fig.data if tr.marker.symbol == "star" and tr.x[0] == 56.5][0]; assert sel.marker.size > 20, "selected scenario must be emphasised"
    for tr in fig.data:                                                                                      # iso-lines really are constant O2 partial pressure
        if tr.name == "Constant O2 partial pressure":
            v = np.array(tr.x) * np.array(tr.y) / 100; assert np.ptp(v) < 1e-6
    assert fig.layout.xaxis.title.text.startswith("Total pressure") and fig.layout.yaxis.title.text.startswith("Oxygen")
    # overlay of other experiments (ground tests and planned platforms) from the catalog
    C = load_catalog(); f2 = coverage_figure(exp, SCENARIOS, selected="lunar", catalog=C); ov = [tr for tr in f2.data if tr.name and tr.name.startswith("Other experiments")]
    assert len(ov) == 2 and {tr.name for tr in ov} == {"Other experiments: ground (1g) tests", "Other experiments: planned"}, [tr.name for tr in ov]
    rect = [tr for tr in ov if tr.mode == "lines"][0]; assert min(rect.x) == 52.7 and max(rect.x) == 58.6 and min(rect.y) == 30 and max(rect.y) == 34   # the PMMA ignition tests at exploration atmosphere
    assert not any("ZARM" in (tr.hovertemplate or "") for tr in ov), "our own dataset must not be drawn twice"
    t2 = coverage_table(exp, SCENARIOS, catalog=C); assert len(t2) == len(t) + 2 and (t2["Type"] == "Other experiment").sum() == 2
    print("COVERAGE MAP TESTS PASSED | exploration atmosphere gap %.1f kPa | ISS status NEAR | %d table rows" % (ppo2_gap(56.5, 34.0, exp), len(t)))

if __name__ == "__main__":
    test_all()
