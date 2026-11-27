import json
from collections import Counter
from pathlib import Path

import pytest

from benchmarks.validate_dataset import DATASET_PATH, DatasetValidationError, load_dataset


@pytest.fixture
def dataset():
    return json.loads(DATASET_PATH.read_text(encoding="utf-8"))


def write_dataset(tmp_path: Path, dataset: dict) -> Path:
    path = tmp_path / "dataset.json"
    path.write_text(json.dumps(dataset), encoding="utf-8")
    return path


def test_checked_in_dataset_has_expected_structure_and_balance():
    cases = load_dataset()
    assert len(cases) == 200
    assert {case["language"] for case in cases} == {"en", "zh-Hant", "ms", "mixed"}
    for intent in ("order", "refund", "product", "support"):
        group = [case for case in cases if case["expected_intent"] == intent]
        assert len(group) == 50
        assert Counter(case["subtype"] for case in group if "subtype" in case) == {
            "ambiguous": 4, "multi_intent": 4
        }


@pytest.mark.parametrize(
    ("payload", "error"),
    [
        (b'{"cases": [}', "Malformed JSON"),
        (b'{"schema_version": 1, "schema_version": 1}', "duplicate key"),
        (b'{"cases": [{"id": "one", "id": "two"}]}', "duplicate key"),
        (b'{"cases": [NaN]}', "nonstandard constant"),
        (b'{"cases": ["\xff"]}', "valid UTF-8"),
    ],
)
def test_invalid_serialized_dataset(tmp_path, payload, error):
    path = tmp_path / "dataset.json"
    path.write_bytes(payload)
    with pytest.raises(DatasetValidationError, match=error):
        load_dataset(path)


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("message", 27, "message must be a string"),
        ("message", " \t\n", "must not be blank"),
        ("message", "\ud800", "must be valid Unicode"),
        ("rationale", "\udfff", "rationale must be valid Unicode"),
        ("rationale", "  ", "rationale must not be blank"),
        ("expected_intent", "billing", "unsupported expected_intent"),
        ("scenario", "other", "unsupported scenario"),
        ("language", "fr", "unsupported language"),
        ("language", "ms", "language does not match scenario"),
        ("id", "intent-999", "ID must match its sequence"),
        ("extra", "unknown", "missing or unknown fields"),
        ("subtype", "ambiguous", "missing or unknown fields"),
        ("expected_intent", "product", "Quota for"),
        ("scenario", "paraphrase", "Quota for"),
    ],
)
def test_invalid_case_fields(dataset, tmp_path, field, value, error):
    dataset["cases"][0][field] = value
    with pytest.raises(DatasetValidationError, match=error):
        load_dataset(write_dataset(tmp_path, dataset))


def test_missing_case_field(dataset, tmp_path):
    del dataset["cases"][0]["rationale"]
    with pytest.raises(DatasetValidationError, match="missing or unknown fields"):
        load_dataset(write_dataset(tmp_path, dataset))


@pytest.mark.parametrize(("subtype", "error"), [
    (None, "missing or unknown fields"),
    (1, "subtype must be a string"),
    ("unknown", "unsupported subtype"),
])
def test_ambiguous_scenario_requires_valid_subtype(dataset, tmp_path, subtype, error):
    case = next(case for case in dataset["cases"] if "subtype" in case)
    if subtype is None:
        del case["subtype"]
    else:
        case["subtype"] = subtype
    with pytest.raises(DatasetValidationError, match=error):
        load_dataset(write_dataset(tmp_path, dataset))


@pytest.mark.parametrize("intent", ["order", "refund", "product", "support"])
@pytest.mark.parametrize(
    ("original", "replacement", "ambiguous_count"),
    [("ambiguous", "multi_intent", 3), ("multi_intent", "ambiguous", 5)],
)
def test_rejects_unbalanced_subtypes_with_eight_cases(
    dataset, tmp_path, intent, original, replacement, ambiguous_count
):
    cases = [
        case for case in dataset["cases"]
        if case["expected_intent"] == intent
        and case["scenario"] == "ambiguous_or_multi_intent"
    ]
    assert len(cases) == 8
    next(case for case in cases if case["subtype"] == original)["subtype"] = replacement
    error = f"Subtype quota for {intent}/ambiguous: expected 4, got {ambiguous_count}"
    with pytest.raises(DatasetValidationError, match=error):
        load_dataset(write_dataset(tmp_path, dataset))


def test_duplicate_id(dataset, tmp_path):
    dataset["cases"][1]["id"] = dataset["cases"][0]["id"]
    with pytest.raises(DatasetValidationError, match="duplicate ID"):
        load_dataset(write_dataset(tmp_path, dataset))


@pytest.mark.parametrize("second", ["Café Straße", "  CAFE\u0301 \t STRASSE "])
def test_duplicate_message_does_not_echo_text(dataset, tmp_path, second):
    dataset["cases"][0]["message"] = "Café Straße"
    dataset["cases"][1]["message"] = second
    with pytest.raises(DatasetValidationError, match="duplicate normalized message") as caught:
        load_dataset(write_dataset(tmp_path, dataset))
    assert second not in str(caught.value)


@pytest.mark.parametrize("version", [True, "1", 1.0, 2])
def test_rejects_unsupported_schema_version(dataset, tmp_path, version):
    dataset["schema_version"] = version
    with pytest.raises(DatasetValidationError, match="schema_version must be integer 1"):
        load_dataset(write_dataset(tmp_path, dataset))


def test_rejects_unknown_top_level_field(dataset, tmp_path):
    dataset["extra"] = False
    with pytest.raises(DatasetValidationError, match="Expected exactly schema_version and cases"):
        load_dataset(write_dataset(tmp_path, dataset))


def test_rejects_wrong_total(dataset, tmp_path):
    dataset["cases"].pop()
    with pytest.raises(DatasetValidationError, match="exactly 200 cases"):
        load_dataset(write_dataset(tmp_path, dataset))


def test_accepts_400_code_points_and_preserves_original_text(dataset, tmp_path):
    text = "  " + "📦" * 396 + "e\u0301"
    assert len(text) == 400
    dataset["cases"][0]["message"] = text
    assert load_dataset(write_dataset(tmp_path, dataset))[0]["message"] == text


def test_rejects_401_code_points(dataset, tmp_path):
    dataset["cases"][0]["message"] = "📦" * 401
    with pytest.raises(DatasetValidationError, match="exceeds 400 characters"):
        load_dataset(write_dataset(tmp_path, dataset))
