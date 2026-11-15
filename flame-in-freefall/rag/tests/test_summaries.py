"""Tests for per-document executive summaries and document explorer (REQ-E4).
Validates:
- Extractive summary <= 120 words and cites the source
- Verification of grounding (number checks, word limit, banned safety phrases)
- Mock LLM generation: valid output accepted (SI), invalid output falls back (EXTRACTIVE)
- Error handling & daily cap fallbacks
- Filtering and catalog search

Run from repo root: python -m rag.tests.test_summaries
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from rag.llm import MockLLM, LLMError
from rag.summaries import (
    MAX_WORDS,
    extractive_summary,
    verify_summary,
    generate_summary,
    load_summaries,
    filter_summaries,
)

SOURCE_DOC = {
    "id": 20150008962,
    "title": "Concurrent Flame Growth, Spread and Extinction over Composite Fabric Samples in Low Speed Purely Forced Flow in Microgravity",
    "abstract": (
        "As a part of the NASA BASS and BASS-II experimental projects aboard the International Space Station, "
        "flame growth, spread and extinction over a composite cotton-fiberglass fabric blend were studied in low-speed concurrent forced flows. "
        "Ambient oxygen was varied from 21% down to 16% and flow speed from 40 cm/s down to 1 cm/s. "
        "Low-speed flame quenching extinction limits were found to be between 1 and 5 cm/s with higher speed in lower oxygen atmosphere."
    ),
    "authors": ["Zhao, Xiaoyang", "T'ien, James S.", "Ferkul, Paul V.", "Olson, Sandra L."],
    "sti_type": "CONFERENCE_PAPER",
}

def test_extractive_summary():
    s = extractive_summary(SOURCE_DOC, max_words=120)
    words = s.split()
    assert len(words) <= 120, f"Extractive summary too long: {len(words)} words"
    assert "20150008962" in s or "NTRS" in s
    assert "NASA BASS" in s

def test_verify_summary():
    src = SOURCE_DOC["abstract"]
    # 1. Valid summary
    valid = "Tests aboard ISS varied oxygen from 21% down to 16% and flow speed between 1 and 5 cm/s. [NTRS 20150008962]"
    ok, why = verify_summary(valid, src, doc_id=20150008962, max_words=120)
    assert ok, f"Expected valid summary to pass: {why}"

    # 2. Too long
    too_long = "word " * 125 + "[NTRS 20150008962]"
    ok, why = verify_summary(too_long, src, doc_id=20150008962, max_words=120)
    assert not ok
    assert any("longer than" in w for w in why)

    # 3. Hallucinated number
    hallucinated = "Tests showed extinction occurred at 99.4 cm/s and 75% oxygen. [NTRS 20150008962]"
    ok, why = verify_summary(hallucinated, src, doc_id=20150008962, max_words=120)
    assert not ok
    assert any("not in source text" in w for w in why)

    # 4. Banned safety claim
    banned = "Experiments proved this material is safe and risk-free in low oxygen. [NTRS 20150008962]"
    ok, why = verify_summary(banned, src, doc_id=20150008962, max_words=120)
    assert not ok
    assert any("banned phrase" in w for w in why)

def test_generate_summary_mock_llm():
    # Good LLM reply
    good_reply = (
        "ISS experiments studied flame spread over fabric in microgravity with 16% to 21% oxygen. "
        "Extinction quenching speeds were measured between 1 and 5 cm/s. [NTRS 20150008962]"
    )
    llm = MockLLM(good_reply)
    res = generate_summary(SOURCE_DOC, chunks_text=SOURCE_DOC["abstract"], llm=llm)
    assert res["method"] == "SI"
    assert res["summary"] == good_reply
    assert res["word_count"] <= 120

    # Bad LLM reply with hallucinated number -> falls back to EXTRACTIVE
    bad_reply = "Spread rate was 888.8 mm/s in microgravity. [NTRS 20150008962]"
    llm_bad = MockLLM(bad_reply)
    res_bad = generate_summary(SOURCE_DOC, chunks_text=SOURCE_DOC["abstract"], llm=llm_bad)
    assert res_bad["method"] == "EXTRACTIVE"
    assert any("failed verification" in r for r in res_bad["reasons"])
    assert res_bad["word_count"] <= 120

    # LLM throws error -> falls back to EXTRACTIVE
    llm_err = MockLLM(LLMError("API timeout"))
    res_err = generate_summary(SOURCE_DOC, chunks_text=SOURCE_DOC["abstract"], llm=llm_err)
    assert res_err["method"] == "EXTRACTIVE"
    assert any("AI service error" in r for r in res_err["reasons"])

def test_load_and_filter():
    summaries = load_summaries()
    assert len(summaries) > 0
    # Filter by query
    f_flame = filter_summaries(summaries, query="flame")
    assert len(f_flame) > 0
    # Filter by STI type
    f_conf = filter_summaries(summaries, sti_type="CONFERENCE_PAPER")
    assert all(r.get("sti_type") == "CONFERENCE_PAPER" for r in f_conf)

def test_all():
    test_extractive_summary()
    test_verify_summary()
    test_generate_summary_mock_llm()
    test_load_and_filter()
    print("RAG SUMMARIES TESTS PASSED | Extractive fallback, verification rules, Mock LLM & filter validated")

if __name__ == "__main__":
    test_all()

