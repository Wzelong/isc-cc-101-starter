import base64
import json
from datetime import date, datetime, timezone
from pathlib import Path
from secrets import token_hex

STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "fhir_store.json"


def _load() -> dict:
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save(store: dict) -> None:
    STORE_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_patient() -> dict:
    return _load()["Patient"]


def get_conditions() -> list[dict]:
    return _load()["Condition"]


def document_text(doc: dict) -> str:
    data = doc["content"][0]["attachment"]["data"]
    return base64.b64decode(data, validate=True).decode("utf-8")


def get_documents() -> list[dict]:
    docs = []
    for doc in _load()["DocumentReference"]:
        try:
            text = document_text(doc)
        except Exception:
            continue
        docs.append(
            {
                "title": doc["content"][0]["attachment"].get("title", "Untitled"),
                "date": doc.get("date", "")[:10],
                "text": text,
            }
        )
    return docs


def add_document(title: str, text: str) -> dict:
    store = _load()
    doc = {
        "resourceType": "DocumentReference",
        "id": f"doc-{token_hex(4)}",
        "status": "current",
        "type": {"text": title},
        "subject": {"reference": f"Patient/{store['Patient']['id']}"},
        "date": _now(),
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "title": title,
                    "data": text,
                }
            }
        ],
    }
    store["DocumentReference"].append(doc)
    _save(store)
    return doc


def remove_document(doc_id: str) -> None:
    store = _load()
    store["DocumentReference"] = [d for d in store["DocumentReference"] if d["id"] != doc_id]
    _save(store)


def add_condition(condition: dict) -> dict:
    store = _load()
    store["Condition"].append(condition)
    _save(store)
    return condition


def _age(birth: str | None) -> str:
    if not birth:
        return ""
    y, m, d = (int(x) for x in birth[:10].split("-"))
    today = date.today()
    return str(today.year - y - ((today.month, today.day) < (m, d)))


def _mrn(identifiers: list[dict] | None) -> str:
    for ident in identifiers or []:
        if ident.get("type", {}).get("coding", [{}])[0].get("code") == "MR":
            return ident.get("value", "")
    return ""


def _contact(patient: dict) -> str:
    addr = (patient.get("address") or [{}])[0]
    line = ", ".join(addr.get("line", []))
    city = " ".join(p for p in [addr.get("city", ""), addr.get("state", ""), addr.get("postalCode", "")] if p)
    phone = next((t.get("value", "") for t in patient.get("telecom", []) if t.get("system") == "phone"), "")
    return " · ".join(p for p in [", ".join(p for p in [line, city] if p), phone] if p)


def patient_header() -> dict:
    p = get_patient()
    name = f"{p['name'][0]['given'][0]} {p['name'][0]['family']}"
    sex = (p.get("gender", "")[:1]).upper()
    age = _age(p.get("birthDate"))
    mrn = _mrn(p.get("identifier"))
    ident = " · ".join(
        x for x in [f"{age}{sex}" if age else "", f"DOB {p.get('birthDate', '')}", f"MRN {mrn}" if mrn else ""] if x
    )
    return {"name": name, "ident": ident, "contact": _contact(p)}


def _code_text(cc: dict) -> str:
    return cc.get("text") or cc.get("coding", [{}])[0].get("display", "")


def _condition_row(r: dict) -> dict:
    return {
        "name": _code_text(r["code"]),
        "meta": r["clinicalStatus"]["coding"][0]["code"],
        "date": (r.get("onsetDateTime") or "")[:4],
    }


def _med_row(r: dict) -> dict:
    return {
        "name": _code_text(r["medicationCodeableConcept"]),
        "meta": (r.get("dosageInstruction") or [{}])[0].get("text", ""),
        "date": (r.get("authoredOn") or "")[:10],
    }


def _allergy_row(r: dict) -> dict:
    return {
        "name": _code_text(r["code"]),
        "meta": r.get("criticality", ""),
        "date": (r.get("recordedDate") or "")[:10],
    }


def _obs_row(r: dict) -> dict:
    q = r.get("valueQuantity", {})
    value = f"{q.get('value', '')} {q.get('unit', '')}".strip()
    interp = (r.get("interpretation") or [{}])[0].get("coding", [{}])[0].get("code", "")
    return {
        "name": _code_text(r["code"]),
        "meta": f"{value} · {interp}" if interp else value,
        "date": (r.get("effectiveDateTime") or "")[:10],
    }


def _encounter_row(r: dict) -> dict:
    return {
        "name": _code_text((r.get("type") or [{}])[0]),
        "meta": r.get("status", ""),
        "date": (r.get("period") or {}).get("start", "")[:10],
    }


_SECTIONS = [
    ("Conditions", "Condition", _condition_row),
    ("Medications", "MedicationRequest", _med_row),
    ("Allergies", "AllergyIntolerance", _allergy_row),
    ("Observations", "Observation", _obs_row),
    ("Encounters", "Encounter", _encounter_row),
]


def chart_sections() -> list[dict]:
    store = _load()
    sections = []
    for title, resource_type, builder in _SECTIONS:
        items = store.get(resource_type, [])
        if items:
            sections.append({"title": title, "count": len(items), "rows": [builder(r) for r in items]})
    return sections
