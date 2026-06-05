from app.fhir import store
from app.fhir.references import linked_patient_id


def list_patients() -> list[dict]:
    return store.load().get("Patient", [])


def get_patient(patient_id: str) -> dict | None:
    for patient in list_patients():
        if patient.get("id") == patient_id:
            return patient
    return None


def search(resource_type: str, patient: str | None = None) -> list[dict]:
    items = store.load().get(resource_type, [])
    if patient is None:
        return items
    return [r for r in items if linked_patient_id(r) == patient]


def create(resource: dict) -> dict:
    data = store.load()
    data.setdefault(resource["resourceType"], []).append(resource)
    store.save(data)
    return resource
