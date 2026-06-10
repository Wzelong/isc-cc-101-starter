from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app import terminology
from app.emr import chart_service

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

DEFAULT_PATIENT = "maria"


@router.get("/", response_class=RedirectResponse)
def index():
    return RedirectResponse(f"/patients/{DEFAULT_PATIENT}")


@router.get("/patients/{patient_id}", response_class=HTMLResponse)
def chart(
    request: Request,
    patient_id: str,
    error: str | None = None,
    uploaded: str | None = None,
    deleted: str | None = None,
):
    header = chart_service.patient_header(patient_id)
    if not header:
        return RedirectResponse(f"/patients/{DEFAULT_PATIENT}")
    return templates.TemplateResponse(
        request,
        "chart.html",
        {
            "header": header,
            "sections": chart_service.chart_sections(patient_id),
            "documents": chart_service.patient_documents(patient_id),
            "codes": terminology.list_codes(),
            "patients": chart_service.patient_summaries(),
            "active_id": patient_id,
            "error": error,
            "uploaded": uploaded,
            "deleted": deleted,
        },
    )
