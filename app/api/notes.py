from urllib.parse import quote

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import RedirectResponse

from app.emr import notes_service

router = APIRouter()


@router.post("/patients/{patient_id}/documents")
async def upload(patient_id: str, file: UploadFile = File(...)):
    raw = (await file.read()).decode("utf-8")
    notes_service.upload_note(patient_id, file.filename, raw)
    return RedirectResponse(
        f"/patients/{patient_id}?uploaded={quote(file.filename or 'note')}",
        status_code=303,
    )


@router.post("/patients/{patient_id}/documents/{document_id}/delete")
async def delete(patient_id: str, document_id: str):
    deleted = notes_service.delete_note(patient_id, document_id)
    suffix = "?deleted=1" if deleted else "?error=note+not+found"
    return RedirectResponse(f"/patients/{patient_id}{suffix}", status_code=303)
