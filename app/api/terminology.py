from fastapi import APIRouter

from app import terminology

router = APIRouter()


@router.get("/api/codes")
def codes(q: str | None = None):
    return terminology.search_codes(q or "")
