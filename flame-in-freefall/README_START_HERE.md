# Flame in Freefall: Quick Start Guide

## Windows / Mac / Linux Quick Start
1. Open a terminal inside the project folder (`flame-in-freefall` or repository root).
2. Check Python version: `python --version` (Python 3.10, 3.11, or 3.12; 3.11 recommended).
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt -r rag/requirements.txt "streamlit>=1.40" plotly psutil
   ```
4. First run & automated audit/tests:
   ```bash
   python scripts/setup_all.py --offline
   ```
   Open `SETUP_REPORT.md` to confirm all 27 test suites and gates pass.
5. Launch the dashboard:
   ```bash
   streamlit run app/streamlit_app.py
   ```
   *Or from repository root: `streamlit run flame-in-freefall/app/streamlit_app.py`*

## Deep-Space Comm Blackout Mode (100% Air-Gapped)
- The platform operates 100% offline out-of-the-box without requiring an OpenAI API key.
- Toggle **Simulate Deep-Space Comm Blackout** in the sidebar to activate the fast-failing Circuit Breaker and run extractive NASA passage retrieval locally via the onboard FAISS vector index (1,573 chunks).

## If You See an Error When Starting
1. Upgrade Streamlit: `pip install -U streamlit plotly`
2. Ensure you run from the folder containing `app/`, `backend/`, and `domain/`.
3. If using Docker: `docker-compose up --build`

## Core Directory Architecture
- `app/`: Streamlit interactive dashboard, NASA-STD-3001 styling, and 60 FPS Three.js volumetric ray-marching shader.
- `domain/`: Pure combustion physics ($Pe, Da, \alpha, Gr$) and Go/No-Go safety evaluation (zero external dependencies).
- `services/`: Application services, cryptographic SHA-256 audit, prompt injection sanitization, and Circuit Breaker.
- `backend/`: Gaussian Process ML regressor (p95 = 1.91 ms), 90% conformal uncertainty intervals, and convex hull envelope guard.
- `rag/`: Dense FAISS vector retrieval index (1,573 chunks), 101 NASA STI papers, and calibrated refusal gate ($\tau = 0.7455$).
- `insights/`: 18 verified NASA findings, 15 verified flight experiment catalog, 4 civilian Earth spin-offs, and 1-click report export.
- `docs/`: `PRD.md`, `ARCHITECTURE.md`, `DATA_CARD.md`, and `EVALUATION.md`.
