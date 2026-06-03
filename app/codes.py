import json
from pathlib import Path

CODES_PATH = Path(__file__).resolve().parent.parent / "data" / "condition_codes.json"


def list_codes() -> list[dict]:
    return json.loads(CODES_PATH.read_text(encoding="utf-8"))


def search_codes(query: str) -> list[dict]:
    q = query.lower().strip()
    if not q:
        return list_codes()
    matches = []
    for code in list_codes():
        haystack = " ".join([code["display"], *code.get("keywords", [])]).lower()
        if q in haystack:
            matches.append(code)
    return matches
