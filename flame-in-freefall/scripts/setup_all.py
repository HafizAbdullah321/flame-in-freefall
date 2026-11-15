"""One-command setup for Flame in Freefall. Run from the repo root (the folder containing app/, backend/, phase0/, rag/):

    python scripts/setup_all.py                 # everything, including the NASA harvest (needs internet)
    python scripts/setup_all.py --offline       # only the steps that need no internet
    python scripts/setup_all.py --per-query 5   # smaller first harvest (default 10)
    python scripts/setup_all.py --calibrate     # also calibrate the refusal threshold after indexing

Each step prints PASS / FAIL / SKIP. A report is written to SETUP_REPORT.md: send it to the assistant if anything fails."""
import argparse, json, subprocess, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
log = []

def run(name, cmd, cwd=ROOT, must=True, env=None):
    t0 = time.time(); print(f"\n=== {name}")
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, env=env)
    tail = (p.stdout + p.stderr).strip().splitlines()[-12:]
    ok = p.returncode == 0
    print("\n".join(tail)); print(f"--- {'PASS' if ok else 'FAIL'} ({time.time()-t0:.0f}s)")
    log.append(dict(step=name, status="PASS" if ok else "FAIL", tail="\n".join(tail)))
    if must and not ok:
        finish(); sys.exit(f"Stopped at: {name}. See SETUP_REPORT.md")
    return ok

def skip(name, why):
    print(f"\n=== {name}\n--- SKIP ({why})"); log.append(dict(step=name, status="SKIP", tail=why))

def finish():
    lines = ["# Setup report", ""] + [f"- **{l['status']}**: {l['step']}" for l in log] + ["", "## Details", ""]
    lines += [f"### {l['step']} ({l['status']})\n```\n{l['tail']}\n```" for l in log]
    extra = ROOT / "rag/index"
    if (extra / "index_meta.json").exists():
        lines += ["## Index", "```", (extra / "index_meta.json").read_text(encoding="utf-8", errors="replace"), "```"]
    if (extra / "excluded.csv").exists():
        lines += ["## Excluded documents", "```", (extra / "excluded.csv").read_text(encoding="utf-8", errors="replace")[:4000], "```"]
    (ROOT / "SETUP_REPORT.md").write_text("\n".join(lines), encoding="utf-8", errors="replace")
    print(f"\nReport written: {ROOT / 'SETUP_REPORT.md'}")

def online_ok():
    try:
        return urllib.request.urlopen("https://ntrs.nasa.gov/api/health", timeout=10).status == 200
    except Exception as e:
        print("NTRS not reachable:", e); return False

REQUIRED = ["backend/requirements.txt", "backend/ffbackend/predict.py", "phase0/phase0_audit.py", "phase0/raw",
            "rag/build_index.py", "rag/requirements.txt", "app/streamlit_app.py"]

