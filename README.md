# Larkspur EMR

A small patient-chart app over a mock FHIR store. Conditions, medications, labs,
encounters, and clinical notes for a handful of patients.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000.

## Reset the data

```bash
git checkout data/fhir_store.json
```
