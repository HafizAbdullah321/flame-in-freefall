# Phase 0 Audit Report

Rows read: 22 | accepted: 22 | rejected: 0 | duplicate keys: 0

## literature
- experiments: 22, rows: 22
- comparable-target rows: 22
- fuels: ['PMMA']
- spread definitions: {'global_opposed_flat': 22}
- g_levels: [0.0]
- o2_pct: n=22, min=21.6, max=36
- pressure_kpa: n=22, min=61.6, max=103
- flow_velocity_mm_s: n=22, min=87.5, max=104
- thickness_mm: n=22, min=0.075, max=0.075
- missing % (required+continuous): {}

## Gate: (fuel, g_level) groups
Threshold: >= 15 distinct comparable experiments

| fuel   |   g_level |   n_experiments | status   |
|:-------|----------:|----------------:|:---------|
| PMMA   |         0 |              22 | MODEL_OK |

## GO / NO-GO: GO (at least one modelable group)
- WARNING: only one gravity level present among comparable rows; the 0g-vs-1g comparison cannot be modeled.