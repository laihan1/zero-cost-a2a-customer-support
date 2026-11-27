"""Load and validate the version 1 intent benchmark without running inference."""

import json
import unicodedata
from collections import Counter
from pathlib import Path

from shared.customer_message import validate_customer_message


DATASET_PATH = Path(__file__).resolve().parent / "data" / "intent_cases_v1.json"
INTENTS = ("order", "refund", "product", "support")
SCENARIO_QUOTAS = {
    "explicit": 20,
    "paraphrase": 10,
    "ambiguous_or_multi_intent": 8,
    "multilingual": 8,
    "prompt_injection": 4,
}
LANGUAGES = {"en", "zh-Hant", "ms", "mixed"}
SUBTYPE_QUOTAS = {"ambiguous": 4, "multi_intent": 4}
CASE_FIELDS = {"id", "message", "expected_intent", "scenario", "language", "rationale"}
CASE_COUNT = len(INTENTS) * sum(SCENARIO_QUOTAS.values())


class DatasetValidationError(ValueError):
    """A dataset could not be read or did not satisfy the benchmark contract."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise DatasetValidationError("JSON contains a duplicate key.")
        result[key] = value
    return result


def _reject_non_json_constant(_constant: str) -> None:
    raise DatasetValidationError("JSON contains a nonstandard constant.")


def _validate_case(case: object, index: int) -> None:
    if not isinstance(case, dict):
        raise DatasetValidationError(f"Case {index}: expected an object.")

    fields = CASE_FIELDS
    if case.get("scenario") == "ambiguous_or_multi_intent":
        fields = fields | {"subtype"}
    if case.keys() != fields:
        raise DatasetValidationError(f"Case {index}: missing or unknown fields.")
    for field in sorted(fields):
        value = case[field]
        if not isinstance(value, str):
            raise DatasetValidationError(f"Case {index}: {field} must be a string.")
        if field != "message":
            try:
                value.encode("utf-8")
            except UnicodeEncodeError:
                raise DatasetValidationError(
                    f"Case {index}: {field} must be valid Unicode."
                ) from None
    if case["expected_intent"] not in INTENTS:
        raise DatasetValidationError(f"Case {index}: unsupported expected_intent.")
    if case["scenario"] not in SCENARIO_QUOTAS:
        raise DatasetValidationError(f"Case {index}: unsupported scenario.")
    if case["language"] not in LANGUAGES:
        raise DatasetValidationError(f"Case {index}: unsupported language.")
    if (case["scenario"] == "multilingual") != (case["language"] != "en"):
        raise DatasetValidationError(f"Case {index}: language does not match scenario.")
    if "subtype" in case and case["subtype"] not in SUBTYPE_QUOTAS:
        raise DatasetValidationError(f"Case {index}: unsupported subtype.")
    if not case["rationale"].strip():
        raise DatasetValidationError(f"Case {index}: rationale must not be blank.")
    try:
        validate_customer_message(case["message"])
    except (TypeError, ValueError) as exc:
        raise DatasetValidationError(f"Case {index}: {exc}") from None


def load_dataset(path: Path = DATASET_PATH) -> list[dict]:
    """Return validated cases in file order with their original message text."""
    try:
        dataset = json.loads(
            path.read_bytes().decode("utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except UnicodeDecodeError:
        raise DatasetValidationError("Dataset must be valid UTF-8.") from None
    except json.JSONDecodeError as exc:
        raise DatasetValidationError(
            f"Malformed JSON at line {exc.lineno}, column {exc.colno}."
        ) from None
    except DatasetValidationError:
        raise
    except (OSError, ValueError, RecursionError):
        raise DatasetValidationError("Dataset could not be read or decoded.") from None

    if not isinstance(dataset, dict) or dataset.keys() != {"schema_version", "cases"}:
        raise DatasetValidationError("Expected exactly schema_version and cases.")
    if type(dataset["schema_version"]) is not int or dataset["schema_version"] != 1:
        raise DatasetValidationError("schema_version must be integer 1.")
    cases = dataset["cases"]
    if not isinstance(cases, list) or len(cases) != CASE_COUNT:
        raise DatasetValidationError(f"Expected exactly {CASE_COUNT} cases in an array.")

    ids = set()
    messages = set()
    quotas = Counter()
    subtype_counts = Counter()
    for index, case in enumerate(cases, start=1):
        _validate_case(case, index)
        case_id = case["id"]
        if case_id in ids:
            raise DatasetValidationError(f"Case {index}: duplicate ID.")
        if case_id != f"intent-{index:03d}":
            raise DatasetValidationError(f"Case {index}: ID must match its sequence.")
        ids.add(case_id)

        folded = unicodedata.normalize("NFC", case["message"]).casefold()
        normalized = " ".join(unicodedata.normalize("NFC", folded).split())
        if normalized in messages:
            raise DatasetValidationError(f"Case {index}: duplicate normalized message.")
        messages.add(normalized)
        quotas[case["expected_intent"], case["scenario"]] += 1
        if "subtype" in case:
            subtype_counts[case["expected_intent"], case["subtype"]] += 1

    for intent in INTENTS:
        for scenario, expected in SCENARIO_QUOTAS.items():
            actual = quotas[intent, scenario]
            if actual != expected:
                raise DatasetValidationError(
                    f"Quota for {intent}/{scenario}: expected {expected}, got {actual}."
                )
        for subtype, expected in SUBTYPE_QUOTAS.items():
            actual = subtype_counts[intent, subtype]
            if actual != expected:
                raise DatasetValidationError(
                    f"Subtype quota for {intent}/{subtype}: expected {expected}, got {actual}."
                )
    return cases


def main() -> int:
    try:
        cases = load_dataset()
    except DatasetValidationError as exc:
        print(f"Invalid dataset: {exc}")
        return 1
    print(f"Validated {len(cases)} benchmark cases (schema version 1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
