from urllib.parse import quote

from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app import codes, fhir_store

app = FastAPI(title="FHIR Chart")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def chart(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        request,
        "chart.html",
        {
            "header": fhir_store.patient_header(),
            "sections": fhir_store.chart_sections(),
            "documents": fhir_store.get_documents(),
            "codes": codes.list_codes(),
            "error": error,
        },
    )


@app.get("/api/codes")
def api_codes(q: str | None = None):
    return codes.search_codes(q or "")


@app.post("/documents")
async def upload(file: UploadFile = File(...)):
    text = (await file.read()).decode("utf-8")
    doc = fhir_store.add_document(file.filename, text)
    try:
        fhir_store.document_text(doc)
    except Exception as err:
        fhir_store.remove_document(doc["id"])
        return RedirectResponse(f"/?error={quote(str(err))}", status_code=303)
    return RedirectResponse("/", status_code=303)
