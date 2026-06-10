from app.fhir import resources, server
from app.fhir.references import linked_patient_id


def upload_note(patient_id: str, filename: str, raw: str) -> dict:
    document = resources.build_document_reference(patient_id, filename, raw)
    return server.create(document)


def delete_note(patient_id: str, document_id: str) -> bool:
    for doc in server.search("DocumentReference", patient=patient_id):
        if doc.get("id") == document_id and resources.is_clinical_note(doc):
            return server.delete("DocumentReference", document_id)
    return False
