"""App-level test for the Documents & Topic Synthesis tab (AppTest).
Validates:
- Rendering of Documents & Synthesis tab without exceptions
- Topic synthesis selectbox interaction and metric display
- Document explorer search and filter controls

Run from repo root: python app/tests/test_app_documents.py
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

def test_documents_tab_rendering():
    at = AppTest.from_file(APP, default_timeout=120).run()
    assert not at.exception, f"App threw exception: {at.exception}"
    
    # Check that synthesis card, document explorer, terrestrial spin-offs, and historic incidents cards are present in markdown
    md_texts = [m.value for m in at.markdown]
    assert any("Topic synthesis" in m for m in md_texts)
    assert any("Document explorer" in m for m in md_texts)
    assert any("Terrestrial spin-offs" in m for m in md_texts)
    assert any("Historic spaceflight fires" in m for m in md_texts)
    
    # Check topic selector exists and can change
    syn_selects = [s for s in at.selectbox if s.key == "syn_topic_choice"]
    assert len(syn_selects) == 1
    syn_selects[0].set_value("microgravity").run()
    assert not at.exception
    
    # Check document search input exists
    search_inputs = [t for t in at.text_input if t.key == "doc_search_query"]
    assert len(search_inputs) == 1
    search_inputs[0].set_value("flame").run()
    assert not at.exception

    # Check terrestrial spin-off filter and search
    spinoff_selects = [s for s in at.selectbox if s.key == "spinoff_cat"]
    assert len(spinoff_selects) == 1
    spinoff_selects[0].set_value("Suppression").run()
    assert not at.exception

    spinoff_inputs = [t for t in at.text_input if t.key == "spinoff_query"]
    assert len(spinoff_inputs) == 1
    spinoff_inputs[0].set_value("mist").run()
    assert not at.exception

    # Check historic incidents selector
    inc_selects = [s for s in at.selectbox if s.key == "inc_choice"]
    assert len(inc_selects) == 1
    inc_selects[0].set_value("INC-03").run()
    assert not at.exception

    # Check Deep-Space Comm Blackout toggle
    toggles = [t for t in at.toggle if t.key == "sim_blackout_toggle"]
    assert len(toggles) == 1, "sim_blackout_toggle must be present in sidebar"
    assert toggles[0].value is False
    toggles[0].set_value(True).run()
    assert not at.exception
    md_texts = [m.value for m in at.markdown]
    assert any("Deep-Space Blackout Active" in m for m in md_texts), "Blackout status should be reflected in telemetry"

    # Check Live Non-Dimensional Physics HUD elements in tab1
    assert any("Live Non-Dimensional Physics HUD" in m for m in md_texts), "Live Physics HUD must be rendered"
    assert any("Péclet" in m for m in md_texts), "Peclet number must be rendered"
    assert any("Damköhler" in m for m in md_texts), "Damkohler number must be rendered"
    assert any("Grashof" in m for m in md_texts), "Grashof number must be rendered"

    # Check Question Discovery Vault & Context-Aware Prompt in AI Assistant tab
    exp_labels = [e.label for e in at.expander]
    assert any("Question Discovery Vault" in l for l in exp_labels), "Question Discovery Vault expander missing"
    assert any("AI Knowledge Boundaries" in l for l in exp_labels), "Knowledge Boundaries expander missing"
    assert any("Active Atmosphere" in m for m in md_texts), "Active atmosphere context card missing"
    assert any(b.key == "btn_ask_ctx" for b in at.button), "btn_ask_ctx missing"
    assert any(b.key == "chip_q1" for b in at.button), "chip_q1 missing"
    assert any(b.key == "chip_q3" for b in at.button), "chip_q3 missing"
    
    # Check What-If Spaceflight Emergency Scenarios in tab1
    assert any("What-If?" in m for m in md_texts), "What-If scenarios card missing"
    assert any(b.key == "btn_wi_lunar" for b in at.button), "btn_wi_lunar missing"
    assert any(b.key == "btn_wi_iss" for b in at.button), "btn_wi_iss missing"
    assert any(b.key == "btn_wi_cfig" for b in at.button), "btn_wi_cfig missing"
    assert any(b.key == "btn_wi_barrier" for b in at.button), "btn_wi_barrier missing"

    # Check 30-Second Mission Tour & Judge Walkthrough banner
    assert any("30-Second Mission Tour" in l for l in exp_labels), "Mission tour expander missing"
    assert any(b.key == "btn_tour_iss" for b in at.button), "btn_tour_iss missing"
    assert any(b.key == "btn_tour_lunar" for b in at.button), "btn_tour_lunar missing"
    assert any(b.key == "btn_tour_blackout" for b in at.button), "btn_tour_blackout missing"
    assert any(b.key == "btn_tour_dismiss" for b in at.button), "btn_tour_dismiss missing"
    
    print("APP DOCUMENTS & SYNTHESIS TAB TESTS PASSED")

if __name__ == "__main__":
    test_documents_tab_rendering()

