"""App-level test for the Natural-Language Scenario feature (REQ-E7).
Validates:
- Expandable NL scenario box
- Input of natural language description and button click
- Proper parsing feedback and scenario activation

Run from repo root: python app/tests/test_app_nl_scenario.py
"""
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import streamlit as st
from streamlit.testing.v1 import AppTest

APP = str(ROOT / "app/streamlit_app.py")

def test_app_nl_scenario_flow():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception, f"App threw exception: {at.exception}"

    # Verify NL scenario query box exists
    nl_inputs = [t for t in at.text_input if t.key == "nl_query"]
    assert len(nl_inputs) == 1, "Missing nl_query text input"

    # Input a lunar habitat description
    nl_inputs[0].set_value("lunar habitat at 8 psi and 30% oxygen").run()
    assert not at.exception

    # Click parse button
    parse_btns = [b for b in at.button if b.key == "btn_parse_nl"]
    assert len(parse_btns) == 1, "Missing btn_parse_nl button"
    parse_btns[0].click().run()
    assert not at.exception

    # Check for success message and activate button
    assert any("Parsed scenario" in s.value for s in at.success)
    apply_btns = [b for b in at.button if b.key == "btn_apply_nl"]
    assert len(apply_btns) == 1, "Missing btn_apply_nl button"

    # Click activate button
    apply_btns[0].click().run()
    assert not at.exception

    print("APP NATURAL-LANGUAGE SCENARIO TESTS PASSED")

if __name__ == "__main__":
    test_app_nl_scenario_flow()

