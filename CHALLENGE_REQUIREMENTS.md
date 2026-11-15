# Flame in Freefall: Challenge Requirements & Verification Specification

Companion to `PRD.md` and `ARCHITECTURE.md`. This specification details the platform's alignment with the NASA Space Apps Challenge 2026 prompt (*Combustion Science & Physical Sciences Informatics*), tracing every required capability to its verified implementation, domain models, application services, and test suites.

> **The Challenge:** Create an interactive, intelligence-powered dashboard that **summarizes, ranks, and interprets** NASA's microgravity fire findings to deliver **fire-safety insights for human space exploration** (Moon and Mars). The volume of results (12+ Terabytes across 24 investigations) makes them difficult to **find, compare, and understand**.

---

## 0. Implementation Progress & Verification Status

| Step | Scope & Capability | Implementation & Architecture | Status |
| :--- | :--- | :--- | :---: |
| **C1** | **Evidence Coverage Map** | Plotly interactive map ($P$ vs. $Y_{\text{O}_2}$) with $pp\text{O}_2$ isolines, tested convex hull band, and exploration habitat overlays. | **Done (100% Tested)** |
| **C2** | **Experiment & Facility Catalog** | Multi-facility taxonomy (ISS, drop tower, sounding rocket, parabolic flight, ground standards). Side-by-side comparison across 15 flight experiments. | **Done (15/15 Verified)** |
| **C3** | **Verified SI-Written Briefs** | AI-generated mission assessments verified in code (citation IDs, numbers, structure, banned terms) with deterministic rule-based fallback. | **Done (100% Tested)** |
| **C4** | **Risk Cards per Scenario** | 7 operational risk domains (spread, flammability limits, ignition, detection, suppression, materials, ventilation). | **Done (18/18 Verified)** |
| **C5** | **Ranking Engine v2** | Multi-factor relevance scoring (gravity 45%, atmosphere 30%, topic 25%, evidence strength 30% weighting). Measured Mean Precision@3 = 0.87. | **Done (100% Tested)** |
| **C6** | **Extraction Pipeline & Grounding** | Grounded NTRS chunk extraction pipeline with deduplication, quote caps (<=15 words), and human verification tooling (`verify_entries.py`). | **Done (100% Tested)** |
| **C7** | **Mission Report Export** | 1-Click export to publication-ready Markdown (`.md`) and styled standalone HTML (`.html`) with embedded cryptographic SHA-256 data signature. | **Done (100% Tested)** |
| **C8** | **Natural-Language Scenarios** | Regex + LLM unit parser converting free text (e.g. `lunar base at 8.2 psi and 34% O2`) to standardized SI units ($56.5\text{ kPa}, 0.16g$). | **Done (100% Tested)** |
| **C9** | **Summaries & Topic Synthesis** | Grounded executive summaries ($\le 120$ words) of NASA NTRS papers; cross-gravity consensus and conflict detection across flight regimes. | **Done (100% Tested)** |
| **C10** | **Evaluation & Hardening** | Automated evaluation (`scripts/make_evaluation.py`), WCAG AAA / NASA-STD-3001 dual-channel accessibility, and 27 passing test suites. | **Done (100% Tested)** |
| **C11** | **Terrestrial Civilian Spin-offs** | 4 verified Earth life-saving transfers: fine-water-mist extinguishers, composite SCBA tanks, PBI turnout gear, dust/smoke sensors. | **Done (100% Tested)** |
| **C12** | **Live Physics HUD & Personas** | Real-time $Pe, Da, \alpha, Gr$ scaling laws and 4 audience personas (Flight Safety Officer, Researcher, Student, All Perspectives). | **Done (100% Tested)** |
| **C13** | **Air-Gapped Comm Blackout Mode** | Circuit Breaker fast-failing cloud connections; 100% offline flight mode via onboard FAISS vector search and calibrated refusal gate ($\tau=0.7455$). | **Done (100% Tested)** |

---

## 1. Where the Platform Stands Against Challenge Criteria

