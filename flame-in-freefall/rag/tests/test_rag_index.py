"""Index build + retrieval tests on a SYNTHETIC corpus (made-up text, labelled as fixtures; not NASA content).
Uses the hash embedder so no model download is needed. Run from the repo root:  python -m rag.tests.test_rag_index"""
import json, tempfile
from pathlib import Path
from rag.build_index import build
from rag.retrieve import Retriever
from rag.embedder import HashEmbedder

DOCS = {
 "1001": ("Flame spread over thin solid fuel in microgravity", "Test fixture about microgravity flame spread, oxygen concentration and opposed flow.",
          "FIXTURE TEXT. In microgravity the flame spread over a thin solid fuel depends on oxygen concentration and opposed flow velocity. " * 30),
 "1002": ("Spacecraft fire safety and material flammability", "Test fixture about spacecraft fire safety and flammability screening of materials.",
          "FIXTURE TEXT. Spacecraft fire safety relies on flammability screening of cabin materials and fire detection and suppression. " * 30),
 "1003": ("Ignition delay times of aromatic fuels in a shock tube", "Test fixture about gas-phase ignition delay times measured in a shock tube.",
          "FIXTURE TEXT. Ignition delay times were measured behind reflected shock waves for gas-phase mixtures. " * 30),
 "1004": ("Restricted record", "Test fixture: copyright review, no text.", ""),
}

def make_corpus(root: Path):
    (root / "docs").mkdir(parents=True)
    rows = []
    for i, (title, abstract, text) in DOCS.items():
        lf = None
        if i != "1004": (root / "docs" / f"{i}.txt").write_text(text); lf = f"docs/{i}.txt"
        rows.append(dict(id=int(i), title=title, abstract=abstract, authors=["A. Author"], citation_url=f"https://ntrs.nasa.gov/citations/{i}",
                         center="GRC", sti_type="REPORT", local_file=lf, review_copyright=(i == "1004")))
    (root / "manifest.jsonl").write_text("\n".join(json.dumps(r) for r in rows))

def test_all():
    tmp = Path(tempfile.mkdtemp()); make_corpus(tmp / "corpus")
    meta, exc = build(tmp / "corpus", tmp / "index", "hash")
    reasons = {str(i): r for i, _, r in exc}
    assert meta["n_docs"] == 2, meta                                    # only the two relevant documents are indexed
    assert "excluded keyword" in reasons["1003"] and "no document text" in reasons["1004"], reasons
    R = Retriever(tmp / "index", HashEmbedder())
    assert all(len(c["text"]) <= 900 for c in R.chunks), "chunk too long"
    hits = R.search("How does oxygen concentration affect flame spread in microgravity?")
    assert hits[0]["id"] == 1001 and hits[0]["citation_url"].endswith("/1001"), hits[0]
    assert R.search("What is spacecraft fire safety screening of materials?")[0]["id"] == 1002
    on, off = hits[0]["score"], R.search("best pizza toppings recipe")[0]["score"]
    assert on > off + 0.15, (on, off)                                  # on-topic scores clearly above off-topic (basis for tau, step 9)
    assert (tmp / "index" / "excluded.csv").exists() and meta["dim"] == 512
    print(f"RAG INDEX TESTS PASSED | chunks={meta['n_chunks']} docs={meta['n_docs']} | on-topic score {on:.2f} vs off-topic {off:.2f}")

if __name__ == "__main__":
    test_all()
