"""Guided verification of the evidence the dashboard shows.
  python scripts/verify_entries.py findings     # check each unverified finding against its source
  python scripts/verify_entries.py catalog      # check each unverified experiment-catalog entry"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from insights.verify import verify_findings, verify_catalog

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else ""
    {"findings": verify_findings, "catalog": verify_catalog}.get(which, lambda: sys.exit(__doc__))()
