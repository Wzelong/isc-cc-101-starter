import json
import os
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex

STORE_PATH = Path(__file__).resolve().parents[2] / "data" / "fhir_store.json"


def load() -> dict:
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def save(store: dict) -> None:
    tmp_path = STORE_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(store, indent=2), encoding="utf-8")
    os.replace(tmp_path, STORE_PATH)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{token_hex(4)}"
