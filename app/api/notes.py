from fastapi import APIRouter, File, UploadFile
from fastapi.responses import RedirectResponse

from app.emr import notes_service

router = APIRouter()


@router.post("/patients/{patient_id}/documents")
async def upload(patient_id: str, file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8")
    notes_service.upload_note(patient_id, file.filename, raw)
    return RedirectResponse(f"/patients/{patient_id}", status_code=303)
