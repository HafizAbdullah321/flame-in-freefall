# Run from the repo root (folder containing phase0/ and backend/)
audit:
	cd phase0 && python phase0_audit.py --raw raw --out out --min-exp 15

train: audit
	cd backend && python -m ffbackend.train --phase0-out ../phase0/out --artifacts artifacts --model-feats o2_pct fuel_coverage

test:
	cd backend && python -m tests.test_backend && python -m tests.test_real

app:
	pip install -r backend/requirements.txt streamlit plotly && streamlit run app/streamlit_app.py

rag-harvest:
	pip install -r rag/requirements.txt && python -m rag.harvest_all --per-query 15

rag-index:
	python -m rag.build_index --corpus rag/corpus --out rag/index

rag-sync:
	python -m rag.ntrs_harvest sync --root rag/corpus

test-rag:
	python -m rag.tests.test_rag_index

rag-calibrate:
	python -m rag.calibrate --index rag/index --questions rag/questions.csv --out rag/tau.json

test-rag-all:
	python -m rag.tests.test_rag_index && python -m rag.tests.test_calibration

setup:
	python scripts/setup_all.py

rag-cache:
	python -m rag.build_cache --index rag/index --tau rag/tau.json --out rag/cache.json

test-assistant:
	python -m rag.tests.test_assistant

test-resources:
	python tests/test_resources.py

test-a11y:
	python app/tests/test_accessibility.py

test-insights:
	python -m insights.tests.test_insights && python -m insights.tests.test_coverage_map && python -m insights.tests.test_catalog && python -m insights.tests.test_risk_cards && python -m insights.tests.test_si_brief && python -m insights.tests.test_verify && python app/tests/test_app_insights.py
