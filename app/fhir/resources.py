import base64

from app.fhir import store
from app.fhir.references import patient_reference


def encode_text(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def decode_text(data: str) -> str:
    return base64.b64decode(data).decode("utf-8")


def build_document_reference(patient_id: str, title: str, text: str) -> dict:
    return {
        "resourceType": "DocumentReference",
        "id": store.new_id("doc"),
        "status": "current",
        "type": {"text": title},
        "subject": {"reference": patient_reference(patient_id)},
        "date": store.now_iso(),
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "title": title,
                    "data": encode_text(text),
                }
            }
        ],
    }


def document_view(doc: dict) -> dict | None:
    attachment = doc["content"][0]["attachment"]
    try:
        text = decode_text(attachment["data"])
    except Exception:
        return None
    return {
        "title": attachment.get("title", "Untitled"),
        "date": (doc.get("date") or "")[:10],
        "text": text,
    }


NOTE_CATEGORY_CODE = "clinical-note"


def is_clinical_note(doc: dict) -> bool:
    for category in doc.get("category", []):
        for coding in category.get("coding", []):
            if coding.get("code") == NOTE_CATEGORY_CODE:
                return True
    return False


def _code_text(concept: dict) -> str:
    return concept.get("text") or concept.get("coding", [{}])[0].get("display", "")


def condition_row(resource: dict) -> dict:
    return {
        "name": _code_text(resource["code"]),
        "meta": resource["clinicalStatus"]["coding"][0]["code"],
        "date": (resource.get("onsetDateTime") or "")[:4],
    }


def medication_row(resource: dict) -> dict:
    return {
        "name": _code_text(resource["medicationCodeableConcept"]),
        "meta": (resource.get("dosageInstruction") or [{}])[0].get("text", ""),
        "date": (resource.get("authoredOn") or "")[:10],
    }


def allergy_row(resource: dict) -> dict:
    return {
        "name": _code_text(resource["code"]),
        "meta": resource.get("criticality", ""),
        "date": (resource.get("recordedDate") or "")[:10],
    }


def observation_row(resource: dict) -> dict:
    quantity = resource.get("valueQuantity", {})
    value = f"{quantity.get('value', '')} {quantity.get('unit', '')}".strip()
    interpretation = (resource.get("interpretation") or [{}])[0].get("coding", [{}])[0].get("code", "")
    return {
        "name": _code_text(resource["code"]),
        "meta": f"{value} · {interpretation}" if interpretation else value,
        "date": (resource.get("effectiveDateTime") or "")[:10],
    }


def encounter_row(resource: dict) -> dict:
    return {
        "name": _code_text((resource.get("type") or [{}])[0]),
        "meta": resource.get("status", ""),
        "date": (resource.get("period") or {}).get("start", "")[:10],
    }


SECTIONS = [
    ("Conditions", "Condition", condition_row),
    ("Medications", "MedicationRequest", medication_row),
    ("Allergies", "AllergyIntolerance", allergy_row),
    ("Observations", "Observation", observation_row),
    ("Encounters", "Encounter", encounter_row),
]
