"""Local embedders. Production = fastembed (ONNX, no PyTorch). HashEmbedder is for tests and offline emergencies only."""
import re, zlib
import numpy as np

class HashEmbedder:
    """Deterministic bag-of-words hashing embedder (L2-normalized). NOT semantic: used for tests and as a last-resort fallback."""
    name = "hash-512"
    def __init__(self, dim=512):
        self.dim = dim
    def embed(self, texts):
        out = np.zeros((len(texts), self.dim), dtype="float32")
        for i, t in enumerate(texts):
            toks = re.findall(r"[a-z0-9]+", t.lower())
            for a, b in zip(toks, toks[1:] + [""]):
                out[i, zlib.crc32(a.encode()) % self.dim] += 1.0
                if b: out[i, zlib.crc32((a + " " + b).encode()) % self.dim] += 0.5
        n = np.linalg.norm(out, axis=1, keepdims=True); n[n == 0] = 1
        return out / n

class FastEmbedder:
    """Semantic embedder via fastembed (downloads the model once on first use)."""
    def __init__(self, model="BAAI/bge-small-en-v1.5", batch=32):
        from fastembed import TextEmbedding           # lazy import: not needed for tests
        self.name, self.batch, self._m = model, batch, TextEmbedding(model_name=model)
    def embed(self, texts):
        v = np.array(list(self._m.embed(list(texts), batch_size=self.batch)), dtype="float32")
        n = np.linalg.norm(v, axis=1, keepdims=True); n[n == 0] = 1
        return v / n

def get_embedder(kind="fastembed", model="BAAI/bge-small-en-v1.5"):
    return HashEmbedder() if kind == "hash" else FastEmbedder(model)
