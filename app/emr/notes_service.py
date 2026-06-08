from app.fhir import resources, server


def upload_note(patient_id: str, filename: str, raw: str) -> dict:
    document = resources.build_document_reference(patient_id, filename, raw)
    return server.create(document)