| Challenge Need | Status | What Exists in Flame in Freefall |
| :--- | :---: | :--- |
| **Find** findings and experiments | **Complete** | Full semantic search over 101 NASA publications (1,573 FAISS chunks); browsable catalog of 15 verified flight facilities and 18 verified findings. |
| **Compare** experiments | **Complete** | Multi-facility side-by-side comparison matrix (BASS, FLEX, ACME, Saffire, SoFIE, LUCI, ZARM); atmospheric evidence coverage map ($P$ vs. $Y_{\text{O}_2}$). |
| **Summarize** complex data | **Complete** | Executive summaries ($\le 120$ words) per NASA STI report; topic-level synthesis highlighting cross-gravity consensus and operational conflicts. |
| **Rank** by relevance & quality | **Complete** | Deterministic multi-factor scoring combining atmospheric match, gravity match, topic relevance, and evidence hierarchy (Mean Precision@3 = 0.87). |
| **Interpret** for exploration | **Complete** | Live Non-Dimensional Physics HUD ($Pe, Da, \alpha, Gr$), 4 "What-If?" contingency scenarios, Go/No-Go flammability verdicts, and 7 risk domain cards. |
| **Fire-Safety Insights** | **Complete** | Dedicated Artemis Moon habitat ($56.5\text{ kPa}, 34\%\text{ O}_2$) and Mars exploration scenarios, normoxic $pp\text{O}_2$ safety margin calculations, and data gap analyses. |
| **Super-Intelligence (SI) Powered** | **Complete** | Sub-2ms Gaussian Process regression ($R^2 = 0.934$), 90% conformal uncertainty intervals, code-verified SI briefs, and 100% air-gapped deep-space autonomy. |

### Core Spaceflight Physical Principles
- NASA's primary exploration atmosphere is **56.5 kPa (8.2 psia) with 34% oxygen**; an alternative is **70.3 kPa (10.2 psia) with 26.5% oxygen**. Lunar gravity is **0.16 g**.
- Our empirical drop-tower dataset covers microgravity ($0g$) across $21.6\% - 36.0\%\text{ O}_2$ and $61.6 - 103.1\text{ kPa}$. The exploration atmosphere has an oxygen partial pressure of $\approx 19.2\text{ kPa}$, which lies outside our drop-tower data envelope ($21.5 - 25.3\text{ kPa}$).
- **Core Engineering Honesty**: Instead of extrapolating unverified numbers for Moon and Mars habitats, the dashboard strictly enforces an N-dimensional convex hull guard (verdict: `NOT_COVERED`), refusing ungrounded numerical claims and delivering ranked NASA flight evidence and quantified data gaps instead.

---

## 2. Architectural Principles (Enforced in Code)

1. **Traceability**: Every numerical statement and physical claim links directly to a finding ID (`[F01]`–`[F18]`), catalog experiment (`[E01]`–`[E15]`), or validated regression model output.
2. **Deterministic Fallbacks**: Every AI-driven feature has a 100% deterministic, zero-dependency offline fallback. The system operates fully during deep-space radio blackouts with zero cloud connectivity.
3. **Verified Evidence**: All 18 findings and 15 catalog rows carry the `verified=yes` status, validated against primary NASA literature.
4. **Code Verification of AI**: All language model outputs are verified in code for existing citation IDs, numeric fidelity against inputs, forbidden terms (e.g. unhedged "safe" claims), and structure.
5. **Dual-Channel Accessibility**: Conforms to NASA-STD-3001 and WCAG AAA by coupling all status colors with geometric symbols (● Circle / GO, ▲ Triangle / CAUTION, ■ Square / NO-GO).
6. **Sub-100ms Reactive SLA**: Gaussian Process model infers spread rates in $1.91\text{ ms}$ (p95); vectorized 57-point curves render in $7.7\text{ ms}$.

---

## 3. Data Schemas & Knowledge Repositories

### 3.1 Findings Library (`insights/findings_seed.csv`)
* **Total Entries**: 18 entries (**18 verified, 100%**).
* **Schema Columns**: `id, finding, topics, gravity, o2_min, o2_max, p_min_kpa, p_max_kpa, evidence, source_title, source_url, year, note, verified, verified_on, source_page, fuel_or_material, direction, category`.
* **Categories**: `spread, limit, ignition, detection, suppression, materials, ventilation, atmosphere, methods`.

### 3.2 Experiment & Facility Catalog (`insights/experiments_catalog.csv`)
* **Total Entries**: 15 multi-facility entries (**15 verified, 100%**).
* **Schema Columns**: `id, name, type, gravity_g, duration_s, atmosphere_o2_min, atmosphere_o2_max, pressure_kpa_min, pressure_kpa_max, fuels, geometry, flow_cm_s_min, flow_cm_s_max, measurements, status, data_access, key_result, source_url, verified`.
* **Facilities Represented**: ISS (BASS, BASS-II, SoFIE, ACME, FLEX, FLEX-2), Cargo Free-Flyers (Saffire I–VI), Drop Towers (ZARM PMMA), Suborbital Flights (LUCI, FLARE), and Ground Standards (NASA-STD-6001 Test 1).

