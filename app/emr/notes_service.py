from app.fhir import resources, server, store


def upload_note(patient_id: str, filename: str, raw: str) -> dict:
    document = {
        "resourceType": "DocumentReference",
        "id": store.new_id("doc"),
        "status": "current",
        "type": {"text": filename},
        "subject": {"reference": f"urn:uuid:{patient_id}"},
        "date": store.now_iso(),
        "content": [
            {
                "attachment": {
                    "contentType": "text/plain",
                    "title": filename,
                    "data": resources.encode_text(raw),
                }
            }
        ],
    }
    return server.create(document)
