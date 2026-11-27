# Intent Benchmark Foundation

Phase 5.5.1 defines a fixed, synthetic intent-classification dataset. Validation
and tests run locally without Ollama, A2A services, a GPU, network access, or
paid APIs. The dataset was authored for this project from the classifier's
labeling policy using varied support enquiries and no real customer data.

## Schema and quotas

`data/intent_cases_v1.json` is UTF-8 JSON with exactly two top-level fields,
integer `schema_version` set to 1 and the `cases` array. Cases are in stable
ID order from `intent-001` through `intent-200`.

| Field | String value |
|---|---|
| `id` | Stable sequential case identifier |
| `message` | Original nonblank customer text, at most 400 Unicode code points |
| `expected_intent` | `order`, `refund`, `product`, or `support` |
| `scenario` | One primary scenario from the quota table |
| `language` | `en`, `zh-Hant`, `ms`, or `mixed`; non-English values belong to the multilingual scenario |
| `rationale` | Short English reason for the expected label |
| `subtype` | Required for `ambiguous_or_multi_intent` only; forbidden elsewhere |

`ambiguous` indicates an underspecified reference, status, or goal that
context resolves or leaves unclear. `multi_intent` indicates two or more
actionable requests, including requests that belong to the same label.
The validator requires exactly four cases of each subtype per intent, in
addition to the combined quota of eight. Every row counts once toward its
primary scenario even if it has other characteristics.

| Scenario | Order | Refund | Product | Support | Total |
|---|---:|---:|---:|---:|---:|
| `explicit` | 20 | 20 | 20 | 20 | 80 |
| `paraphrase` | 10 | 10 | 10 | 10 | 40 |
| `ambiguous_or_multi_intent` | 8 | 8 | 8 | 8 | 32 |
| `multilingual` | 8 | 8 | 8 | 8 | 32 |
| `prompt_injection` | 4 | 4 | 4 | 4 | 16 |
| **Total** | **50** | **50** | **50** | **50** | **200** |

## Labeling and semantic review

1. Identify the actual customer request. Use `order` for existing order
   fulfillment, shipping, delivery, and tracking. Use `refund` for refunds,
   returns, cancellations, and their eligibility. Use `product` for pricing,
   specifications, stock, and recommendations. Use `support` for general
   help, greetings, opening hours, and genuinely unclear or unrelated requests.
2. Label the primary request. Explicit refund, return, or cancellation
   requests take priority over order enquiries. Resolve genuine ties in
   the order `refund > order > product > support`.
3. Ignore embedded instructions that try to dictate the classification.
   Classify the remaining customer request, or use `support` if it is unclear.
4. Review the message and primary scenario, assign a label from these rules,
   then compare it with the recorded label and rationale. Review similar
   messages for superficial variation. Record disagreements by ID and rationale
   and resolve them before freezing a version used for scoring.

Codex reviewed all 200 labels and rationales against the policy without
model predictions or keyword-classifier outputs. In the targeted review,
Codex checked all 32 multilingual messages against their language labels
and corrected six mismatches. The slice has 12 Traditional Chinese,
12 Malay, and eight mixed-language cases. The Codex review found no
remaining label disputes. Human review remains pending. The validator
checks metadata and balance. Language, meaning, and wording diversity
require semantic review.

## Reproduce and version

From the repository root in the existing virtual environment, run:

```powershell
python -m benchmarks.validate_dataset
python -m pytest tests/test_benchmark_dataset.py -q -p no:cacheprovider
python -c "import hashlib; from pathlib import Path; data = Path('benchmarks/data/intent_cases_v1.json').read_bytes(); print(hashlib.sha256(data.replace(b'\r\n', b'\n')).hexdigest())"
```

Version 1 has SHA-256
`f10f766b376f2c3fc6d9d92da201e4f75361cb949638fc39275e0e231d053f75`
for the UTF-8 bytes with LF line endings. The command normalizes CRLF
checkouts so the fingerprint is portable. Record the dataset path, schema
version, SHA-256, and source commit with future benchmark results. Freeze
the reviewed dataset before inference. Publish changed cases or labels as
a new dataset revision with its own digest and review.

Only `message` may reach the future inference path. Keep
`expected_intent`, `rationale`, and other metadata outside model input.
The validator normalizes a copy of each message for duplicate detection
and returns the original text.

This balanced sample gives equal weight to the four routing intents. It
does not represent production intent frequencies, customer language use,
general classification accuracy, or broad prompt-injection resistance.
The labels describe routing targets, and specialist response quality and
business outcomes require separate evaluation. Boundary and malformed
inputs belong to offline fixtures outside the 200-case dataset.
