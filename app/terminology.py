import json
from pathlib import Path

CODES_PATH = Path(__file__).resolve().parents[1] / "data" / "condition_codes.json"


def list_codes() -> list[dict]:
    return json.loads(CODES_PATH.read_text(encoding="utf-8"))


def search_codes(query: str) -> list[dict]:
    needle = query.lower().strip()
    if not needle:
        return list_codes()
    matches = []
    for code in list_codes():
        haystack = " ".join([code.get("display", ""), *code.get("synonyms", [])]).lower()
        if needle in haystack:
            matches.append(code)
    return matches
