# Phase 0 workflow
1. Put each extracted dataset in raw/ as <name>.csv with a <name>.map.json (copy sources_template.map.json).
2. python phase0_audit.py --raw raw --out out --min-exp 15
3. Read out/AUDIT_REPORT.md, fill DATA_CARD.md, record GO / NO-GO.
Never put synthetic or guessed numbers in raw/.
