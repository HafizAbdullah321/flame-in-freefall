"""Run the NTRS harvest for the project's queries (run this on YOUR machine; needs internet).
  python -m rag.harvest_all --per-query 15
Then:  python -m rag.build_index"""
import argparse
from pathlib import Path
from . import ntrs_harvest as h

QUERIES = ["flame spread microgravity", "BASS-II solid fuel combustion", "SoFIE solid fuel ignition and extinction",
           "Saffire spacecraft fire experiment", "LUCI lunar gravity combustion", "NASA-STD-6001 flammability",
           "spacecraft fire safety", "flammability microgravity PMMA", "ACME advanced combustion microgravity experiments",
           "opposed flow flame spread thin fuel", "partial gravity flame spread"]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default="rag/corpus"); ap.add_argument("--per-query", type=int, default=15)
    a = ap.parse_args(); root = Path(a.root); root.mkdir(parents=True, exist_ok=True)
    for q in QUERIES:
        print("==", q); h.harvest(q, root, a.per_query)
    print("Done. Review corpus/manifest.jsonl, then build the index. Run `python -m rag.ntrs_harvest sync` weekly.")
