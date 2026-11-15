"""Prediction contract (REQ-B1)."""
from dataclasses import dataclass, asdict
from typing import Optional
from .config import DISCLAIMER

STATUSES = ("IN", "SPARSE", "OUT", "DATA_ONLY")

@dataclass
class Prediction:
    rate: Optional[float] = None
    lo: Optional[float] = None
    hi: Optional[float] = None
    status: str = "OUT"
    message: str = ""
    disclaimer: str = DISCLAIMER

    def to_dict(self):
        assert self.status in STATUSES
        if self.status in ("OUT", "DATA_ONLY"):
            self.rate = self.lo = self.hi = None
        return asdict(self)