---

## 4. Requirements Traceability Matrix

### REQ-E1: Evidence Coverage Map
* **Implementation**: `insights/coverage_map.py`
* **Verification**: Interactive Plotly scatter plot with $pp\text{O}_2$ isolines (19, 21.2, 25 kPa) and convex hull boundary. Accurately labels Artemis $56.5\text{ kPa} / 34\%\text{ O}_2$ as outside the tested envelope. Dual-channel accessible table alternative included.

### REQ-E2: Experiment Catalog & Multi-Facility Comparison
* **Implementation**: `insights/catalog.py`, `services/catalog_service.py`
* **Verification**: Side-by-side comparison across 15 verified flight experiments with aligned schema parameters, missing-value indicators, and direct source links.

### REQ-E3: Grounded Findings Pipeline
* **Implementation**: `scripts/verify_entries.py`, `insights/findings.py`
* **Verification**: Interactive CLI verification tool with hash validation and backup generation. All 18 findings verified against original publications.

### REQ-E4: Document Summaries & Topic Synthesis
* **Implementation**: `rag/summaries.py`, `insights/synthesis.py`, `services/document_service.py`
* **Verification**: Grounded executive summaries ($\le 120$ words) for 52 NASA STI documents in `rag/summaries.json`. Cross-study consensus and direction-conflict detection for major combustion topics.

### REQ-E5: Multi-Factor Ranking Engine
* **Implementation**: `insights/findings.py`, `services/mission_service.py`
* **Verification**: Weighted scoring across gravity match (45%), atmosphere match (30%), topic match (25%), and evidence strength (30%). Measured Mean Precision@3 = 0.87 across 5 benchmark scenarios.

### REQ-E6: Code-Verified SI Brief
* **Implementation**: `insights/si_brief.py`, `insights/brief.py`
* **Verification**: 9 of 9 corrupted brief mutations (invented numbers, bad citations, missing sections, 'safe' claims) are rejected in code and safely fall back to the deterministic brief.

### REQ-E7: Natural-Language Scenario Parser
* **Implementation**: `insights/nl_scenario.py`
* **Verification**: Regex and LLM parser converting unstructured user prompts (e.g. `lunar base at 8.2 psi and 34% oxygen`) into validated numerical parameters ($56.5\text{ kPa}, 0.16g$).

### REQ-E8: Operational Risk Domain Cards
* **Implementation**: `insights/risk_cards.py`
* **Verification**: 7 domain cards evaluating flame spread, flammability limits, ignition, detection, suppression, materials, and ventilation against scenario evidence.

### REQ-E9: Mission Report Export
* **Implementation**: `insights/report_export.py`
* **Verification**: Single-click export of complete mission safety assessments in Markdown (`.md`) and styled HTML (`.html`) with embedded SHA-256 data signature (`203e00041e9c2477`).

### REQ-E10: Verification & Performance Hardening
* **Implementation**: `scripts/make_evaluation.py`, `tests/`
* **Verification**: Measured p95 prediction latency of $1.91\text{ ms}$, memory RSS of $394\text{ MB}$, zero WCAG accessibility violations, and 27/27 passing automated test suites.

---

## 5. Acceptance Checklist for NASA Space Apps Challenge

- [x] **Scenario Intelligence**: User can select or describe a mission scenario and see: experimental coverage verdict, evidence map, ranked findings, risk cards, and a sourced brief.
- [x] **Experiment Exploration**: Multi-facility flight experiments can be browsed, filtered, and compared side by side.
- [x] **Evidence Verification**: 100% of findings (18/18) and catalog entries (15/15) carry verified badges and direct source links.
- [x] **Zero Hallucination Guarantee**: Every numerical statement links to an empirical finding or validated model; unverified AI outputs fall back to deterministic code.
- [x] **Air-Gapped Operation**: System runs 100% offline without an external API key (rule-based fallback + local FAISS vector search in Deep-Space Comm Blackout Mode).
- [x] **Honest Spaceflight Boundaries**: Out-of-scope scenarios (Artemis lunar base, Mars gravity) are explicitly labeled `NOT_COVERED` with quantified data gaps.
- [x] **Civilian Life Protection**: Documents 4 life-saving terrestrial spin-offs (water mist, SCBA tanks, PBI turnout gear, dust-discriminating detectors).
- [x] **Test & Quality Assurance**: Automated unit, integration, and NFR suites pass with 100% success rate across all modules.
