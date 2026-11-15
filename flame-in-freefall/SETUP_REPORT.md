# Setup report

- **SKIP**: Install dependencies
- **PASS**: Phase 0 data audit
- **PASS**: Train model
- **PASS**: Backend tests (synthetic)
- **PASS**: Backend tests (real data)
- **PASS**: RAG index tests (fixture)
- **PASS**: RAG calibration tests (fixture)
- **PASS**: Assistant tests (mock LLM)
- **PASS**: Insights tests (findings, scenarios)
- **PASS**: Insights tests (coverage map)
- **PASS**: Insights tests (experiment catalog)
- **PASS**: Insights tests (risk cards)
- **PASS**: Insights tests (topic synthesis)
- **PASS**: Insights tests (natural-language scenarios)
- **PASS**: Insights tests (AI brief verifier, mock LLM)
- **PASS**: Insights tests (verification tool)
- **PASS**: Insights tests (terrestrial spin-offs)
- **PASS**: Insights tests (report export)
- **PASS**: Insights tests (historic incidents)
- **PASS**: Insights tests (persona adapters)
- **PASS**: Domain layer tests (physics & safety)
- **PASS**: Application services tests
- **PASS**: Non-functional requirements tests (security, audit, circuit breaker)
- **PASS**: RAG summaries tests
- **PASS**: App tests (AI brief flow, mock LLM)
- **PASS**: App tests (natural-language scenarios)
- **PASS**: App tests (documents and synthesis tab)
- **PASS**: Resource tests (memory, latency)
- **SKIP**: NASA harvest
- **SKIP**: Build index
- **SKIP**: Calibrate

## Details

