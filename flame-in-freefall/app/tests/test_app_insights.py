"""App-level tests for the AI brief flow with a MOCK LLM (AppTest, no network). Run from the repo root: python app/tests/test_app_insights.py"""
import os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT / "backend")); sys.path.insert(0, str(ROOT)); os.chdir(ROOT)
import streamlit as st
from streamlit.testing.v1 import AppTest
import rag.llm as L
from insights.tests.test_si_brief import GOOD_LUNAR
import insights.si_brief as sb

APP = str(ROOT / "app/streamlit_app.py")
def run(reply, key=True):
    if key: os.environ["OPENAI_API_KEY"] = "sk-test"
    else: os.environ.pop("OPENAI_API_KEY", None)
    L.OpenAILLM = lambda cfg, api_key=None, client=None: L.MockLLM(reply)          # the app imports it inside get_llm(), so the patch applies
    sb._CACHE.clear(); st.cache_resource.clear(); st.cache_data.clear()                                 # get_llm() is cached; each scenario needs a fresh client
    at = AppTest.from_file(APP, default_timeout=90).run(); assert not at.exception, at.exception
    at.selectbox[0].set_value("lunar").run(); return at

def test_all():
    at = run("unused", key=False); assert not [b for b in at.button if b.key == "brief_ai"] and any("AI-written briefs are off" in c.value for c in at.caption)
    assert any("Scenario:" in m.value and "NASA's documents" in m.value for m in at.markdown), "rule-based brief must always show"
    at = run(GOOD_LUNAR); btn = [b for b in at.button if b.key == "brief_ai"][0]; btn.click(); at.run(); assert not at.exception
    assert any("AI-written brief" in s.value for s in at.success) and any(m.value.startswith("Scenario: Lunar habitat") for m in at.markdown)
    assert any("Not certified fire-safety guidance" in m.value for m in at.markdown)
    dl = [m.value for m in at.markdown if m.value.startswith("Scenario: Lunar habitat")]; assert dl
    bad = run(GOOD_LUNAR.replace("0.16 g.", "0.16 g, flame spread of 7.3 mm/s.")); [b for b in bad.button if b.key == "brief_ai"][0].click(); bad.run(); assert not bad.exception
    assert any("failed verification" in w.value for w in bad.warning) and not any("AI-written brief" in s.value for s in bad.success)
    assert any("**Scenario:**" in m.value for m in bad.markdown), "fallback must be the rule-based brief"
    down = run(L.LLMError("APITimeoutError")); [b for b in down.button if b.key == "brief_ai"][0].click(); down.run()
    assert any("unavailable" in w.value for w in down.warning)
    # rate limit: 5 AI requests per minute per session
    lim = run(GOOD_LUNAR)
    for i in range(7):
        lim.selectbox[0].set_value("lunar" if i % 2 else "lunar_alt").run(); [b for b in lim.button if b.key == "brief_ai"][0].click(); lim.run()
    assert any("Too many AI requests" in w.value for w in lim.warning)
    print("APP BRIEF TESTS PASSED | no-key mode, verified AI brief, rejected AI brief, service down, rate limit")

if __name__ == "__main__":
    test_all()
