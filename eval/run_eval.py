"""Validation harness for the note-extraction hypothesis.

Run a candidate extractor over labeled dev notes and score it against ground
truth: recall of documented conditions, precision, negation handling, dedup.
Module 6 replaces `stub_extractor` with a real note -> findings extractor.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV_SET = Path(__file__).resolve().parent / "dev_set"
NOTES = ROOT / "notes"


def load_cases() -> list[tuple[dict, str]]:
    cases = []
    for label_file in sorted(DEV_SET.glob("*.json")):
        label = json.loads(label_file.read_text(encoding="utf-8"))
        note_text = (NOTES / label["note_file"]).read_text(encoding="utf-8")
        cases.append((label, note_text))
    return cases


def _key(finding: dict) -> str | None:
    return finding.get("icd10") or finding.get("code")


def score(expected: list[dict], predicted: list[dict]) -> dict:
    present = [f for f in expected if f["status"] == "present"]
    predicted_keys = {_key(f) for f in predicted}
    present_keys = {_key(f) for f in present}

    matched = [f for f in present if _key(f) in predicted_keys]
    recall = len(matched) / len(present) if present else 1.0
    true_positives = [f for f in predicted if _key(f) in present_keys]
    precision = len(true_positives) / len(predicted) if predicted else 1.0

    negated = [f for f in expected if f["status"] == "negated"]
    duplicates = [f for f in expected if f["status"] == "duplicate"]
    negation_ok = all(_key(f) not in predicted_keys for f in negated)
    dedup_ok = all(_key(f) not in predicted_keys for f in duplicates)

    return {"recall": recall, "precision": precision, "negation_ok": negation_ok, "dedup_ok": dedup_ok}


def run(extractor) -> None:
    cases = load_cases()
    print(f"Eval over {len(cases)} dev case(s)\n")
    totals = {"recall": 0.0, "precision": 0.0, "negation": 0, "dedup": 0}
    for label, note in cases:
        result = score(label["findings"], extractor(note))
        totals["recall"] += result["recall"]
        totals["precision"] += result["precision"]
        totals["negation"] += int(result["negation_ok"])
        totals["dedup"] += int(result["dedup_ok"])
        print(
            f"{label['note_file']}: recall={result['recall']:.0%} precision={result['precision']:.0%} "
            f"negation={'ok' if result['negation_ok'] else 'FAIL'} dedup={'ok' if result['dedup_ok'] else 'FAIL'}"
        )
    n = len(cases) or 1
    print(
        f"\nMean recall {totals['recall'] / n:.0%} · precision {totals['precision'] / n:.0%} · "
        f"negation {totals['negation']}/{n} · dedup {totals['dedup']}/{n}"
    )


def stub_extractor(note_text: str) -> list[dict]:
    """Module 6: replace this with your real extraction (note -> findings)."""
    return []


if __name__ == "__main__":
    run(stub_extractor)
