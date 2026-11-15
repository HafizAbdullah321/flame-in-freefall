# Evaluation report

Generated 2026-11-15 06:08 UTC by `scripts/make_evaluation.py`. All numbers below were measured by that script.

## 1. Evidence base and verification status

- Findings library: 18 entries, **18 verified** against their sources, 0 unverified (paraphrased from source excerpts; check before quoting).
- Experiment catalog: 15 entries, **15 verified**, 0 unverified; schema validation errors: 0.
- Every entry has an https source link. The dashboard marks unverified items.

## 2. What our experiments cover (honesty check)

| Scenario | Gravity | Pressure kPa | O2 % | O2 partial kPa | Atmosphere vs tested band | Verdict |
|---|---|---|---|---|---|---|
| ISS-like cabin (microgravity) | 0 g | 101.3 | 21.0 | 21.3 | near (gap 0.2 kPa) | NEAR |
| Exploration atmosphere, vehicle in microgravity | 0 g | 56.5 | 34.0 | 19.2 | outside (gap 2.3 kPa) | NOT_COVERED |
| Lunar habitat, alternative atmosphere | 0.16 g | 70.3 | 26.5 | 18.6 | outside (gap 2.8 kPa) | NOT_COVERED |
| Lunar habitat, exploration atmosphere | 0.16 g | 56.5 | 34.0 | 19.2 | outside (gap 2.3 kPa) | NOT_COVERED |
| Mars gravity, exploration atmosphere (illustrative) | 0.38 g | 56.5 | 34.0 | 19.2 | outside (gap 2.3 kPa) | NOT_COVERED |

Predictions are produced for 0 of 5 planned scenarios: the rest are refused with specific reasons.

## 3. Ranking quality (precision at 3)

Labels: one reviewer (the developer), small set; treat as a sanity check, not a benchmark.

| Scenario | Top 3 | Relevant in top 3 | Precision@3 |
|---|---|---|---|
| ISS-like cabin (microgravity) | F12, F14, F13 | 3 | 1.00 |
| Exploration atmosphere, vehicle in microgravity | F14, F12, F08 | 2 | 0.67 |
| Lunar habitat, alternative atmosphere | F15, F04, F07 | 3 | 1.00 |
| Lunar habitat, exploration atmosphere | F07, F15, F10 | 3 | 1.00 |
| Mars gravity, exploration atmosphere (illustrative) | F08, F07, F16 | 2 | 0.67 |

**Mean precision@3: 0.87**

## 4. AI brief verifier (no model needed)

- A correct brief passes: **True**.
- Corrupted briefs rejected: **9 of 9**.

  - invented number: rejected
  - unknown citation id: rejected
  - uncited evidence: rejected
  - 'safe' claim: rejected
  - over length: rejected
  - missing section: rejected
  - prediction for uncovered scenario: rejected
  - text before first label: rejected
  - malformed citation: rejected

## 5. Citation validity (rule-based brief)

- 15 links across 5 scenario briefs; links not in the findings library: **0**.

## 6. Latency (no AI call)

- Scenario evaluation + ranking + risk cards + brief: p50 2.3 ms, p95 2.6 ms (200 runs).

## 7. Not measured here

- Real AI brief quality and cost (needs your API key).
- Findings extraction at scale (not built yet).
- Frame rate on a real graphics card.
- Ranking against an independent reviewer's labels.

## Data signature

`203e00041e9c2477` (findings + catalog files)