def preflight():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        sys.exit("The project folders are not all in place.\nExpected next to the 'scripts' folder: app/, backend/, phase0/, rag/\n"
                 f"Looked in: {ROOT}\nMissing: {', '.join(missing)}\n"
                 "Fix: unzip flame-in-freefall.zip (it keeps the folder layout), then run this script from inside that folder.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true"); ap.add_argument("--skip-install", action="store_true")
    ap.add_argument("--per-query", type=int, default=10); ap.add_argument("--calibrate", action="store_true")
    a = ap.parse_args()
    if sys.version_info < (3, 10): sys.exit("Python 3.10 or newer is required.")
    preflight()
    # 1. dependencies
    if a.skip_install: skip("Install dependencies", "--skip-install")
    else:
        run("Install dependencies", [PY, "-m", "pip", "install", "-q", "-r", "backend/requirements.txt", "-r", "rag/requirements.txt", "streamlit>=1.40", "plotly", "psutil"])
    # 2. data audit + model (local data, no internet)
    run("Phase 0 data audit", [PY, "phase0_audit.py", "--raw", "raw", "--out", "out", "--min-exp", "15"], cwd=ROOT / "phase0")
    run("Train model", [PY, "-m", "ffbackend.train", "--phase0-out", "../phase0/out", "--artifacts", "artifacts", "--model-feats", "o2_pct", "fuel_coverage"], cwd=ROOT / "backend")
    run("Backend tests (synthetic)", [PY, "-m", "tests.test_backend"], cwd=ROOT / "backend")
    run("Backend tests (real data)", [PY, "-m", "tests.test_real"], cwd=ROOT / "backend")
    run("RAG index tests (fixture)", [PY, "-m", "rag.tests.test_rag_index"])
    run("RAG calibration tests (fixture)", [PY, "-m", "rag.tests.test_calibration"])
    run("Assistant tests (mock LLM)", [PY, "-m", "rag.tests.test_assistant"])
    run("Insights tests (findings, scenarios)", [PY, "-m", "insights.tests.test_insights"])
    run("Insights tests (coverage map)", [PY, "-m", "insights.tests.test_coverage_map"])
    run("Insights tests (experiment catalog)", [PY, "-m", "insights.tests.test_catalog"])
    run("Insights tests (risk cards)", [PY, "-m", "insights.tests.test_risk_cards"])
    run("Insights tests (topic synthesis)", [PY, "-m", "insights.tests.test_synthesis"])
    run("Insights tests (natural-language scenarios)", [PY, "-m", "insights.tests.test_nl_scenario"])
    run("Insights tests (AI brief verifier, mock LLM)", [PY, "-m", "insights.tests.test_si_brief"])
    run("Insights tests (verification tool)", [PY, "-m", "insights.tests.test_verify"])
    run("Insights tests (terrestrial spin-offs)", [PY, "-m", "insights.tests.test_terrestrial"])
    run("Insights tests (report export)", [PY, "-m", "insights.tests.test_report_export"])
    run("Insights tests (historic incidents)", [PY, "-m", "insights.tests.test_historic_incidents"])
    run("Insights tests (persona adapters)", [PY, "-m", "insights.tests.test_persona"])
    run("Domain layer tests (physics & safety)", [PY, "tests/test_domain_physics.py"])
    run("Application services tests", [PY, "tests/test_services.py"])
    run("Non-functional requirements tests (security, audit, circuit breaker)", [PY, "tests/test_nfr.py"])
    run("RAG summaries tests", [PY, "-m", "rag.tests.test_summaries"])
    run("App tests (AI brief flow, mock LLM)", [PY, "app/tests/test_app_insights.py"])
    run("App tests (natural-language scenarios)", [PY, "app/tests/test_app_nl_scenario.py"])
    run("App tests (documents and synthesis tab)", [PY, "app/tests/test_app_documents.py"])
    run("Resource tests (memory, latency)", [PY, "tests/test_resources.py"])
    # 3. NASA harvest + real index (internet)
    if a.offline:
        skip("NASA harvest", "--offline"); skip("Build index", "--offline"); skip("Calibrate", "--offline")
    else:
        if not online_ok():
            skip("NASA harvest", "ntrs.nasa.gov not reachable: check internet, VPN, or proxy")
            skip("Build index", "no corpus"); skip("Calibrate", "no index")
        else:
            run("NASA harvest", [PY, "-m", "rag.harvest_all", "--per-query", str(a.per_query)])
            run("Build index (downloads the embedding model on first run)", [PY, "-m", "rag.build_index", "--corpus", "rag/corpus", "--out", "rag/index"])
            if a.calibrate:
                run("Calibrate refusal threshold", [PY, "-m", "rag.calibrate", "--index", "rag/index", "--questions", "rag/questions.csv", "--out", "rag/tau.json"], must=False)
            else:
                skip("Calibrate", "run with --calibrate AFTER editing rag/questions.csv")
    finish()
    print("\nNext: streamlit run app/streamlit_app.py")

if __name__ == "__main__":
    main()
