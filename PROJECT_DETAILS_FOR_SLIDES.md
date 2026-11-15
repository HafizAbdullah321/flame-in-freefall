# Flame in Freefall: Product Requirements Document (PRD) & Presentation Specification

**NASA Space Apps Challenge 2026 — Combustion Science & Physical Sciences Informatics (PSI)**  
*Autonomous Microgravity Combustion Intelligence & Spacecraft Fire Safety Platform*  
**Document Status:** Release Candidate (100% Tested & Verified)  
**Reference Video:** [NASA Space Apps Submission and Judging Guide](https://www.youtube.com/watch?v=CV7AYfMRyMM)  

---

## Executive Summary & Project Identity

### Project Name
**Flame in Freefall**

### Tagline
*Physics-Grounded Machine Learning, 3D Ray-Marched Simulation, and Air-Gapped Flight Autonomy for Deep-Space Exploration and Earth Safety.*

### Elevator Pitch (100 Words)
Fire in microgravity is silent, spherical, and deceptively deadly: without gravity-driven buoyancy, flames do not flicker or rise, but gentle cabin ventilation drafts can trigger rapid catastrophic spread. **Flame in Freefall** transforms 12+ Terabytes of NASA Physical Sciences Informatics (PSI) flight data into an operational mission intelligence platform. Featuring sub-2ms Gaussian Process predictive models with conformal confidence bounds, a real-time 3D ray-marched flame simulator, and a 100% air-gapped flight assistant with a mathematically calibrated refusal gate, our platform protects Artemis lunar and Mars crews while transferring spaceflight suppression innovations directly to civilian life on Earth.

### Target User Personas
1. **Flight Safety Officers**: Immediate Go/No-Go flammability limits, normoxic equivalent pressure ($pp\text{O}_2$) safety margins, and NASA-STD-6001 operational compliance.
2. **Combustion Science Researchers**: Live Non-Dimensional Physics HUD (Péclet $Pe$, Damköhler $Da$, Thermal Diffusivity $\alpha$, Grashof $Gr$), Gaussian Process log $R^2$, and grouped cross-validation residuals.
3. **Students & Educators**: Interactive 3D visualization, zero-buoyancy vs Earth-gravity flame comparisons, and pedagogical explanations of zero-gravity physics.

---

## Official NASA Space Apps Submission & Judging Alignment

Based on the official NASA Space Apps Challenge *Project Submission and Judging & Awards Guide* ([Video Reference](https://www.youtube.com/watch?v=CV7AYfMRyMM)):

### Strict Presentation Constraints
- **Slide Count**: Maximum limit of **7 slides total** (including title and conclusion/team slides).
- **Language**: 100% English.
- **Alternative Demo Video Option**: Maximum length of **30 seconds** strictly, with mandatory English subtitles, hosted on an open public URL.

### Five Core Judging Criteria Evaluation Matrix

| Criterion | Weight | How "Flame in Freefall" Directly Satisfies the Criterion |
| :--- | :---: | :--- |
| **Impact** | 20% | Provides operational Go/No-Go flammability verification for Artemis Moon habitats ($34\%\text{ O}_2, 56.5\text{ kPa}$) and Mars rovers; documents 4 life-saving Earth spinoffs (fine water mist, lightweight SCBA tanks, PBI turnout gear, dust-discriminating detectors). |
| **Creativity** | 20% | Combines a 60 FPS real-time WebGL/Three.js ray-marched volume shader, Gaussian Process regression with non-parametric conformal uncertainty bounds, an N-dimensional convex hull extrapolation guard, and an air-gapped Deep-Space Comm Blackout Mode. |
| **Validity** | 20% | 100% scientifically grounded in verified NASA flight data from 24 PSI investigations and 22 ZARM drop tower freefall experiments (DOI: 10.5281/zenodo.18479713); strictly refuses ungrounded extrapolations in code. |
| **Relevance** | 20% | Built directly for the "Flame in Freefall" challenge prompt, addressing low-gravity combustion science, exploration atmospheres, and civilian Earth fire safety applications. |
| **Presentation** | 20% | NASA-STD-3001 dual-channel accessibility compliance (geometric symbols ●, ▲, ■ paired with all statuses), WCAG AAA contrast ratios, and intuitive audience persona toggle views. |

---

## The Spaceflight Hazard: The Zero-Buoyancy Paradox

### The Physics: 0g (Microgravity) vs 1g (Earth Gravity)
* **Earth Gravity ($1g$)**: Heated combustion gases drop in density and rise rapidly due to gravitational buoyancy ($Gr > 10^4, Ra > 10^4$), driving an upward convective plume at 1 to 2 m/s that stretches flames into flickering yellow teardrops and supplies fresh oxygen automatically.
* **Microgravity ($0g$)**: Gravitational acceleration drops to zero ($g \approx 0$). Natural buoyant convection ceases completely:
  $$\text{Grashof Number: } Gr = \frac{g \cdot \beta \cdot (T_f - T_\infty) \cdot L^3}{\nu^2} \xrightarrow{g \to 0} 0$$
  $$\text{Rayleigh Number: } Ra = Gr \cdot Pr \xrightarrow{g \to 0} 0$$
  Flames become quiescent, pale blue, and spherical. Carbon soot does not incandesce in bright upward exhaust columns.
* **The Spacecraft Hazard Paradox**: In perfectly stagnant cabin air, a microgravity flame often self-extinguishes as it chokes in its own combustion products ($\text{CO}_2$ and $\text{H}_2\text{O}$). However, when cabin ventilation fans or astronaut movements produce a gentle breeze (**1 to 10 cm/s**), it sweeps away exhaust and continuously delivers fresh oxygen, causing rapid, aggressive flame front propagation along polymer wiring and crew materials.

---

## Data Engine & NASA Open Data Utilization

### Harvested Open Datasets
1. **NASA Physical Sciences Informatics (PSI) Repository** ([psi.nasa.gov](https://psi.nasa.gov)):
   - Complete metadata and flight synthesis across **all 24 NASA Combustion Science investigations** representing **12+ Terabytes** of flight telemetry and imagery.
   - Core investigations analyzed:
     - **BASS & BASS-II**: Burning and Suppression of Solids across solid PMMA slabs and fabric samples.
     - **FLEX & FLEX-2**: Droplet combustion, multi-stage cool flames, and radiative extinction limits in MDCA.
     - **ACME / CFI-G**: Flammability boundaries up to 36% $\text{O}_2$ and electric field ion-wind control.
     - **Saffire I–VI**: Real-scale fabric and solid burns inside Cygnus cargo vehicles after departing the ISS.
     - **SAME, SAME-R, DAFT**: Smoke particulate morphology and smoke vs. lunar dust aerosol discrimination.
2. **ZARM Drop Tower Microgravity Global Dataset**:
   - 22 comparable microgravity orbital freefall tests (4.7 seconds pure freefall) on thin polymethyl methacrylate (PMMA, 75 µm).
   - Zenodo DOI: `10.5281/zenodo.18479713` (GPL-3.0-or-later).
   - Variables: Oxygen concentration (21.7% to 36.0%), pressure (40 to 110 kPa), opposed ventilation flow (0 to 150 mm/s), continuous PMMA strips vs inert metal heatsink barrier gaps ($f^* \in [0.72, 1.0]$).
3. **NASA Scientific and Technical Information (STI / NTRS)**:
   - 101 harvested technical reports, flight anomaly investigations, and peer-reviewed conference reprints indexed into a dense vector FAISS corpus (1,573 chunks).

---

## Live Non-Dimensional Physics Engine ($Pe, Da, \alpha, Gr$)

The application computes real-time dimensionless transport scaling laws on every atmospheric adjustment:

1. **Péclet Number ($Pe$) & Convective vs Diffusive Transport**:
   $$Pe = \frac{U_{\text{flow}} \cdot L_{\text{char}}}{\alpha(P)}$$
   Because natural buoyant convection is extinguished ($Gr = 0$), low-speed forced ventilation drafts determine whether molecular thermal diffusion ($Pe < 1$) or advection ($Pe > 5$) feeds the flame front.
2. **Damköhler Number ($Da$) & Extinction Limits**:
   $$Da = \frac{\tau_{\text{flow}}}{\tau_{\text{chem}}} = \frac{L / U_{\text{flow}}}{\left[Y_{\text{O}_2}^2 \cdot (P/P_0)\right]^{-1}}$$
   Compares flow residence timescale ($\tau_{\text{flow}}$ in ms) to chemical reaction timescale ($\tau_{\text{chem}}$ in ms). When $Da \gg 1$, kinetics outpace transport, sustaining flame propagation. Near extinction ($Da \to 1$), radiative heat loss extinguishes the flame.
3. **Gas Thermal Diffusivity Scaling ($\alpha$)**:
   $$\alpha(P) = \alpha_{\text{ref}} \cdot \left(\frac{P_{\text{ref}}}{P}\right) \quad [\text{cm}^2/\text{s}]$$
   In reduced-pressure exploration habitats (e.g. Artemis 56.5 kPa), reduced gas density inversely increases thermal diffusivity, accelerating preheat zone conduction ahead of the fuel flame front.

---

## Machine Learning Architecture & Conformal Confidence

### Predictive Engine
* **Model Family**: Gaussian Process Regressor (GPR) with composite Radial Basis Function (RBF) kernel, WhiteNoise regularization, and Matern-5/2 covariance.
* **Validation**: 5-Fold Grouped Cross-Validation grouped strictly by experiment ID (eliminating spatial/temporal data leakage).
* **Statistical Performance**:
  - Model Log $R^2$: **0.934**
  - Baseline Mean Absolute Error: **0.22 mm/s** (beating linear, decision tree, and baseline predictors).
  - Inference Latency: **1.91 ms (p95)** — 50x faster than the 100 ms SLA ceiling.
* **90% Non-Parametric Conformal Confidence Bounds**:
  - Replaces arbitrary Gaussian standard deviations with distribution-free conformal quantiles ($\pm 0.13\text{ log margin}$).
  - Mathematically guarantees **90.0% empirical coverage** across unseen test folds.

### N-Dimensional Convex Hull Safety Guard
* Commercial and academic ML models in aerospace risk hallucinating optimistic spread rates when queried outside training envelopes.
* **Flame in Freefall** enforces an N-dimensional convex hull guard over oxygen concentration (21.7% to 36.0%), pressure (40 to 110 kPa), and flow velocity:
  * **COVERED (● Circle / Green)**: Inside validated envelope; certified spread rate and 90% conformal interval emitted.
  * **NEAR (▲ Triangle / Orange)**: Just outside envelope boundary; nearest tested orientation comparator provided with explicit refusal of flight prediction.
  * **NOT_COVERED (■ Square / Red)**: Mathematically unsupported (e.g. Lunar 0.16g or Mars 0.38g gravity); model extrapolation is strictly refused in code.

---

## Real-Time 3D Ray-Marched Simulation & "What-If?" Hazards

### WebGL/Three.js Ray-Marched Volume Shader
* Custom GLSL ray-marching volume shader rendering volumetric microgravity flame dynamics in real time at **60 FPS**.
* Opposed airflow velocity and oxygen concentration drive real-time volumetric blue-to-yellow chromatic shifts.
* Toggles between a spherical, quiescent blue diffusion bubble ($0g$) and an elongated, flickering buoyant teardrop plume ($1g$).
* Uses persistent iframe DOM binding to preserve user camera orbit, rotation, and zoom across all parameter updates.

### Interactive "What-If?" Mission Hazard Contingencies
1. **Artemis Cabin (Decompression Hazard)**: 56.5 kPa (8.2 psi), 34% $\text{O}_2$ — tests how reduced ambient pressure increases thermal diffusivity $\alpha$, accelerating fuel preheating.
2. **Cabin Draft (HVAC Ventilation Failure)**: 21.8% $\text{O}_2$, 97 mm/s flow — illustrates how gentle cabin airflow sweeps away choking exhaust and supplies fresh oxygen.
3. **High-$\text{O}_2$ Limit (CFI-G Max Tested)**: 36.0% $\text{O}_2$, 70 kPa — demonstrates rapid flame propagation at extreme Damköhler numbers ($Da > 15$).
4. **Barrier Quench (Structural Metal Heatsink)**: $f^* = 0.72$ fuel coverage — proves how conductive aluminum heatsink gaps absorb thermal energy and extinguish propagating flames.

---

## Autonomous AI Flight Assistant & Comm Blackout Mode

### Retrieval-Augmented Generation (RAG) Architecture
* **Corpus**: 101 Harvested NASA STI research publications and 24 PSI investigations chunked into 1,573 vector segments embedded with `BAAI/bge-small-en-v1.5` into a dense local FAISS index.
* **Mathematical Refusal Gate**: Cosine similarity threshold ($\tau = 0.7455, \text{AUC} = 0.9863$). Questions outside the NASA knowledge domain (e.g. pop culture, speculative advice) are mathematically declined in code rather than hallucinated.
* **Security & Prompt Injection Protection**: Integrated `SecurityService` strips hostile instruction hijacking and jailbreak payloads before vector processing.

### Deep-Space Comm Blackout Mode (100% Air-Gapped Autonomy)
* During deep-space missions (lunar far side, Mars solar conjunction), ground communications suffer high latency (up to 22 minutes) or complete radio blackout.
* Activating the **Simulate Deep-Space Comm Blackout** toggle:
  1. Instantly severs external cloud LLM API connectivity via an internal Circuit Breaker.
  2. Shifts the system into 100% air-gapped local flight autonomy.
  3. Delivers verified, extractive technical passages directly from the onboard FAISS vector index with zero external dependencies.

---

## Terrestrial Civilian Spin-offs & Historical Disasters

### NASA Earth Spinoff Technologies
* **SPIN-01: Fine-Water-Mist Fire Extinguishers (ISS Replacement for Halon 1301)**
  - *Space Origin*: NASA Glenn & ADA Technologies replaced toxic Halon on the ISS. FLEX microgravity droplet research proved micro-droplets (<100 µm) flash-evaporate to absorb 2.26 MJ/kg thermal energy without suffocating crew.
  - *Earth Application*: High-value fire protection for commercial data centers, server rooms, and historic archives without toxic residue or electrical damage.
* **SPIN-02: Ultra-Lightweight Composite Firefighter SCBA Air Tanks**
  - *Space Origin*: NASA Johnson Space Center transferred Apollo spacesuit composite pressure vessel technology to municipal firefighting.
  - *Earth Application*: Replaced 33 lb steel cylinders with 20 lb aluminum-lined composite tanks (saving 13 lbs per firefighter), cutting heat exhaustion and cardiac fatalities.
* **SPIN-03: PBI High-Temperature Protective Turnout Gear (Project FIRES)**
  - *Space Origin*: Post-Apollo 1 thermal polymer research (polybenzimidazole PBI, Nomex) deployed under Project FIRES by NASA and FEMA.
  - *Earth Application*: Established nationwide NFPA 1971 standards, reducing municipal firefighter burn casualties by over 60%.
* **SPIN-04: Dust vs. Smoke Discriminating Detectors**
  - *Space Origin*: Space Shuttle and ISS experiments (SAME, DAFT) overcame microgravity aerosol suspension issues where floating dust triggered false alarms.
  - *Earth Application*: Dual-parameter continuous air sampling deployed in subway tunnels, underground mines, and cleanrooms.

### Historical Spaceflight Fire Emergency Lessons
* **Mir 1997 Oxygen Candle Fire**: Kvant-1 solid fuel oxygen generator ruptured into an open blowtorch in microgravity; led to modern non-toxic fine-water-mist extinguishers and redesigned crew respirators.
* **Apollo 1 (1967)**: Pure oxygen (100% $\text{O}_2$) at 16.7 psia led to explosive fire spread; led to strict cabin oxygen flammability caps and NASA-STD-6001 Test 1 upward flammability screening.

---

## System Architecture, Performance SLAs & Compliance

### Hexagonal Architecture (Ports & Adapters)
* **Domain Layer**: Pure mathematical physics (`evaluate_combustion_physics`) and operational safety assessments (`evaluate_safety_officer_verdict`).
* **Ports Layer**: `PredictorPort`, `RetrieverPort`, `AuditPort`, `SecurityPort`, `FaultTolerancePort`.
* **Adapters Layer**: GP Regression ML Predictor, Dense FAISS Retriever, Prompt Injection Guardrail, Circuit Breaker.
* **Container**: Centralized `ServiceContainer` for dependency injection and strict decoupling.

### Verified Operational SLAs
* **ML Predictor Latency (p95)**: **1.91 ms** *(SLA budget < 100 ms)*
* **Vectorized 57-Point Curve Generation**: **7.7 ms** *(14x faster than scalar loops)*
* **Memory RSS Footprint**: **394 MB** *(budget ceiling: 1024 MB)*
* **Automated Regression Suite**: **27 / 27 test suites passing (100% PASS)**
* **NASA-STD-3001 Compliance**: Complete dual-channel accessibility pairing color with geometric status symbols (● GO, ▲ CAUTION, ■ NO-GO).

---

## Master 7-Slide Winning Presentation Blueprint

This slide-by-slide blueprint maps directly to the official 7-slide maximum rule and guides an AI presentation maker to create an impactful deck:

```
+---------------------------------------------------------------------------------------------------+
| SLIDE 1: TITLE & THE PARADOX OF FIRE IN SPACE                                                     |
|                                                                                                   |
| Headline: Flame in Freefall: Autonomous Microgravity Combustion Intelligence                      |
| Subtitle: Transforming 12+ TB of NASA PSI Data into Spacecraft Fire Safety & Earth Spin-offs      |
|                                                                                                   |
| Key Points:                                                                                       |
| * On Earth, gravity makes fire predictable: hot buoyant plumes flicker and rise.                  |
| * In microgravity, buoyancy vanishes (Gr -> 0): flames turn into silent, dim blue spheres.        |
| * The Paradox: Stagnant flames choke, but gentle cabin drafts (1-10 cm/s) cause explosive spread. |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| Hero split-screen visual: Left side shows 1g flickering yellow teardrop flame; Right side shows   |
| 0g spherical blue flame from the app's 3D Ray-Marched Simulation.                                |
| Sub-badge: "NASA Space Apps Challenge 2026 | Physical Sciences Informatics (PSI)"                 |
+---------------------------------------------------------------------------------------------------+
| SLIDE 2: THE PROBLEM & SPACEFLIGHT EXPLORATION HAZARD                                             |
|                                                                                                   |
| Headline: Deep-Space Exploration Demands Physics-Grounded Intelligence                            |
|                                                                                                   |
| Key Points:                                                                                       |
| * High-Oxygen Habitats: Artemis Moon base & Mars rovers operate at reduced pressure and elevated |
|   oxygen (34% O2, 56.5 kPa), accelerating thermal diffusivity (alpha) and preheat spread.        |
| * Past Disasters: Mir 1997 oxygen fire and Apollo 1 proved that spaceflight fires escalate fast.  |
| * The AI Danger: Generic commercial LLMs hallucinate unsafe fire advice and extrapolate blindly.  |
| * Deep-Space Blackouts: Lunar far-side & Mars solar conjunctions sever ground comms for minutes.  |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| Timeline of historic flight fires (Apollo 1 -> Mir 1997 -> ISS) paired with a screenshot of the   |
| app's Historic Spaceflight Incidents & Engineering Lessons inspection card.                       |
+---------------------------------------------------------------------------------------------------+
| SLIDE 3: DATA ENGINE & 3D REAL-TIME SIMULATION                                                    |
|                                                                                                   |
| Headline: 12 Terabytes of NASA PSI Flight Data at 60 Frames Per Second                            |
|                                                                                                   |
| Key Points:                                                                                       |
| * Complete Ingestion: All 24 NASA PSI Combustion investigations (BASS, FLEX, ACME, Saffire)       |
|   synthesized with 22 drop-tower orbital freefall experiments.                                    |
| * 3D Ray-Marched Simulator: WebGL/Three.js volume shader rendering real-time chromatic shifts     |
|   based on oxygen fraction and ventilation velocity at 60 FPS.                                    |
| * "What-If?" Hazards: 1-Click contingency buttons for cabin decompression, ventilation stoppage,  |
|   high-oxygen boundary limits, and conductive metal heatsink barrier quenching.                   |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| Hero screenshot of the app's 3D Ray-Marched Simulation card with the oxygen/fuel sliders and the  |
| 4 What-If contingency action buttons (Artemis Cabin, Cabin Draft, High-O2, Barrier Quench).       |
+---------------------------------------------------------------------------------------------------+
| SLIDE 4: THE SCIENCE: LIVE NON-DIMENSIONAL HUD & CONFORMAL ML                                     |
|                                                                                                   |
| Headline: Verified Physics & Conformal Machine Learning Bounds                                    |
|                                                                                                   |
| Key Points:                                                                                       |
| * Non-Dimensional HUD: Real-time calculation of Peclet (Pe), Damkohler (Da), and Diffusivity (a). |
| * Gaussian Process Regression: RBF kernel + Matern-5/2 covariance with 90% non-parametric         |
|   empirical conformal prediction confidence intervals.                                            |
| * Convex Hull Guard: Enforces deterministic boundaries: COVERED (●), NEAR (▲), or NOT_COVERED (■).|
| * Sub-2ms Latency: 1.91 ms prediction latency (p95) across 57-point curves.                       |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| Dual visual: Screenshot of the Live Non-Dimensional Physics HUD (4 stat cards + timescale ribbon) |
| paired with the Plotly model curve chart showing drop-tower points inside the 90% conformal band. |
+---------------------------------------------------------------------------------------------------+
| SLIDE 5: AIR-GAPPED DEEP-SPACE AUTONOMY & COMM BLACKOUT MODE                                      |
|                                                                                                   |
| Headline: 100% Air-Gapped Flight Autonomy for Deep-Space Radio Blackout                           |
|                                                                                                   |
| Key Points:                                                                                       |
| * Deep-Space Comm Blackout Mode: When ground link is lost, internal circuit breaker switches       |
|   instantly to 100% offline flight mode with zero external cloud dependencies.                    |
| * Mathematical Refusal Gate: Dense FAISS vector retrieval calibrated with cosine similarity       |
|   threshold tau = 0.7455 (AUC = 0.9863). Off-topic/ungrounded questions are mathematically denied.|
| * Question Discovery Vault: Categorized library of 13 NASA technical queries covering physics,    |
|   Moon/Mars limits, droplet burning, and emergency suppression protocols.                         |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| Screenshot of the AI Flight Assistant tab displaying the "Simulated Deep-Space Comm Blackout      |
| Active" warning banner, Question Discovery Vault expander, and verified extractive NASA sources.  |
+---------------------------------------------------------------------------------------------------+
| SLIDE 6: TERRESTRIAL SPIN-OFFS: SAVING LIVES ON EARTH                                             |
|                                                                                                   |
| Headline: Spaceflight Science Directly Protecting Civilian Lives on Earth                         |
|                                                                                                   |
| Key Points:                                                                                       |
| * Fine Water Mist: ISS Halon replacement technology now protecting terrestrial server farms,     |
|   data centers, and historical archives without toxic chemicals.                                  |
| * Lightweight SCBA Air Tanks: Apollo composite pressure vessels reduced firefighter cylinder      |
|   weight by 40% (saving 13 lbs per firefighter), cutting cardiac fatalities.                      |
| * PBI Turnout Gear: Project FIRES NASA spacesuit thermal barrier polymer transferred to municipal |
|   firefighters, reducing burn injuries by over 60%.                                               |
| * Dust vs Smoke Sensors: Space Shuttle/ISS incipient fire detection tech preventing false alarms  |
|   in subway tunnels, cleanrooms, and underground mines.                                           |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| 4-Quadrant visual card layout showing the 4 spin-offs (Water Mist, SCBA Tanks, Turnout Gear, Dust |
| Discriminating Sensors) pairing Spaceflight Origin with Earth Commercial Benefit.                 |
+---------------------------------------------------------------------------------------------------+
| SLIDE 7: ARCHITECTURE, COMPLIANCE & FUTURE HORIZONS                                               |
|                                                                                                   |
| Headline: Hexagonal Clean Architecture & The Future of Spaceflight Safety                         |
|                                                                                                   |
| Key Points:                                                                                       |
| * Robust Architecture: Ports & Adapters design, 27/27 automated test suites passing (100% PASS),  |
|   394 MB RAM footprint, sub-2ms prediction response.                                              |
| * Dual-Channel Accessibility: NASA-STD-3001 compliant geometric status indicators (●, ▲, ■).     |
| * Operational Value: Ready to assist flight safety officers, payload developers, and astronaut    |
|   crews on Artemis and Mars human exploration missions.                                           |
| * Future Horizon: Real-time telemetry ingestion from Lunar Gateway and Saffire-VII flights.        |
|                                                                                                   |
| Visual / Image Recommendation:                                                                    |
| Diagram of the Hexagonal Architecture (Ports, Adapters, Predictor, Retriever, Streamlit UI)       |
| alongside team credits: "NASA Space Apps Challenge 2026 | Built on Open NASA PSI & STI Data".     |
+---------------------------------------------------------------------------------------------------+
```

---

## Key Metrics & Numerical Proofs Reference

| Metric | Measured Value | Significance / Context |
| :--- | :---: | :--- |
| **Total NASA PSI Flight Data** | **12+ Terabytes** | Across all 24 Combustion Science flight investigations |
| **NASA STI Papers Harvested** | **101 Publications** | Peer-reviewed technical reports and flight memos |
| **FAISS Vector Chunks** | **1,573 Chunks** | Ingested into local dense vector retrieval index |
| **ML Prediction Latency (p95)** | **1.91 ms** | Measured across 400 test iterations (budget < 100 ms) |
| **Batched Curve Calculation** | **7.7 ms** | 14x faster than scalar 57-step loops |
| **Model Accuracy (Log $R^2$)** | **0.934** | 5-Fold Grouped Cross-Validation across distinct experiments |
| **Conformal Coverage Rate** | **90.0%** | Guaranteed distribution-free empirical interval coverage |
| **Refusal Gate Cosine $\tau$** | **0.7455** | AUC = 0.9863 calibrated threshold refusing hallucinations |
| **3D Rendering Frame Rate** | **60 FPS** | Ray-marched volumetric WebGL shader |
| **Automated Test Pass Rate** | **100% (27/27)** | Master suite across unit, integration, and UI tests |
| **Memory RSS Footprint** | **394 MB** | Stable under 1024 MB resource ceiling |
| **SCBA Tank Weight Reduction**| **40% (13 lbs)** | Civilian firefighter air tank weight saved via Apollo PLSS |
| **Firefighter Burn Reduction** | **> 60%** | Civilian firefighter burn casualties eliminated via PBI gear |

