"""Calibration tests on the SYNTHETIC fixture corpus (hash embedder: test of the code, not of real semantics).
Run from the repo root:  python -m rag.tests.test_calibration"""
import csv, json, tempfile
from pathlib import Path
from rag.build_index import build
from rag.retrieve import Retriever, REFUSAL
from rag.embedder import HashEmbedder
from rag.calibrate import calibrate, choose_tau, fbeta, auc
from rag.tests.test_rag_index import make_corpus
import numpy as np

IN = ["How does oxygen concentration affect flame spread over thin solid fuel in microgravity?",
      "What is the effect of opposed flow on flame spread in microgravity?",
      "Does oxygen concentration change flame spread over a solid fuel?",
      "How does flame spread depend on oxygen and opposed flow velocity?",
      "Flame spread over thin solid fuel in microgravity",
      "What affects the spread of a flame over a thin solid fuel?",
      "How does spacecraft fire safety rely on flammability screening of materials?",
      "What is flammability screening of cabin materials for spacecraft fire safety?",
      "Why is fire detection and suppression important for spacecraft fire safety?",
      "How are cabin materials screened for flammability in spacecraft?",
      "Spacecraft fire safety and material flammability",
      "What does spacecraft fire safety need for cabin materials?"]
OUT = ["best pizza topping recipe", "who won the football match yesterday", "how to fix a leaking kitchen faucet",
       "current price of a bitcoin", "write a poem about the ocean", "symptoms of the flu and how to treat them",
       "which programming language should I learn", "capital city of australia", "translate good morning into french",
       "painting by leonardo", "how to reduce electricity bill", "weather forecast for tomorrow"]

def test_all():
    tmp = Path(tempfile.mkdtemp()); make_corpus(tmp / "corpus"); build(tmp / "corpus", tmp / "index", "hash")
    q = tmp / "q.csv"
    with open(q, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["id", "question", "label", "category"])
        for i, t in enumerate(IN): w.writerow([f"in{i}", t, "in", "x"])
        for i, t in enumerate(OUT): w.writerow([f"out{i}", t, "out", "x"])
    rep = calibrate(tmp / "index", q, tmp / "tau.json", HashEmbedder())
    assert rep["auc"] > 0.95 and not rep["warnings"], rep
    assert rep["wrongly_answered"] == [] and rep["train"]["answer_precision"] == 1.0, rep          # biased toward refusing
    assert rep["cross_validated"]["false_answers"] == 0, rep["cross_validated"]
    assert rep["out_max"] < rep["tau"] <= rep["in_median"], (rep["out_max"], rep["tau"], rep["in_median"])
    # gate behaviour
    R = Retriever(tmp / "index", HashEmbedder()); R.load_tau(tmp / "tau.json")
    ok, hits = R.answerable("How does oxygen concentration affect flame spread in microgravity?"); assert ok and hits[0]["citation_url"]
    ok2, _ = R.answerable("what is the best pizza topping"); assert not ok2 and isinstance(REFUSAL, str)
    # stale tau is rejected when the index changes
    t = json.loads((tmp / "tau.json").read_text()); t["corpus_signature"] = "deadbeef"; (tmp / "tau_bad.json").write_text(json.dumps(t))
    try: R.load_tau(tmp / "tau_bad.json"); raise AssertionError("stale tau accepted")
    except AssertionError as e: assert "different index" in str(e)
    # unit checks of the maths
    s = np.array([.1, .2, .3, .7, .8, .9]); y = np.array([0, 0, 0, 1, 1, 1]); assert .3 < choose_tau(s, y) <= .7 and auc(s, y) == 1.0
    assert abs(fbeta(y, (s >= .5).astype(int))[0] - 1.0) < 1e-9
    # ties and overlap: tau leans toward refusing
    s2 = np.array([.2, .5, .5, .5, .9]); y2 = np.array([0, 0, 1, 0, 1]); assert choose_tau(s2, y2) > .5
    print(f"CALIBRATION TESTS PASSED | tau={rep['tau']:.3f} | out max {rep['out_max']:.2f} < in median {rep['in_median']:.2f} | AUC {rep['auc']:.2f}")

if __name__ == "__main__":
    test_all()
