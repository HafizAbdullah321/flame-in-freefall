"""Tests for the Mission Fire Safety Report Exporter (REQ-E9).
Run from repo root: python -m insights.tests.test_report_export
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

import pandas as pd
from ffbackend.predict import Predictor
from insights.scenarios import SCENARIOS, evaluate
from insights.findings import load_findings, rank_findings
from insights.risk_cards import build_cards
from insights.brief import build_brief
from insights.report_export import build_markdown_report, build_html_report

def test_report_export():
    P = Predictor.load(ROOT / "backend/artifacts/ff_model.joblib")
    exp = pd.read_csv(ROOT / "phase0/raw/zarm_experiments_global.csv")
    exp["o2_pct"] = exp["o2_frac"] * 100
    F = load_findings()
    
    sc = SCENARIOS["lunar"]
    ev = evaluate(sc, P, exp)
    ranked = rank_findings(F, sc.g, sc.o2_pct, sc.pressure_kpa, sc.tags)
    cards = build_cards(ev, ranked)
    brief = build_brief(ev, ranked)
    
    fixed_ts = "2026-10-31 00:00 UTC"
    md = build_markdown_report(sc, ev, ranked, cards, brief, timestamp=fixed_ts)
    
    # Assertions on content and repeatability
    assert "Lunar habitat" in md
    assert "0.16 g" in md
    assert "NOT_COVERED" in md
    assert "Topic Risk Assessment Matrix" in md
    assert "Top-Ranked NASA Experimental Findings" in md
    assert "Executive Fire Safety Brief" in md
    assert "Terrestrial Spin-offs" in md
    assert "Data Provenance & Safety Disclaimer" in md
    assert fixed_ts in md
    
    # Repeatability test: identical inputs give identical output
    md2 = build_markdown_report(sc, ev, ranked, cards, brief, timestamp=fixed_ts)
    assert md == md2, "Report generation must be deterministic"
    
    # HTML report test
    html_rep = build_html_report(sc, ev, ranked, cards, brief, timestamp=fixed_ts)
    assert "<!DOCTYPE html>" in html_rep
    assert "Lunar habitat" in html_rep
    
    print("REPORT EXPORT TESTS PASSED")

if __name__ == "__main__":
    test_report_export()