### Install dependencies (SKIP)
```
--skip-install
```
### Phase 0 data audit (PASS)
```
- thickness_mm: n=22, min=0.075, max=0.075
- missing % (required+continuous): {}

## Gate: (fuel, g_level) groups
Threshold: >= 15 distinct comparable experiments

| fuel   |   g_level |   n_experiments | status   |
|:-------|----------:|----------------:|:---------|
| PMMA   |         0 |              22 | MODEL_OK |

## GO / NO-GO: GO (at least one modelable group)
- WARNING: only one gravity level present among comparable rows; the 0g-vs-1g comparison cannot be modeled.
```
### Train model (PASS)
```
    },
    "n_experiments": 22,
    "folds": 5,
    "mae_log": 0.05519046455127021,
    "r2_log": 0.9336574618461688,
    "mae_mm_s": 0.2207358511386777,
    "baseline_mae_log": 0.23210211439562684,
    "beats_baseline": true,
    "conformal_q90_log": 0.12971772978933035,
    "cross_conformal_coverage": 0.9
  }
}
```
### Backend tests (synthetic) (PASS)
```
C:\Users\dell\AppData\Local\Programs\Python\Python311\Lib\site-packages\sklearn\gaussian_process\kernels.py:450: ConvergenceWarning: The optimal value found for dimension 0 of parameter k1__k2__length_scale is close to the specified upper bound 1000.0. Increasing the bound and calling fit again may find a better value.
  warnings.warn(
C:\Users\dell\AppData\Local\Programs\Python\Python311\Lib\site-packages\sklearn\gaussian_process\kernels.py:450: ConvergenceWarning: The optimal value found for dimension 1 of parameter k1__k2__length_scale is close to the specified upper bound 1000.0. Increasing the bound and calling fit again may find a better value.
  warnings.warn(
C:\Users\dell\AppData\Local\Programs\Python\Python311\Lib\site-packages\sklearn\gaussian_process\kernels.py:450: ConvergenceWarning: The optimal value found for dimension 0 of parameter k1__k2__length_scale is close to the specified upper bound 1000.0. Increasing the bound and calling fit again may find a better value.
  warnings.warn(
C:\Users\dell\AppData\Local\Programs\Python\Python311\Lib\site-packages\sklearn\gaussian_process\kernels.py:450: ConvergenceWarning: The optimal value found for dimension 1 of parameter k1__k2__length_scale is close to the specified upper bound 1000.0. Increasing the bound and calling fit again may find a better value.
  warnings.warn(
C:\Users\dell\AppData\Local\Programs\Python\Python311\Lib\site-packages\sklearn\gaussian_process\kernels.py:450: ConvergenceWarning: The optimal value found for dimension 0 of parameter k1__k2__length_scale is close to the specified upper bound 1000.0. Increasing the bound and calling fit again may find a better value.
  warnings.warn(
C:\Users\dell\AppData\Local\Programs\Python\Python311\Lib\site-packages\sklearn\gaussian_process\kernels.py:450: ConvergenceWarning: The optimal value found for dimension 1 of parameter k1__k2__length_scale is close to the specified upper bound 1000.0. Increasing the bound and calling fit again may find a better value.
  warnings.warn(
```
### Backend tests (real data) (PASS)
```
model: gp | safe O2 range: 21.7-36.0% | p95 latency 2.70 ms
REAL-DATA TESTS PASSED
```
### RAG index tests (fixture) (PASS)
```
RAG INDEX TESTS PASSED | chunks=12 docs=2 | on-topic score 0.47 vs off-topic 0.14
```
### RAG calibration tests (fixture) (PASS)
```
CALIBRATION TESTS PASSED | tau=0.252 | out max 0.21 < in median 0.56 | AUC 1.00
```
### Assistant tests (mock LLM) (PASS)
```
ASSISTANT TESTS PASSED (11 groups: gate, grounding, verification, timeout chain, no-key mode, rate limit, daily cap, validation, logs, cache builder, OpenAI client)
```
### Insights tests (findings, scenarios) (PASS)
```
INSIGHTS TESTS PASSED | {'iss': 'NEAR', 'transit': 'NOT_COVERED', 'lunar_alt': 'NOT_COVERED', 'lunar': 'NOT_COVERED', 'mars': 'NOT_COVERED'} | lunar top 3: ['F07', 'F15', 'F10']
```
### Insights tests (coverage map) (PASS)
```
COVERAGE MAP TESTS PASSED | exploration atmosphere gap 2.3 kPa | ISS status NEAR | 25 table rows
```
### Insights tests (experiment catalog) (PASS)
```
CATALOG TESTS PASSED | 15 entries, 15 verified | exploration-atmosphere evidence: ['E09', 'E10'] (no microgravity data)
```
### Insights tests (risk cards) (PASS)
```
RISK CARD TESTS PASSED | lunar: {'spread': 'NO_PREDICTION', 'limit': 'MEASURED', 'ignition': 'INDIRECT', 'detection': 'INDIRECT', 'suppression': 'INDIRECT', 'materials': 'INDIRECT', 'ventilation': 'INDIRECT'}
```
### Insights tests (topic synthesis) (PASS)
```
TOPIC SYNTHESIS TESTS PASSED | Verified flame-spread synthesis & conflicting directions fixture validated
```
### Insights tests (natural-language scenarios) (PASS)
```
NATURAL-LANGUAGE SCENARIO TESTS PASSED | 12 phrasings, unit conversions, clarifications & validations confirmed
```
### Insights tests (AI brief verifier, mock LLM) (PASS)
```
SI BRIEF TESTS PASSED | 11 bad outputs rejected, each by its own rule, rounding allowed, fallback/cap/cache verified
```
### Insights tests (verification tool) (PASS)
```
VERIFY TOOL TESTS PASSED | findings: verify/edit/cannot-confirm/delete/skip/quit; catalog: verify/edit/invalid edit refused; real files untouched
```
### Insights tests (terrestrial spin-offs) (PASS)
```
TERRESTRIAL SPIN-OFF TESTS PASSED | 4 verified applications
```
### Insights tests (report export) (PASS)
```
REPORT EXPORT TESTS PASSED
```
### Insights tests (historic incidents) (PASS)
```
HISTORIC INCIDENTS TESTS PASSED
```
### Insights tests (persona adapters) (PASS)
```
PERSONA TESTS PASSED
```
### Domain layer tests (physics & safety) (PASS)
```
DOMAIN LAYER TESTS PASSED
```
### Application services tests (PASS)
```
APPLICATION SERVICES LAYER TESTS PASSED
```
### Non-functional requirements tests (security, audit, circuit breaker) (PASS)
```
ALL NFR UNIT TESTS PASSED
```
### RAG summaries tests (PASS)
```
RAG SUMMARIES TESTS PASSED | Extractive fallback, verification rules, Mock LLM & filter validated
```
### App tests (AI brief flow, mock LLM) (PASS)
```
APP BRIEF TESTS PASSED | no-key mode, verified AI brief, rejected AI brief, service down, rate limit
2026-11-15 00:57:52.978 WARNING streamlit.runtime.caching.cache_data_api: No runtime found, using MemoryCacheStorageManager
2026-11-15 00:57:52.978 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 00:57:56.850 No runtime found, using MemoryCacheStorageManager
2026-11-15 00:57:56.851 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 00:57:58.505 No runtime found, using MemoryCacheStorageManager
2026-11-15 00:57:58.506 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 00:58:00.492 No runtime found, using MemoryCacheStorageManager
2026-11-15 00:58:00.492 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
2026-11-15 00:58:02.975 No runtime found, using MemoryCacheStorageManager
2026-11-15 00:58:02.975 Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```
### App tests (natural-language scenarios) (PASS)
```
APP NATURAL-LANGUAGE SCENARIO TESTS PASSED
2026-11-15 00:58:12.435 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```
### App tests (documents and synthesis tab) (PASS)
```
APP DOCUMENTS & SYNTHESIS TAB TESTS PASSED
2026-11-15 00:58:18.788 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```
### Resource tests (memory, latency) (PASS)
```
predict p95 1.91 ms | 57-point curve 96 ms | RSS after load 394 MB, after 10 reruns 406 MB, after 30 406 MB (budget 1024 MB)
RESOURCE TESTS PASSED
2026-11-15 00:58:28.497 WARNING streamlit.runtime.scriptrunner_utils.script_run_context: Thread 'MainThread': missing ScriptRunContext! This warning can be ignored when running in bare mode.
```
### NASA harvest (SKIP)
```
--offline
```
### Build index (SKIP)
```
--offline
```
### Calibrate (SKIP)
```
--offline
```
## Index
```
{
 "embedder": "BAAI/bge-small-en-v1.5",
 "dim": 384,
 "n_chunks": 1573,
 "n_docs": 52,
 "corpus_signature": "4577ed032f35",
 "built_at": "2026-11-14T14:11:57.800346+00:00",
 "chunk_size": 800
}
```
## Excluded documents
```
id,title,reason
20205004657,Effects of Confinement on Flame Spread in Microgravity,no document text (metadata only or copyright review)
19970020613,"Ignition, Transition, Flame Spread in Multidimensional Configurations in Microgravity",no document text (metadata only or copyright review)
20210011385,Burning and Suppression of Solids–II  (BASS-II) Summary Report,no document text (metadata only or copyright review)
20170000230,Operation and Development Status of the Spacecraft Fire Experiments (Saffire),no document text (metadata only or copyright review)
20170001636,"The Spacecraft Fire Experiment (Saffire) - Objectives, Development and Status",no document text (metadata only or copyright review)
20240002981,Preliminary Results from the Saffire VI Experiment,no document text (metadata only or copyright review)
20240007488,Preliminary Results from the Saffire VI Experiment,no document text (metadata only or copyright review)
20220002714,Model Development of Large-Scale Spacecraft Fires During the Saffire-IV Experiments,no document text (metadata only or copyright review)
20250010653,Lunar Combustion Investigation: Flammability Results from a Rotating Sounding Rocket,no document text (metadata only or copyright review)
20260000859,Revision of NASA-STD-6001,no document text (metadata only or copyright review)
20040142368,Organizing Questions for Reduced-Gravity Flammability,no document text (metadata only or copyright review)
20030053428,Control of Materials Flammability Hazards,no document text (metadata only or copyright review)
20040084025,Reference Material Kydex(registered trademark)-100 Test Data Message for Flammability Testing,no document text (metadata only or copyright review)
20130000677,Large Scale Experiments on Spacecraft Fire Safety,excluded keyword
20130001713,Large Scale Experiments on Spacecraft Fire Safety,excluded keyword
20205000063,Spacecraft Fire Safety Technology Development Plan For Exploration Missions,no document text (metadata only or copyright review)
19880003138,Spacecraft Fire Safety,no document text (metadata only or copyright review)
19960008403,Combustion of a polymer (PMMA) sphere in microgravity,no document text (metadata only or copyright review)
20210015913,Advanced Combustion via Microgravity Experiments (ACME) on the International Space Station (ISS),no document text (metadata only or copyright review)
20220015583,ACME: Advanced Combustion via Microgravity Experiments,no document text (metadata only or copyright review)
20210022542,Recent Research on Flames of Gaseous Fuel Aboard the International Space Station ,no document text (metadata only or copyright review)
20210021781,Recent Research on Flames of Gaseous Fuel Aboard the International Space Station ,no document text (metadata only or copyright review)
20040053516,Transport And Chemical Effects On Concurrent And Opposed-Flow Flame Spread At Microgravity,no document text (metadata only or copyright review)
20040053557,Extinction Criteria for Opposed-Flow Flame Spread in a Microgravity Environment,no document text (metadata only or copyright review)
19890014267,An experimental study of opposed flow diffusion flame extinction over a thin fuel in microgravity,no document text (metadata only or copyright review)
20010074003,Three-Dimensional Upward Flame Spreading in Partial-Gravity Buoyant Flows,no document text (metadata only or copyright review)
20040053567,Upward And Downward Flame Spreading And Extinction In Partial Gravity Environments,no document text (metadata only or copyright review)
20210017787,Determining the Cause of Reduced Concurrent Flame Spread over Thin Solid Fuels in Low Pressure and Low Gravity,no document text (metadata only or copyright review)
20210020516,Fire on the Moon: Solid Fuel Combustion Experiments,no document text (metadata only or copyright review)
20010074095,Flame Spread in a Microgravity Environment-Role of Fuel Thickness,no document text (metadata only or copyright review)
19880006471,The Effect of Micro
```