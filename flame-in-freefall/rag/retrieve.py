"""Retriever over the FAISS index. Scores are cosine similarity (higher is better)."""
import json
from pathlib import Path
import numpy as np, faiss
from .config import RagConfig
from .embedder import get_embedder

REFUSAL = "Insufficient experimental data in the NASA repository to verify this query."

class Retriever:
    def __init__(self, index_dir, embedder=None, cfg=RagConfig()):
        d = Path(index_dir); self.cfg = cfg
        self.meta = json.loads((d / "index_meta.json").read_text())
        self.index = faiss.read_index(str(d / "faiss.index"))
        self.chunks = [json.loads(l) for l in (d / "chunks.jsonl").read_text().splitlines()]
        self.embedder = embedder or get_embedder("hash" if self.meta["embedder"].startswith("hash") else "fastembed", cfg.embed_model)
        assert self.embedder.name == self.meta["embedder"], f"index built with {self.meta['embedder']}, got {self.embedder.name}"
        self.tau = 0.65
        if (d / "tau.json").exists():
            try: self.load_tau(d / "tau.json")
            except Exception: pass

    def search(self, query, k=None):
        s, i = self.index.search(self.embedder.embed([query]), k or self.cfg.top_k)
        return [dict(score=float(sc), **self.chunks[ix]) for sc, ix in zip(s[0], i[0]) if ix >= 0]

    def load_tau(self, path):
        t = json.loads(Path(path).read_text())
        assert t["embedder"] == self.meta["embedder"] and t["corpus_signature"] == self.meta["corpus_signature"], \
            "tau was calibrated for a different index or embedder: re-run rag.calibrate"
        self.tau = float(t["tau"]); return self.tau

    def answerable(self, query, k=None):
        """Refusal gate (runs in code, before any LLM call). Returns (ok, hits)."""
        hits = self.search(query, k)
        return bool(hits and hits[0]["score"] >= self.tau), hits
