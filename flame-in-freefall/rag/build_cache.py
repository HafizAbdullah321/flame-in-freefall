"""Pre-compute answers for the 15 critical questions (needs the index, tau.json and OPENAI_API_KEY).
  python -m rag.build_cache --index rag/index --tau rag/tau.json --out rag/cache.json
Only answers that pass citation verification (tier LLM) are stored. Re-run whenever the corpus changes."""
import argparse, json, datetime as dt
from pathlib import Path
from .config import AssistantConfig, CACHE_QUESTIONS

def build_cache(assistant, questions, out):
    entries, failed = [], []
    for q in questions:
        r = assistant.ask(q)
        if r["tier"] == "LLM": entries.append(dict(question=q, answer=r["answer"], sources=r["sources"]))
        else: failed.append((q, r["tier"]))
    Path(out).write_text(json.dumps(dict(corpus_signature=assistant.R.meta["corpus_signature"], embedder=assistant.R.meta["embedder"],
                                         built_at=dt.datetime.now(dt.timezone.utc).isoformat(), entries=entries), indent=1))
    return entries, failed

if __name__ == "__main__":
    from .retrieve import Retriever
    from .llm import OpenAILLM
    from .answer import Assistant
    ap = argparse.ArgumentParser(); ap.add_argument("--index", default="rag/index"); ap.add_argument("--tau", default="rag/tau.json")
    ap.add_argument("--out", default="rag/cache.json"); a = ap.parse_args()
    cfg = AssistantConfig(); R = Retriever(a.index); R.load_tau(a.tau)
    entries, failed = build_cache(Assistant(R, OpenAILLM(cfg), cfg=cfg), CACHE_QUESTIONS, a.out)
    print(f"{len(entries)} cached, {len(failed)} skipped"); [print("  skipped:", q, "->", t) for q, t in failed]
