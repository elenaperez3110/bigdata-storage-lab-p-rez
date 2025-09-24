.PHONY: venv install ingest validate normalize kpis app

venv:
	python -m venv .venv

install: venv
	. .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

ingest:
	. .venv/bin/activate && python -m src.ingestion.run

validate:
	. .venv/bin/activate && python -m src.validation.run

normalize:
	. .venv/bin/activate && python -m src.normalization.run

kpis:
	. .venv/bin/activate && python -m src.common.kpis

app:
	. .venv/bin/activate && streamlit run app/streamlit_app.py
