"""Light-weight rate limiting (no heavy imports, so the dashboard can use it without faiss installed)."""
import json, time, datetime as dt
from pathlib import Path

class TokenBucket:
    """Per-session limiter: `rate` requests per minute."""
    def __init__(self, rate=10, now=time.monotonic):
        self.cap, self.tokens, self.now, self.t = float(rate), float(rate), now, now()
        self.refill = rate / 60.0
    def allow(self):
        n = self.now(); self.tokens = min(self.cap, self.tokens + (n - self.t) * self.refill); self.t = n
        if self.tokens >= 1: self.tokens -= 1; return True
        return False

class DailyCap:
    """Global LLM-call counter persisted in a small JSON file."""
    def __init__(self, path, cap, today=dt.date.today):
        self.path, self.cap, self.today = Path(path), cap, today
    def _read(self):
        try: d = json.loads(self.path.read_text())
        except Exception: d = {}
        return d if d.get("date") == str(self.today()) else {"date": str(self.today()), "count": 0}
    def available(self): return self._read()["count"] < self.cap
    def record(self):
        d = self._read(); d["count"] += 1; self.path.write_text(json.dumps(d))
