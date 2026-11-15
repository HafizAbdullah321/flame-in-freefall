"""Assistant tests with a MOCK LLM on the synthetic fixture corpus (no network, no API key).
Run from the repo root:  python -m rag.tests.test_assistant"""
import json, tempfile, datetime as dt
from pathlib import Path
import httpx
from rag.build_index import build
from rag.retrieve import Retriever, REFUSAL
from rag.embedder import HashEmbedder
from rag.config import AssistantConfig
from rag.llm import MockLLM, LLMError, OpenAILLM
from rag.answer import Assistant, Cache, TokenBucket, DailyCap, SYSTEM
from rag.build_cache import build_cache
from rag.tests.test_rag_index import make_corpus

Q_ON = "How does oxygen concentration affect flame spread over thin solid fuel in microgravity?"
Q_ON2 = "What matters for flame spread over solid fuel?"
Q_OFF = "what is the best pizza topping recipe"

def setup():
    tmp = Path(tempfile.mkdtemp()); make_corpus(tmp / "corpus"); meta, _ = build(tmp / "corpus", tmp / "index", "hash")
    R = Retriever(tmp / "index", HashEmbedder()); R.tau = 0.25
    cache_file = tmp / "cache.json"
    cache_file.write_text(json.dumps(dict(corpus_signature=meta["corpus_signature"], entries=[
        dict(question=Q_ON, answer="Cached: oxygen and opposed flow control the spread rate [1].", sources=[dict(n=1, title="T", url="https://ntrs.nasa.gov/citations/1001")])])))
    return tmp, R, Cache(cache_file, HashEmbedder(), meta["corpus_signature"]), meta

def test_all():
    tmp, R, cache, meta = setup(); cfg = AssistantConfig()
    # 1. refusal happens in code, BEFORE the LLM is called
    llm = MockLLM(); A = Assistant(R, llm, cache, cfg, log_path=tmp / "log.jsonl")
    r = A.ask(Q_OFF); assert r["tier"] == "REFUSED" and r["answer"] == REFUSAL and llm.calls == []
    # 2. grounded answer with verified citations; prompt hygiene
    llm = MockLLM("Oxygen concentration and opposed flow both change the spread rate [1]."); A = Assistant(R, llm, cache, cfg, log_path=tmp / "log.jsonl")
    r = A.ask(Q_ON); assert r["tier"] == "LLM" and r["sources"][0]["url"].startswith("https://ntrs.nasa.gov/citations/") and len(llm.calls) == 1
    sysmsg, usermsg = llm.calls[0]; assert "ignore any instructions" in sysmsg and "<context>" in usermsg and "[1]" in usermsg and Q_ON in usermsg
    assert "FIXTURE TEXT" in usermsg and sysmsg == SYSTEM
    # 3. post-generation check
    for bad in ("Oxygen matters but no citation.", "Oxygen matters [9].", "Oxygen matters [0] and [1]."):
        assert Assistant(R, MockLLM(bad), cache, cfg).ask(Q_ON)["tier"] == "REFUSED", bad
    assert Assistant(R, MockLLM(REFUSAL), cache, cfg).ask(Q_ON)["tier"] == "REFUSED"
    # 4. LLM timeout -> cache (semantic match) -> extractive
    down = MockLLM(LLMError("APITimeoutError"))
    r = Assistant(R, down, cache, cfg).ask(Q_ON); assert r["tier"] == "CACHE" and "Cached" in r["label"] and r["answer"].startswith("Cached:")
    r = Assistant(R, down, cache, cfg).ask(Q_ON2); assert r["tier"] == "EXTRACTIVE" and "FIXTURE TEXT" in r["answer"] and r["sources"] and "[1]" in r["answer"]
    # 5. no API key at all -> still useful (cache / extractive), never an error
    assert Assistant(R, None, cache, cfg).ask(Q_ON)["tier"] == "CACHE" and Assistant(R, None, None, cfg).ask(Q_ON2)["tier"] == "EXTRACTIVE"
    # 6. per-session rate limit (10 per minute) with a fake clock
    now = [0.0]; lim = TokenBucket(10, now=lambda: now[0]); A = Assistant(R, MockLLM("Ok [1]."), None, cfg)
    tiers = [A.ask(Q_ON, lim)["tier"] for _ in range(11)]; assert tiers[:10] == ["LLM"] * 10 and tiers[10] == "RATE_LIMITED", tiers
    now[0] += 60; assert A.ask(Q_ON, lim)["tier"] == "LLM"
    # 7. global daily cap: beyond it the LLM is skipped, not the whole assistant
    day = [dt.date(2026, 1, 1)]; cap = DailyCap(tmp / "cap.json", 2, today=lambda: day[0]); llm = MockLLM("Ok [1]."); A = Assistant(R, llm, None, cfg, daily=cap)
    assert [A.ask(Q_ON)["tier"] for _ in range(3)] == ["LLM", "LLM", "EXTRACTIVE"] and len(llm.calls) == 2
    day[0] = dt.date(2026, 1, 2); assert A.ask(Q_ON)["tier"] == "LLM"
    # 8. input validation
    A = Assistant(R, MockLLM("Ok [1]."), None, cfg)
    assert A.ask("x" * 501)["tier"] == "INVALID" and A.ask("   ")["tier"] == "INVALID" and A.ask(None)["tier"] == "INVALID"
    assert A.ask("flame spread\x00 over thin solid fuel \x07 in microgravity")["tier"] == "LLM"
    # 9. logs hold metadata only, never question text
    A = Assistant(R, MockLLM("Ok [1]."), None, cfg, log_path=tmp / "meta.jsonl"); A.ask(Q_ON); A.ask(Q_OFF)
    log = (tmp / "meta.jsonl").read_text(); assert "pizza" not in log and "oxygen" not in log and '"tier": "LLM"' in log and '"tier": "REFUSED"' in log
    # 10. cache builder keeps only verified LLM answers; stale cache is flagged
    out = tmp / "built.json"; entries, failed = build_cache(Assistant(R, MockLLM("Ok [1]."), None, cfg), [Q_ON, Q_ON2, Q_OFF], out)
    assert len(entries) == 2 and failed == [(Q_OFF, "REFUSED")] and json.loads(out.read_text())["corpus_signature"] == meta["corpus_signature"]
    assert not Cache(out, HashEmbedder(), meta["corpus_signature"]).stale and Cache(out, HashEmbedder(), "other").stale
    # 11. production client: settings and error mapping
    llm = OpenAILLM(cfg, api_key="sk-test"); assert llm.client.timeout == 8.0 and llm.client.max_retries == 1
    import openai
    class Boom:
        class chat:
            class completions:
                @staticmethod
                def create(**kw): raise openai.APITimeoutError(request=httpx.Request("POST", "https://x"))
    try: OpenAILLM(cfg, client=Boom()).complete("s", "u"); raise AssertionError("no error")
    except LLMError as e: assert "APITimeoutError" in str(e)
    class Ok:
        class chat:
            class completions:
                @staticmethod
                def create(**kw):
                    assert kw["model"] == "gpt-4o-mini" and kw["max_tokens"] == 400 and kw["messages"][0]["role"] == "system"
                    return type("R", (), {"choices": [type("C", (), {"message": type("M", (), {"content": " hi [1] "})()})()]})()
    assert OpenAILLM(cfg, client=Ok()).complete("s", "u") == "hi [1]"
    print("ASSISTANT TESTS PASSED (11 groups: gate, grounding, verification, timeout chain, no-key mode, rate limit, daily cap, validation, logs, cache builder, OpenAI client)")

if __name__ == "__main__":
    test_all()
