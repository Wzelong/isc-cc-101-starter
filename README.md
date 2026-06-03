# FHIR Chart — ISC Claude Code 101

A tiny patient-chart app over a mock FHIR store. One patient, their coded
conditions, and their uploaded clinical notes. You'll use Claude Code to fix it,
probe it, and extend it across the tutorial.

## The picture

A health system runs a plain FHIR repository. The structured chart is thin —
the real clinical signal is buried in free-text notes. Over the next modules you
will make those notes useful: fix how they're stored, prove what's hidden in
them, and extract it into structured FHIR.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000.

## First step

Upload `notes/discharge-summary.txt` with the **Upload note** button on the chart
page. See what happens.

## Reset the data

The store is a single file. To start over:

```bash
git checkout data/fhir_store.json
```

## Layout

```
app/
  main.py          FastAPI routes — chart view + note upload
  fhir_store.py    mock FHIR store (load/save data/fhir_store.json)
  templates/       chart page
data/fhir_store.json   one Patient + one Condition + uploaded notes
notes/                 clinical notes to upload
```
