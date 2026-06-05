from datetime import date

from app.fhir import resources, server


def _name(patient: dict) -> str:
    name = (patient.get("name") or [{}])[0]
    given = " ".join(name.get("given", []))
    return f"{given} {name.get('family', '')}".strip()


def _age(birth: str | None) -> str:
    if not birth:
        return ""
    year, month, day = (int(part) for part in birth[:10].split("-"))
    today = date.today()
    return str(today.year - year - ((today.month, today.day) < (month, day)))


def _mrn(identifiers: list[dict] | None) -> str:
    for identifier in identifiers or []:
        if identifier.get("type", {}).get("coding", [{}])[0].get("code") == "MR":
            return identifier.get("value", "")
    return ""


def _ident(patient: dict) -> str:
    sex = (patient.get("gender", "")[:1]).upper()
    age = _age(patient.get("birthDate"))
    mrn = _mrn(patient.get("identifier"))
    parts = [f"{age}{sex}" if age else "", f"DOB {patient.get('birthDate', '')}", f"MRN {mrn}" if mrn else ""]
    return " · ".join(part for part in parts if part)


def _contact(patient: dict) -> str:
    address = (patient.get("address") or [{}])[0]
    line = ", ".join(address.get("line", []))
    city = " ".join(part for part in [address.get("city", ""), address.get("state", ""), address.get("postalCode", "")] if part)
    phone = next((t.get("value", "") for t in patient.get("telecom", []) if t.get("system") == "phone"), "")
    return " · ".join(part for part in [", ".join(part for part in [line, city] if part), phone] if part)


def patient_header(patient_id: str) -> dict | None:
    patient = server.get_patient(patient_id)
    if not patient:
        return None
    return {"name": _name(patient), "ident": _ident(patient), "contact": _contact(patient)}


def patient_summaries() -> list[dict]:
    return [{"id": p["id"], "name": _name(p), "ident": _ident(p)} for p in server.list_patients()]


def chart_sections(patient_id: str) -> list[dict]:
    sections = []
    for title, resource_type, builder in resources.SECTIONS:
        items = server.search(resource_type, patient=patient_id)
        if items:
            sections.append({"title": title, "count": len(items), "rows": [builder(r) for r in items]})
    return sections


def patient_documents(patient_id: str) -> list[dict]:
    documents = []
    for doc in server.search("DocumentReference", patient=patient_id):
        view = resources.document_view(doc)
        if view:
            documents.append(view)
    return documents
