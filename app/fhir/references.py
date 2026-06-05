PATIENT = "Patient"


def patient_reference(patient_id: str) -> str:
    return f"{PATIENT}/{patient_id}"


def reference_id(reference: str | None) -> str | None:
    if not reference or "/" not in reference:
        return None
    resource_type, _, resource_id = reference.partition("/")
    return resource_id if resource_type == PATIENT else None


def references_match(reference: str | None, patient_id: str) -> bool:
    return reference_id(reference) == patient_id


def linked_patient_id(resource: dict) -> str | None:
    link = resource.get("subject") or resource.get("patient") or {}
    return reference_id(link.get("reference"))
