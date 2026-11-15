"""Calibrate the refusal threshold tau (step 9, REQ-R2).

Answer when top-1 cosine >= tau, refuse otherwise. tau maximizes F-beta (beta=0.5, i.e. precision-weighted, biased
toward refusing) for the 'answer' class on a labelled question set. Reported honestly with cross-validation.

  python -m rag.calibrate --index rag/index --questions rag/questions.csv --out rag/tau.json
Review rag/questions.csv first: delete in-scope questions your corpus cannot actually answer."""
import argparse, csv, json
from pathlib import Path
import numpy as np
from .retrieve import Retriever

def load_questions(path):
    rows = list(csv.DictReader(open(path)))
    return [r["question"] for r in rows], np.array([1 if r["label"] == "in" else 0 for r in rows]), [r.get("category", "") for r in rows]

def top1_scores(R, qs):
    return np.array([(R.search(q, 1) or [{"score": -1.0}])[0]["score"] for q in qs])

def fbeta(y, pred, beta=0.5):
    tp = int(((pred == 1) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum()); fn = int(((pred == 0) & (y == 1)).sum())
    p = tp / (tp + fp) if tp + fp else 1.0; r = tp / (tp + fn) if tp + fn else 0.0
    return (1 + beta ** 2) * p * r / (beta ** 2 * p + r) if p + r else 0.0, p, r

def choose_tau(s, y, beta=0.5):
    cands = np.unique(np.concatenate([s, [s.min() - 1e-6, s.max() + 1e-6]]))
    best = max(cands, key=lambda t: (fbeta(y, (s >= t).astype(int), beta)[0], t))     # ties -> higher tau (refuse more)
    return float(best)

def auc(s, y):
    pos, neg = s[y == 1], s[y == 0]
    return float(np.mean([(p > n) + 0.5 * (p == n) for p in pos for n in neg]))

def cross_validated(s, y, k=5, seed=0):
    rng = np.random.default_rng(seed); idx = rng.permutation(len(s)); folds = np.array_split(idx, k); preds = np.zeros(len(s), int)
    for f in folds:
        tr = np.setdiff1d(idx, f); t = choose_tau(s[tr], y[tr]); preds[f] = (s[f] >= t).astype(int)
    _, p, r = fbeta(y, preds)
    refuse_prec = float(((preds == 0) & (y == 0)).sum() / max((preds == 0).sum(), 1)); refuse_rec = float(((preds == 0) & (y == 0)).sum() / max((y == 0).sum(), 1))
    return dict(answer_precision=p, answer_recall=r, refusal_precision=refuse_prec, refusal_recall=refuse_rec,
                false_answers=int(((preds == 1) & (y == 0)).sum()), false_refusals=int(((preds == 0) & (y == 1)).sum()))

def calibrate(index_dir, questions, out=None, embedder=None):
    R = Retriever(index_dir, embedder)
    qs, y, cats = load_questions(questions); s = top1_scores(R, qs)
    tau = choose_tau(s, y); pred = (s >= tau).astype(int); f, p, r = fbeta(y, pred)
    rep = dict(tau=tau, embedder=R.meta["embedder"], corpus_signature=R.meta["corpus_signature"], n_in=int(y.sum()), n_out=int((1 - y).sum()),
               auc=auc(s, y), in_median=float(np.median(s[y == 1])), out_median=float(np.median(s[y == 0])), out_max=float(s[y == 0].max()),
               in_min=float(s[y == 1].min()), train=dict(answer_precision=p, answer_recall=r, fbeta=f), cross_validated=cross_validated(s, y),
               missed_in_scope=[qs[i] for i in np.where((y == 1) & (pred == 0))[0]], wrongly_answered=[qs[i] for i in np.where((y == 0) & (pred == 1))[0]])
    warn = []
    if rep["auc"] < 0.9: warn.append("Low separation (AUC < 0.9): in-scope and out-of-scope scores overlap. Check the corpus and the embedder.")
    if rep["cross_validated"]["false_answers"] > 0: warn.append("Cross-validation answered some out-of-scope questions.")
    rep["warnings"] = warn
    if out: Path(out).write_text(json.dumps(rep, indent=1))
    return rep

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--index", default="rag/index"); ap.add_argument("--questions", default="rag/questions.csv")
    ap.add_argument("--out", default="rag/tau.json"); a = ap.parse_args()
    print(json.dumps(calibrate(a.index, a.questions, a.out), indent=1))
