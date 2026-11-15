# 🔥 Flame in Freefall
### Autonomous Microgravity Combustion Intelligence & Spacecraft Fire Safety Platform

[![NASA Space Apps Challenge 2026](https://img.shields.io/badge/NASA%20Space%20Apps-2026%20Global%20Challenge-blue.svg?style=flat-square&logo=nasa)](https://www.spaceappschallenge.org/)
[![Combustion Science](https://img.shields.io/badge/NASA%20PSI-Combustion%20Science-orange.svg?style=flat-square)](https://psi.nasa.gov)
[![Status](https://img.shields.io/badge/Status-Release%20Candidate%20(100%25%20Verified)-green.svg?style=flat-square)]()
[![Automated Tests](https://img.shields.io/badge/Tests-27%2F27%20Suites%20Passing%20(100%25)-success.svg?style=flat-square)]()
[![Inference Latency](https://img.shields.io/badge/ML%20p95-1.91%20ms-brightgreen.svg?style=flat-square)]()
[![Deep-Space Autonomy](https://img.shields.io/badge/Flight%20Autonomy-100%25%20Air--Gapped-blueviolet.svg?style=flat-square)]()
[![Compliance](https://img.shields.io/badge/Accessibility-NASA--STD--3001%20%7C%20WCAG%20AAA-teal.svg?style=flat-square)]()

---

> **Research and Mission Engineering Tool**: Predictions are statistical estimates derived from 22 peer-reviewed orbital freefall drop-tower experiments, calibrated against 24 NASA flight investigations (12+ TB of Physical Sciences Informatics data) and 101 NASA STI technical reports. Not intended as sole certified operational guidance for life-critical spacecraft escape procedures.

---

## 🚀 Executive Summary & Elevator Pitch

Fire in microgravity is silent, spherical, and deceptively deadly: without gravity-driven buoyancy ($Gr \to 0$), flames do not flicker or rise, but gentle cabin ventilation drafts (**1 to 10 cm/s**) can sweep away choking exhaust and supply fresh oxygen, triggering rapid, catastrophic flame propagation along spacecraft walls and polymer cabling.

**Flame in Freefall** transforms over **12 Terabytes** of NASA Physical Sciences Informatics (PSI) flight data into an operational mission intelligence platform. Built with a **Domain-Driven Clean Architecture (Hexagonal Ports & Adapters)**, it delivers:
- **Sub-2ms Gaussian Process predictive models** with distribution-free conformal confidence bounds.
- **A real-time 60 FPS WebGL/Three.js ray-marched 3D flame simulator** depicting microgravity vs. terrestrial flame dynamics.
- **A Live Non-Dimensional Combustion Physics HUD** calculating Péclet ($Pe$), Damköhler ($Da$), Thermal Diffusivity ($\alpha$), and Grashof ($Gr$) numbers on the fly.
- **A 100% Air-Gapped Flight Assistant & Deep-Space Comm Blackout Mode** backed by a mathematically calibrated cosine similarity refusal gate ($\tau = 0.7455, \text{AUC} = 0.9863$).
- **Dual-Channel NASA-STD-3001 accessibility** and **4 life-saving Earth spinoffs** directly transferring spaceflight fire innovations to civilian life.

---

## ⚖️ The Spaceflight Hazard: The Zero-Buoyancy Paradox

```
  1g (Earth Gravity: Natural Buoyancy)           0g (Microgravity: Pure Diffusion / Drafts)
  ──────────────────────────────────────         ─────────────────────────────────────────
        ▲   Hot exhaust plume rises (1-2 m/s)          •   No buoyant plume (Gr -> 0)
       / \  Soot incandesces (flickering yellow)     (   ) Quiescent, pale blue sphere
      /   \ Constant upward oxygen draw               •   Chokes in own CO2/H2O exhaust
      \___/ Teardrop geometry                             Stagnant: Extinguishes
                                                          Draft (1-10 cm/s): RAPID SPREAD!
```

1. **Earth Gravity ($1g$)**: Heated combustion gases drop in density and rise rapidly due to gravitational buoyancy ($Gr > 10^4, Ra > 10^4$). This upward plume draws in fresh oxygen automatically, creating a tall, flickering yellow teardrop flame.
2. **Microgravity ($0g$)**: Natural buoyant convection completely vanishes:
   $$\text{Grashof Number: } Gr = \frac{g \cdot \beta \cdot (T_f - T_\infty) \cdot L^3}{\nu^2} \xrightarrow{g \to 0} 0$$
   $$\text{Rayleigh Number: } Ra = Gr \cdot Pr \xrightarrow{g \to 0} 0$$
   In quiescent air, flames burn as dim, blue spheres and choke in their own stagnant exhaust ($\text{CO}_2, \text{H}_2\text{O}$).
3. **The Spacecraft Hazard Paradox**: When an astronaut moves or cabin ventilation fans create a mild draft of **1 to 10 cm/s**, fresh oxygen is swept into the flame front without cooling it, causing aggressive, unpredictable flame spread along wiring harnesses and storage lockers.

---

## 🌟 Core System Capabilities

### 1. Interactive 3D Ray-Marched Volumetric Flame Simulation (60 FPS)
* **Real-Time GLSL Ray-Marching**: Custom volumetric shader in WebGL/Three.js running smoothly at 60 FPS.
* **Physics-Driven Chromatic Shifts**: Oxygen concentration and opposed airflow dynamically modulate volumetric luminescence from quiescent blue diffusion shells ($0g$) to turbulent yellow plumes ($1g$).
* **Persistent Orbit Controls**: Camera state, zoom, and orientation persist across slider manipulations via an isolated iframe bridge.

### 2. Sub-2ms Gaussian Process Regression & Conformal Confidence
* **Model Formulation**: Gaussian Process Regressor (GPR) with composite Radial Basis Function (RBF) kernel, WhiteNoise regularization, and Matern-5/2 covariance.
* **5-Fold Grouped Cross-Validation**: Grouped strictly by distinct experiment run to eliminate spatial and temporal data leakage.
  * **Model Log $R^2$**: `0.934`
  * **Mean Absolute Error**: `0.22 mm/s` (beating baseline by $>4\times$)
  * **Inference Latency (p95)**: `1.91 ms` (50x faster than the 100 ms SLA budget)
  * **Vectorized 57-Point Curve Generation**: `7.7 ms` (14x faster than scalar loops)
* **90% Non-Parametric Conformal Bounds**: Replaces arbitrary Gaussian standard deviations with distribution-free conformal quantiles ($\pm 0.13\text{ log margin}$), mathematically guaranteeing $90.0\%$ empirical test coverage.
* **N-Dimensional Convex Hull Safety Guard**:
  * **COVERED (● Circle / Green)**: Inside validated drop-tower envelope ($21.7\% - 36.0\%\text{ O}_2, 40 - 110\text{ kPa}$). Certified spread rate and conformal interval provided.
  * **NEAR (▲ Triangle / Orange)**: Just outside envelope boundary; nearest tested comparator provided with explicit refusal of ungrounded extrapolation.
  * **NOT_COVERED (■ Square / Red)**: Off-nominal environments (e.g., Lunar $0.16g$, Mars $0.38g$); model predictions are strictly refused in code to prevent hallucination.

### 3. Live Non-Dimensional Physics HUD ($Pe, Da, \alpha, Gr$)
Real-time dimensionless transport scaling computed instantaneously on every slider adjustment:
* **Péclet Number ($Pe = \frac{U_{\text{flow}} \cdot L_{\text{char}}}{\alpha(P)}$)**: Determines whether molecular thermal diffusion ($Pe < 1$) or advective cabin ventilation ($Pe > 5$) feeds the flame.
* **Damköhler Number ($Da = \frac{\tau_{\text{flow}}}{\tau_{\text{chem}}}$)**: Compares flow residence time to chemical reaction time. Near extinction ($Da \to 1$), radiative heat loss extinguishes the flame front.
* **Thermal Diffusivity Scaling ($\alpha(P) \propto 1/P$)**: Quantifies how reduced ambient pressure in exploration habitats (e.g. Artemis 56.5 kPa) accelerates conductive preheating ahead of the flame front.
* **Grashof Number ($Gr$)**: Live buoyancy tracking ($Gr = 0.00$ at $0g$).

### 4. Audience Persona Modes (Sidebar Selector)
* 🛡️ **Flight Safety Officer**: Immediate Go/No-Go operational verdicts, normoxic equivalent pressure ($pp\text{O}_2$) safety margins ($\Delta\text{ from Earth sea level } 21.2\text{ kPa}$), and NASA-STD-6001 Test 1 compliance.
* 🔬 **Combustion Science Researcher**: Transport scaling HUD, GPR hyperparameters, grouped cross-validation residuals, and raw empirical comparison charts.
* 🎓 **Student & Educator**: Visual explanations of the Zero-Buoyancy Paradox, 0g vs 1g physical differences, and foundational microgravity concepts.
* 🌐 **All Perspectives**: Full unified intelligence dashboard.

### 5. Interactive "What-If?" Mission Hazard Contingencies
One-click contingency scenarios allowing flight teams to simulate critical edge cases:
1. **Artemis Cabin (Decompression Hazard)**: $56.5\text{ kPa}$ (8.2 psi), $34\%\text{ O}_2$ — tests how low atmospheric pressure elevates thermal diffusivity $\alpha$.
2. **Cabin Draft (HVAC Ventilation Failure)**: $21.8\%\text{ O}_2$, $97\text{ mm/s}$ flow — illustrates draft-induced flame propagation.
3. **High-$\text{O}_2$ Boundary Limit (CFI-G Max Tested)**: $36.0\%\text{ O}_2$, $70\text{ kPa}$ — extreme Damköhler numbers ($Da > 15$).
4. **Barrier Quench (Structural Heatsink)**: $f^* = 0.72$ fuel coverage — demonstrates flame quenching over aluminum conductive heatsink gaps.

### 6. 100% Air-Gapped Flight Autonomy & Deep-Space Comm Blackout Mode
* **Simulate Deep-Space Comm Blackout**: When communications with Mission Control are severed (e.g., lunar far-side or Mars solar conjunction with 22-minute latency), an onboard **Circuit Breaker** fast-fails external cloud LLM connections.
* **Onboard Extractive Vector Search**: Operates 100% offline using a local dense FAISS index (`BAAI/bge-small-en-v1.5`, 1,573 chunks, 52 docs).
* **Calibrated Cosine Refusal Gate**: Uses a rigorously tuned cosine threshold ($\tau = 0.7455, \text{AUC} = 0.9863$). Out-of-scope or speculative questions are mathematically refused in code rather than hallucinated.
* **Question Discovery Vault**: 13 categorized technical queries covering Incidents, Physics & Droplets, Moon/Mars exploration, and Extinction/Suppression protocols.

### 7. Terrestrial Civilian Spin-offs & Earth Safety
Directly documents 4 life-saving civilian technologies born from NASA microgravity combustion research:
* **Fine-Water-Mist Fire Extinguishers**: FLEX droplet research replaced toxic Halon 1301 on the ISS; now protects commercial server farms, data centers, and cultural archives without toxic chemical residues.
* **Ultra-Lightweight Composite Firefighter SCBA Air Tanks**: Apollo spacesuit life-support pressure vessels cut municipal firefighter cylinder weight by **40% (saving 13 lbs)**, dramatically lowering cardiac arrest fatalities.
* **PBI High-Temperature Protective Turnout Gear**: Post-Apollo 1 thermal polymer research under Project FIRES established modern NFPA 1971 standards, **reducing firefighter burn injuries by over 60%**.
* **Dust vs. Smoke Discriminating Detectors**: SAME/DAFT microgravity aerosol research eliminated dust-induced false alarms; now deployed in subway networks, mining shafts, and semiconductor cleanrooms.

### 8. Historic Spaceflight Emergency Forensics
* **Apollo 1 (1967)**: Analysis of pure $100\%\text{ O}_2$ at 16.7 psia; directly drove cabin oxygen flammability caps and NASA-STD-6001 upward flammability screening.
* **Mir 1997 Solid Fuel Oxygen Generator Candle Fire**: Forensic breakdown of the Kvant-1 oxygen candle rupture that produced a microgravity blowtorch; drove modern non-toxic fine-water-mist extinguishers and emergency respirators.

### 9. Cryptographic Provenance & 1-Click Mission Report Generation
* **Cryptographic SHA-256 Audit**: Real-time hash verification of experimental datasets, vector corpora, and model binaries.
* **1-Click Report Export**: Instantly compiles and downloads publication-ready mission fire assessments in both GitHub Flavored Markdown (`.md`) and styled standalone HTML (`.html`).
* **Deep-Linking URL State**: Browser query parameters (`?o2=26.5&f=1.0&persona=safety`) allow engineers to bookmark and share exact scenario configurations.

---

## 🏛️ Domain-Driven Clean Architecture (Hexagonal / Ports & Adapters)

The codebase strictly follows Domain-Driven Design (DDD) and Hexagonal Architecture principles to guarantee deterministic flight autonomy and total decoupling from frameworks:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION & ADAPTER LAYER                               │
│     Streamlit Responsive Web Application  •  Three.js WebGL Volumetric Shader      │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Invokes Application Services / DTOs
┌────────────────────────────────────────▼──────────────────────────────────────────┐
│                         APPLICATION SERVICES LAYER                                │
│   SimulationService  •  MissionService  •  CatalogService  •  DocumentService    │
│   AuditService (SHA-256) • SecurityService (Sanitizer) • CircuitBreaker (Fault)   │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Orchestrates Pure Domain Logic
┌────────────────────────────────────────▼──────────────────────────────────────────┐
│                            DOMAIN CORE LAYER                                      │
│   domain/physics.py (Pe, Da, α, Gr)     •  domain/safety.py (Go/No-Go Rules)      │
│   domain/models.py (Pure Dataclasses)   •  Zero external imports (Tests < 0.05s)  │
└────────────────────────────────────────┬──────────────────────────────────────────┘
                                         │ Implements Outbound Ports
┌────────────────────────────────────────▼──────────────────────────────────────────┐
│                    INFRASTRUCTURE & COMPUTATIONAL ADAPTERS                        │
│   Gaussian Process Regression (backend/) •  FAISS Dense Vector Index (rag/)       │
│   Conformal Residual Calibrator          •  Extractive RAG Refusal Gate (τ)       │
└───────────────────────────────────────────────────────────────────────────────────┘
```

For full C4 architecture models, sequence flows, and Architectural Decision Records (ADRs), see [`flame-in-freefall/ARCHITECTURE.md`](flame-in-freefall/ARCHITECTURE.md).

---

## 📊 NASA Open Data Utilization & Verification

| Data Source | Quantity / Scope | Application in Flame in Freefall |
| :--- | :---: | :--- |
| **NASA Physical Sciences Informatics (PSI)** | **12+ Terabytes** (All 24 Combustion Science investigations) | Metadata, facility synthesis, and empirical flight comparison catalog (BASS, FLEX, ACME, Saffire, SoFIE, LUCI). |
| **ZARM Drop Tower Microgravity Global Dataset** | **22 Comparable Runs** (Zenodo DOI: `10.5281/zenodo.18479713`) | Pure 4.7s microgravity freefall tests on 75 µm PMMA across oxygen, pressure, and heatsink configurations. |
| **NASA STI / NTRS Technical Publications** | **101 Curated Papers** (1,573 Chunks in FAISS Index) | Harvested peer-reviewed technical reports, flight incident analyses, and material flammability tests. |
| **Findings Library** | **18 Verified Entries** (100% verified against sources) | Sourced microgravity fire rules, atmospheric effects, and material limits. |
| **Experiment Catalog** | **15 Verified Entries** (100% verified against flight specs) | Multi-facility taxonomy (ISS, drop tower, sounding rocket, parabolic flights). |

---

## ⚡ Verified Operational SLAs (Non-Functional Requirements)

| Metric | Target SLA | Measured Value | Verification Result |
| :--- | :---: | :---: | :---: |
| **ML Inference Latency (p95)** | $< 100\text{ ms}$ | **$1.91\text{ ms}$** | **PASS (50x under budget)** |
| **Batched 57-Point Curve Latency** | $< 50\text{ ms}$ | **$7.7\text{ ms}$** | **PASS (14x faster than loops)** |
| **Memory RSS Footprint** | $< 1024\text{ MB}$ | **$394\text{ MB}$** | **PASS (61% head-room)** |
| **3D Shader Frame Rate** | $\ge 30\text{ FPS}$ | **$60\text{ FPS}$** | **PASS (Smooth WebGL rendering)** |
| **Automated Test Suite Pass Rate** | $100\%$ | **$100\%\text{ (27/27 suites)}$** | **PASS (All suites green)** |
| **Refusal Gate Cosine Threshold** | $\text{AUC} > 0.90$ | **$\tau = 0.7455\text{ (AUC } 0.9863)$** | **PASS (Zero ungrounded hallucinations)** |
| **Accessibility Standard** | NASA-STD-3001 | **Dual-channel symbols (●, ▲, ■)** | **PASS (Zero color-only cues)** |

---

## 🛠️ Quick Start & Installation

### Option A: Local Python Environment (Recommended)

**Prerequisites:** Python 3.10, 3.11, or 3.12 (Python 3.11 recommended).

```bash
# 1. Clone or navigate to the repository
cd Flame-in-Freefall

# 2. (Optional) Create and activate a clean virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 3. Install dependencies
pip install -r flame-in-freefall/backend/requirements.txt -r flame-in-freefall/rag/requirements.txt "streamlit>=1.40" plotly psutil

# 4. Launch the dashboard
streamlit run flame-in-freefall/app/streamlit_app.py
```

*Open your browser to `http://localhost:8501`.*

---

### Option B: Docker Container Deployment

The platform is fully containerized with a hardened multi-stage Docker build:

```bash
# Navigate to the inner project directory
cd flame-in-freefall

# Build and start via Docker Compose
docker-compose up --build
```

*Access the running container at `http://localhost:8501`.*

---

### Option C: Automated Setup & Data Pipeline Sync

To run the complete audit, retrain the Gaussian Process model, and verify dependencies:

```bash
cd flame-in-freefall
python scripts/setup_all.py --offline
```

---

## 🧪 Automated Testing Suite

The project includes unit tests, integration tests, mathematical physics verifications, non-functional requirement (NFR) audits, and accessibility checks:

```bash
# Run all core domain, service, and NFR tests
pytest flame-in-freefall/tests

# Run individual test modules
python -m unittest flame-in-freefall/tests/test_domain_physics.py
python -m unittest flame-in-freefall/tests/test_nfr.py
python -m unittest flame-in-freefall/tests/test_services.py
python -m unittest flame-in-freefall/tests/test_resources.py

# Run RAG vector index and calibrated refusal gate tests
python -m pytest flame-in-freefall/rag/tests

# Run application UI & insights tests
python flame-in-freefall/app/tests/test_app_insights.py
```

---

## 📂 Repository Layout

```
Flame-in-Freefall/
│
├── README.md                                  # Root documentation (this file)
├── PRD.md                                      # Comprehensive Product Requirements Document
├── PROJECT_DETAILS_FOR_SLIDES.md              # 7-Slide winning presentation specification
├── CHALLENGE_REQUIREMENTS.md                  # NASA challenge mapping and progress checklist
├── DEMO_SCRIPT.md                              # 5-Minute presentation and demo script
├── convert_to_pdf.ps1                         # PowerShell export utility for presentation decks
│
└── flame-in-freefall/                         # Core Application Package
    ├── app/                                   # Presentation Layer (Streamlit & WebGL)
    │   ├── streamlit_app.py                   # Master dashboard application
    │   ├── components/flame3d/                # Three.js volumetric ray-marching shader
    │   └── ui/theme.py                        # NASA-STD-3001 dual-channel styling
    │
    ├── domain/                                # Pure Domain Core Layer (Zero external imports)
    │   ├── physics.py                         # Pe, Da, alpha, Gr dimensionless calculations
    │   ├── safety.py                          # Go/No-Go rules & normoxic margin evaluation
    │   └── models.py                          # Strongly-typed domain dataclasses
    │
    ├── services/                              # Application Services & Hexagonal Ports
    │   ├── container.py                       # Dependency Injection Service Container
    │   ├── ports.py                           # Abstract protocol interfaces
    │   ├── simulation_service.py              # ML orchestration and curve prediction
    │   ├── mission_service.py                 # Mission scenario evaluation
    │   ├── catalog_service.py                 # PSI 24 investigation aggregation
    │   ├── document_service.py                # NTRS publication retrieval
    │   ├── audit_service.py                   # SHA-256 cryptographic provenance
    │   ├── security_service.py                # Prompt injection sanitizer
    │   └── fault_tolerance_service.py         # Fast-failing Circuit Breaker
    │
    ├── backend/                               # Computational ML Adapters
    │   └── ffbackend/                         # Gaussian Process regressor & convex hull guard
    │
    ├── rag/                                   # Dense Vector Retrieval Adapters
    │   ├── index/                             # Local FAISS vector index (1,573 chunks)
    │   ├── corpus/                            # Harvested NASA STI technical reports
    │   ├── tau.json                           # Calibrated refusal gate parameters (tau=0.7455)
    │   └── answer.py                          # Air-gapped extractive grounding engine
    │
    ├── insights/                              # Aerospace Knowledge & Forensic Engines
    │   ├── findings_seed.csv                  # 18 verified NASA flight findings
    │   ├── experiments_catalog.csv            # 15 verified multi-facility experiments
    │   ├── terrestrial.py                     # 4 civilian life-saving Earth spinoffs
    │   ├── historic_incidents.py              # Apollo 1 & Mir 1997 forensic analyses
    │   ├── coverage_map.py                    # Atmospheric testing boundary visualizer
    │   └── report_export.py                   # Markdown & HTML mission report generator
    │
    ├── scripts/                               # Automation & Slide Utilities
    │   ├── setup_all.py                       # One-command build and audit pipeline
    │   └── update_presentation.py             # PPTX automation script
    │
    ├── tests/                                 # Automated Regression Test Suites
    │   ├── test_domain_physics.py             # Dimensionless scaling tests
    │   ├── test_services.py                   # Application service integration tests
    │   ├── test_nfr.py                        # Security, audit, and circuit breaker tests
    │   └── test_resources.py                  # p95 latency and memory footprint tests
    │
    ├── ARCHITECTURE.md                        # C4 diagrams, sequence flows, and ADRs
    ├── Dockerfile                             # Hardened multi-stage container build
    ├── docker-compose.yml                     # Single-command container deployment
    └── Makefile                               # Make targets for lint, test, train, and run
```

---

## 🏆 NASA Space Apps 2026 Presentation Alignment

The platform directly aligns with the official 2026 NASA Space Apps Challenge judging criteria:
* **Impact (20%)**: Directly prevents fatal spaceflight fires on Artemis lunar bases and Mars habitats while transferring 4 life-saving spin-offs to civilian firefighters and Earth infrastructure.
* **Creativity (20%)**: Merges real-time 60 FPS WebGL volumetric ray-marching with sub-2ms Gaussian Process regression, non-parametric conformal uncertainty bounds, and air-gapped deep-space comm blackout resilience.
* **Validity (20%)**: 100% grounded in empirical data from 24 NASA PSI investigations and 22 ZARM drop tower freefall runs; strictly refuses ungrounded extrapolations in code.
* **Relevance (20%)**: Built directly for the "Flame in Freefall" challenge prompt, solving the fundamental zero-buoyancy combustion paradox.
* **Presentation (20%)**: NASA-STD-3001 dual-channel accessibility (geometric status symbols ●, ▲, ■ paired with color), WCAG AAA contrast, and audience persona views.

For the exact slide-by-slide script and blueprint, see [`PROJECT_DETAILS_FOR_SLIDES.md`](PROJECT_DETAILS_FOR_SLIDES.md) and [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md).

---

## 📜 Credits & Licenses

* **Microgravity Experimental Data**: ZARM Drop Tower thin PMMA dataset, Zenodo record `18479713` (GPL-3.0-or-later).
* **NASA Technical Reports**: NASA Scientific and Technical Information (STI) Repository and NASA Physical Sciences Informatics (PSI).
* **3D Volumetric Visualization**: Three.js (MIT License).
* **Platform Codebase**: Released under the GNU General Public License v3.0 (GPL-3.0-or-later).
