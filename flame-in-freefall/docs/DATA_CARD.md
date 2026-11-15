# Data Card: Flame in Freefall Training & Evidence Catalog

## 1. Experimental Training Dataset

### Source
* **Study**: ZARM Drop Tower orbital freefall study of flame spread over thin PMMA with and without metal heat sinks.
* **Zenodo Repository**: Record `18479713` (DOI: `10.5281/zenodo.18479713`), licensed **GPL-3.0-or-later**.
* **Publication**: *Proceedings of the Combustion Institute* / Microgravity Science and Technology.
* **Source Files**: `index.csv` (per-experiment ambient conditions), `Figure_06.csv` (fuel coverage $f^*$), `Figure_07.csv` (global spread rates and atmospheric parameters). Additional reference files: `Figure_03/04/05/09.csv`, `Sample_Shapes.csv` (archived in `phase0/sources/`).

### Dataset Scope & Feature Parameters (`phase0/raw/zarm_experiments_global.csv`)
| Parameter | Value / Distribution | Physical Units | Notes |
| :--- | :---: | :---: | :--- |
| **Experiments** | 22 comparable freefall tests | integer count | 5 continuous PMMA strips, 17 with aluminium or stainless steel barrier gaps |
| **Fuel Material** | Thin polymethyl methacrylate (PMMA) | 0.075 mm (75 µm) | Uniform thin-film solid polymer |
| **Gravity Level** | 0.0 (pure freefall) | $g_0$ | 4.7 seconds pure microgravity in drop tower capsule |
| **Flow Orientation** | Opposed flow | forced ventilation | Airflow opposes the advancing flame front |
| **Oxygen Concentration** | 21.6% to 36.0% | mole % ($Y_{\text{O}_2} \times 100$) | Atmospheric oxygen fraction |
| **Total Pressure** | 61.6 to 103.1 kPa | kPa | Confounded with oxygen ($\rho \approx -0.98$) |
| **Opposed Airflow Velocity** | 87.5 to 104.0 mm/s | mm/s | Sub-buoyant forced draft |
| **Fuel Coverage Ratio ($f^*$)** | 0.71 to 1.00 | dimensionless ratio | Effective fuel area fraction ($1.0 = \text{continuous}$) |
| **Target: Global Spread Rate** | 2.35 to 6.26 mm/s | mm/s | Target variable for regression modeling |
| **Canonical Label** | `global_opposed_flat` | string identifier | Harmonized Phase 0 comparable cohort |

### Data Joins & Validation Integrity
Figure 7 and Figure 6 were harmonized on the exact oxygen concentration (22 of 22 records matched perfectly). Pressure and flow velocity were confirmed against `index.csv`. Minimum quality gate of $\ge 15$ distinct experiments per fuel/gravity cohort passed with 22 rows. Full audit report: `phase0/out/AUDIT_REPORT.md`.

---

## 2. Model Performance Summary (`backend/artifacts/CV_REPORT.md`)

* **Model Family**: Gaussian Process Regressor (GPR) with composite Radial Basis Function (RBF) kernel, WhiteNoise regularization, and Matern-5/2 covariance.
* **Validation Strategy**: 5-Fold Grouped Cross-Validation grouped strictly by experiment run ID (zero spatial/temporal leakage).
* **Statistical Metrics**:
  * **Model Log $R^2$**: `0.9337`
  * **Log Mean Absolute Error**: `0.0552`
  * **Linear Scale MAE**: `0.2207 mm/s` (beats baseline by $>4\times$)
  * **Inference Latency (p95)**: `1.91 ms` (measured over 400 iterations)
  * **Conformal $q_{90}$ Bound**: `±0.1297 log margin`
  * **Cross-Conformal Empirical Coverage**: **90.0%** guaranteed distribution-free coverage.

---

## 3. NASA PSI Flight Ingestion & STI Publications

* **NASA Physical Sciences Informatics (PSI)**: Synthesizes metadata, facilities, and flight outcomes across **all 24 NASA Combustion Science investigations** representing **12+ Terabytes** of flight data (BASS, BASS-II, FLEX, FLEX-2, ACME, CFI-G, Saffire I–VI, SoFIE, LUCI, SAME, DAFT).
* **NASA STI / NTRS Technical Corpus**: 101 harvested research papers and accident investigation memos indexed into a dense FAISS vector index (1,573 chunks, 384-dimensional `BAAI/bge-small-en-v1.5` embeddings).
* **Calibrated Refusal Gate**: Cosine similarity cutoff ($\tau = 0.7455, \text{AUC} = 0.9863$). Questions outside NASA combustion science are mathematically declined in code.

---

## 4. Evidence Base & Verification Quality Status

* **Findings Library (`insights/findings_seed.csv`)**:
  * **Total Findings**: 18 entries.
  * **Verification Status**: **18 of 18 verified (100% verified)** against original NASA technical reports, AIAA conference papers, and peer-reviewed journals.
  * Exact page, table, and figure citations recorded for every claim. Zero unverified items.
* **Experiment & Facility Catalog (`insights/experiments_catalog.csv`)**:
  * **Total Entries**: 15 multi-facility entries (ISS, drop tower, sounding rocket, parabolic flights, ground standards).
  * **Verification Status**: **15 of 15 verified (100% verified)** against NASA mission specifications and flight project documents.
  * Schema validation errors: **0**.
* **Cryptographic Data Signature**: `203e00041e9c2477` (SHA-256 hash across findings and catalog datasets).

---

## 5. Known Caveats & Operational Envelope Guard

1. **Oxygen-Pressure Confounding**: Oxygen and total pressure vary inversely in the drop-tower dataset (correlation $\approx -0.98$), while flow velocity is held near 100 mm/s. The physical model uses oxygen as the primary slider and exposes pressure and flow as derived values along the experimental operating line.
2. **Fuel Specificity**: Predictions apply specifically to 75 µm thin-film PMMA under microgravity. Predictions for thick fuels or alternate materials are not supported.
3. **N-Dimensional Convex Hull Guard**:
   * Evaluates oxygen ($21.7\% - 36.0\%$), pressure ($40 - 110\text{ kPa}$), flow velocity, and fuel coverage.
   * If queried outside the convex hull (such as Artemis exploration atmosphere $56.5\text{ kPa} / 34\%\text{ O}_2$ or Lunar $0.16g$), model extrapolation is **strictly refused in code** (verdict: `NOT_COVERED`). The dashboard provides ranked NASA evidence and data gap analyses instead of speculative numbers.
4. **No 1g Measurements in Dataset**: Terrestrial 1g comparisons in the 3D visualizer are illustrative physical simulations; no empirical 1g flame spread rates are claimed.
5. **Intended Use**: Mission engineering, research, and educational demonstration tool. Not certified operational fire-safety guidance for spacecraft emergency egress.
