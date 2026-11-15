"""Build the FAISS index from the harvested NTRS corpus.

  python -m rag.build_index --corpus rag/corpus --out rag/index            # production (fastembed)
  python -m rag.build_index --corpus rag/corpus --out rag/index --embedder hash   # offline test

Inputs : corpus/manifest.jsonl + corpus/docs/<id>.txt (from ntrs_harvest.py)
Outputs: index/faiss.index, index/chunks.jsonl, index/index_meta.json, index/excluded.csv
"""
import argparse, csv, json, hashlib, datetime as dt
from pathlib import Path
import numpy as np, faiss
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import RagConfig
from .embedder import get_embedder

def relevant(rec, cfg):
    text = f"{rec.get('title') or ''} {rec.get('abstract') or ''}".lower()
    if any(k in text for k in cfg.exclude_kw): return False, "excluded keyword"
    if not any(k in text for k in cfg.must_kw): return False, "no relevance keyword"
    return True, ""

def build(corpus: Path, out: Path, embedder="fastembed", cfg=RagConfig()):
    man = [json.loads(l) for l in (corpus / "manifest.jsonl").read_text().splitlines() if l.strip()]
    splitter = RecursiveCharacterTextSplitter(chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap)
    chunks, excluded = [], []
    for rec in man:
        if not rec.get("local_file"):
            excluded.append((rec["id"], rec.get("title"), "no document text (metadata only or copyright review)")); continue
        ok, why = relevant(rec, cfg)
        if not ok:
            excluded.append((rec["id"], rec.get("title"), why)); continue
        text = (corpus / rec["local_file"]).read_text(errors="ignore")
        for j, piece in enumerate(splitter.split_text(text)):
            chunks.append(dict(text=piece, id=rec["id"], chunk=j, title=rec.get("title"), authors=rec.get("authors"),
                               citation_url=rec["citation_url"], center=rec.get("center"), sti_type=rec.get("sti_type")))
    if not chunks: raise SystemExit("No relevant documents to index. Check the corpus and the relevance filter.")
    emb = get_embedder(embedder, cfg.embed_model)
    vecs = np.vstack([emb.embed([c["text"] for c in chunks[i:i + 64]]) for i in range(0, len(chunks), 64)])
    index = faiss.IndexFlatIP(vecs.shape[1]); index.add(vecs)           # normalized vectors -> inner product = cosine
    out.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(out / "faiss.index"))
    (out / "chunks.jsonl").write_text("\n".join(json.dumps(c) for c in chunks))
    sig = hashlib.sha256("".join(sorted(str(r["id"]) for r in man)).encode()).hexdigest()[:12]
    meta = dict(embedder=emb.name, dim=int(vecs.shape[1]), n_chunks=len(chunks), n_docs=len({c["id"] for c in chunks}),
                corpus_signature=sig, built_at=dt.datetime.now(dt.timezone.utc).isoformat(), chunk_size=cfg.chunk_size)
    (out / "index_meta.json").write_text(json.dumps(meta, indent=1))
    with open(out / "excluded.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "title", "reason"]); w.writerows(excluded)
    return meta, excluded

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--corpus", default="rag/corpus"); ap.add_argument("--out", default="rag/index")
    ap.add_argument("--embedder", default="fastembed", choices=["fastembed", "hash"])
    a = ap.parse_args(); meta, exc = build(Path(a.corpus), Path(a.out), a.embedder)
    print(json.dumps(meta, indent=1)); print(f"{len(exc)} documents excluded (see {a.out}/excluded.csv)")
