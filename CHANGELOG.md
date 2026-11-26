# Changelog

All notable changes to the Zero-Cost A2A Customer Support System will be documented in this file.

## [Unreleased]

### Phase 5.1 — Local LLM Environment Setup

- Completed standalone setup with Ollama 0.40.18 and `qwen3:4b` (2.5 GB download).
- JSON mode produced incorrect or unsupported intents. JSON Schema with enum constraints passed 4/4 smoke cases, with a mean latency of 1.46 s across those cases.
- Recorded 100% GPU offloading, 2844 MiB observed GPU memory usage, and approximately 51 tokens/sec during warm generation.
- Recorded standalone performance observations for the initial cold start (134.14 s) and refund case (4.59 s). At this milestone, Supervisor integration and broader benchmarking were pending.

### Phase 5.2 — Shared Local LLM Client

- Added immutable `LLMConfig`, on-demand `load_llm_config(environ=None)`, and an independent LLM exception hierarchy.
- Added async `chat(messages, *, response_format=None)` using the existing HTTPX dependency. The client defaults to disabled, restricts requests to loopback HTTP, disables environment proxies and redirects, and makes a single request per call.
- Preserved native HTTP status errors, validated the response envelope and non-empty message content, and kept sensitive payloads out of application logs.
- Passed 63 new LLM unit tests in 0.27 s and all 189 regression tests in 3.66 s, up from the Phase 4 baseline of 126 tests.
- Passed 2/2 live `qwen3:4b` client smoke requests with expected and actual intent `order`. The first request took 5.86 s with an unconfirmed cold-start state. The warm request took 0.55 s. The smoke test used a temporary 180-second HTTPX timeout. The default is 15 seconds.
- Committed and pushed as `98e1468` (`feat: implement shared local Ollama client with configuration and tests`).

### Phase 5.3 — Standalone Structured Intent Classifier

#### Added

- Asynchronous local intent classification with a four-intent JSON Schema, a 400-character input limit, strict generated JSON validation, and duplicate-key rejection.
- Classifier and client tests for input validation, structured output, completion metadata, and error propagation.

#### Changed

- The shared LLM client supports opt-in completion validation. Strict mode requires `done is True` and `done_reason == "stop"`. Existing callers retain the default behavior.

#### Verified

- Passed 134 targeted tests in 0.51 s and all 249 full regression tests in 3.75 s.
- Passed 7/7 live classifier smoke tests at the existing 64-token allowance using an already-loaded `qwen3:4b` model and a temporary 180-second HTTPX timeout.
- Verified all five integration services and existing A2A and Supervisor workflows with `LLM_ENABLED=false`.

#### Known Limitations

- Phase 5.3 allowed isolated Unicode surrogates to reach request construction. Phase 5.4.2 resolves this.
- At Phase 5.3, the seven warm standalone smoke cases did not establish accuracy, broad prompt-injection resistance, model-unloaded behavior, or default-timeout reliability. Later Phase 5.4 work added Supervisor integration and deterministic fallback.
- Phase 5.3 was committed and pushed as `73aede3` (`feat: add structured local LLM intent classification`).

### Phase 5.4.2 — Input Validation Hardening

- Added a shared validator for non-blank strings of at most 400 Unicode code points. It rejects isolated surrogates before inference or routing and preserves valid text exactly.
- The Supervisor rejects invalid input at its executor boundary with sanitized `INVALID_INPUT` Text and Data Parts. Valid requests still use the existing keyword router.
- Passed 139 targeted tests in 0.64 s, 60 validation and executor tests in 0.85 s, and all 302 full regression tests in 4.31 s with `LLM_ENABLED=false`.
- The character limit does not guarantee a model token budget. SDK-level request errors may occur before the application boundary.
- Committed and pushed as `6cfb51c` (`feat: harden customer message validation before supervisor routing`).

### Phase 5.4.3 — Supervisor LLM Integration

- Added asynchronous Supervisor intent resolution using the existing LLM configuration. Enabled mode awaits the local classifier once. Disabled mode uses deterministic keyword routing without any Ollama request.
- Preserved the input validation boundary, original specialist request text, and native A2A response parts. Configuration and classification errors propagate separately from specialist communication errors.
- Passed 66 Supervisor and executor tests in 0.89 s, 152 shared validation and LLM tests in 0.62 s, 11 integration tests in 1.48 s, and all 321 regression tests in 4.40 s with `LLM_ENABLED=false`. Enabled-mode tests mocked inference.
- Committed and pushed as `0fb8484` (`feat: integrate local LLM intent classification into supervisor routing`).

### Phase 5.4.4 — Deterministic Fallback and Classification Deadline

- Added one keyword fallback for `LLMDisabledError`, `LLMUnavailableError`, `LLMTimeoutError`, `LLMResponseError`, `httpx.HTTPStatusError`, and confirmed classification deadline expiration. Unexpected errors and external cancellation still propagate.
- Added a classification-only `asyncio.timeout()` budget using `LLM_TIMEOUT` (default 15 seconds). The existing HTTPX operation timeouts run concurrently. Keyword fallback and specialist communication remain outside the timeout context.
- Added stable routing-source and fallback-reason diagnostics without logging customer text or model output.
- Passed 79 Supervisor and executor tests in 1.11 s, 152 shared validation and LLM tests in 0.69 s, 11 focused integration tests in 1.48 s, and all 334 regression tests in 4.49 s with `LLM_ENABLED=false` for the service runs.
- The deadline is cooperative. Phase 5.4.4 verified it with mocked inference. Phase 5.4.6 later verified live routing, outage fallback, and same-Supervisor recovery. Live cold-start timeout fallback and server-side cancellation remain unverified.
- Committed and pushed as `f76b984` (`feat: add deterministic LLM fallback and supervisor classification deadline`).

### Phase 5.4.5 — Comprehensive Automated Testing

- Added 27 pipeline cases using real Supervisor, classifier, and client code with HTTPX `MockTransport`. Verified four-intent routing, fallback after representative HTTP and generated-output failures, native A2A responses, and application log privacy.
- Verified late-result rejection, deadline isolation from specialist calls, propagation of unexpected cleanup errors, cooperative HTTP cancellation, and concurrent request isolation. All seven timing-sensitive cases passed in three repeat runs.
- Passed 27 pipeline tests in 1.14 s, 79 Supervisor and executor tests in 1.10 s, 152 shared validation and LLM tests in 0.67 s, 11 focused A2A integration tests in 1.77 s, and 361 full regression tests in 6.35 s. The A2A service runs used `LLM_ENABLED=false`.
- No production changes. An exploratory classifier that swallowed external cancellation returned an intent and allowed the resolver to continue.
- Committed and pushed as `0d494b2` (`test: add cross-layer LLM pipeline and concurrent request verification`).

### Phase 5.4.6 — Live Supervisor and Ollama Verification

- Verified live Supervisor routing with Ollama 0.40.18, `qwen3:4b`, and the default 15-second classification budget. The model-unloaded request used LLM routing and returned the shipped order in 9.483 s end to end.
- All 12 warm standard-workflow requests used LLM routing and returned the expected business results. Two of four semantic comparisons selected a different specialist from keyword mode. Both unknown-order requests returned `ORDER_NOT_FOUND` with the existing native response parts.
- Passed 11 focused integration tests in 1.22 s, 27 pipeline tests in 0.95 s, and 361 regression tests in 5.87 s with the live Agent services configured for disabled inference. Ollama remained reachable.
- Verified all four standard workflows during an actual Ollama outage. Enabled mode logged one `keyword_fallback` with `llm_unavailable` per request. Disabled mode used keyword routing without LLM failure diagnostics. Both preserved native response parts and expected business results.
- Verified automatic recovery on Supervisor PID 28276 without restart or reconfiguration. The first recovered request selected Order via LLM in 5.5553 s. The warm semantic dispatch request selected Order via LLM in 0.6748 s, where keywords select Support.
- Passed all 361 tests in 5.59 s with Ollama unavailable at every check. Verified task-owned agent exit and port release, and confirmed Ollama and the installed model after the final manual restart.
- “When are you open?” selected Support in both modes and returned a clarification prompt. Specialist business logic is unchanged.

- Phase 5.4.6 verification was committed and pushed as `0a6fbe0`.

### Phase 5.4.7 — Final Regression and Documentation

- Passed all 361 tests in 5.10 s with zero failures, errors, or skips. The five Agent services and Pytest used `LLM_ENABLED=false`. Ollama remained reachable at the before and after checks.
- Preserved the Phase 5.4.6 live verification and its 361-test offline regression in 5.59 s. No production source, tests, dependencies, or defaults changed.
- Reconciled milestone documentation. Direct Git worktree verification, commit, and push remain pending. Phase 5.5 benchmarking remains pending.

## [0.4.0] — Supervisor Architecture

### Added

- Centralized Agent Registry.
- Shared A2A communication client.
- Shared Agent Card discovery.
- Centralized port, URL, and timeout configuration.
- Five Agent Registry tests.
- Five shared A2A Client tests.
- Three Agent Discovery tests.
- Supervisor Agent running on port 9995.
- Rule-based Supervisor intent detection.
- Centralized agent orchestration.
- Supervisor Agent registration and Agent Card.
- Eight Supervisor Logic tests.
- Four Supervisor Integration tests.
- One additional Agent Registry test.
- Three additional Supervisor intent detection tests.
- Support Agent isolation integration test.
- Shared AgentResponse schema.
- Shared A2A response message builder.
- Native A2A structured Data Part support.
- Structured response unit and integration tests.
- Shared communication exceptions and centralized console logging.
- Configurable LOG_LEVEL environment variable.
- 49 additional discovery, client, executor failure and logging tests.

### Changed

- Refactored Support and Refund Agents to reuse shared A2A components.
- Standardized Python package imports across all four agents.
- Standardized agent startup using Python module execution.
- Removed the requirement for manual PYTHONPATH configuration.
- Updated README and development roadmap.
- Centralized all customer intent routing in Supervisor Agent.
- Refactored Support Agent to handle FAQ questions only.
- Updated existing integration tests to use Supervisor Agent as the main entry point.
- Consolidated intent detection keywords.
- Refactored all specialist agents to return structured responses.
- Extended the shared A2A client to retrieve structured data.
- Replaced refund order status text parsing with structured data access.
- Updated Supervisor Agent to forward complete structured responses.
- Preserved backward compatibility with existing text responses.
- Validated Agent Cards, response parts and structured response fields.
- Improved text extraction to find the first text part.
- Preserved existing customer-facing fallback messages and error codes.

### Removed

- Duplicated A2A communication logic.
- Legacy Support Agent discovery module.
- Duplicated routing logic in Support Agent.
- Unused Support Agent A2A client.

### Testing

- Phase 4.1 automated tests: 45/45 passed.
- Supervisor Logic: 8/8 passed.
- Supervisor Integration: 4/4 passed.
- Additional Supervisor Registry test: 1/1 passed.
- Total: 58/58 automated tests passed.
- All five agents successfully started.
- Added 9 structured response unit tests.
- Added 6 structured integration tests.
- Total: 77/77 automated tests passed.

- Phase 4.5–4.6: 126/126 automated tests passed.
- Manual Order Agent offline, fault isolation, logging and recovery checks passed.

### Release Status

- Phase 4 completed and published via Git tag `v0.4.0` at commit `cf17927`.
- The `main` branch and `v0.4.0` tag were pushed to GitHub.

## [0.3.0] — Multi-Agent Collaboration

### Added

- Refund Agent for refund policy and eligibility enquiries.
- Agent-to-agent communication between Refund Agent and Order Agent.
- Product Agent for product information, pricing, and stock availability.
- Basic product recommendation functionality.
- Product and refund routing through Support Agent.
- Reusable A2A client function.
- Refund Agent automated tests.
- Product Agent automated tests.
- Multi-agent integration tests.
- Project development roadmap.

### Improved

- Routing priority for refund, order, and product enquiries.
- Error handling for unavailable agent services.
- Multi-agent collaboration architecture.

### Testing

- Support Logic: 4/4 passed.
- Order and Support Integration: 6/6 passed.
- Refund Agent: 5/5 passed.
- Refund Integration: 5/5 passed.
- Product Agent: 6/6 passed.
- Product Integration: 6/6 passed.
- Total: 32/32 automated tests passed.

### Known Limitations

- Keyword-based intent routing.
- Hardcoded mock data.
- Predefined Agent Card URLs.
- Preliminary refund eligibility checks.
- No actual refund transactions.
- No local LLM integration.
- Manual agent service startup.
- Limited failure scenario coverage.

## [0.2.0] — Order Agent and Agent Discovery

### Added

- Order Agent.
- Mock order data.
- Order tracking functionality.
- Order status and tracking number enquiries.
- A2A client communication.
- Agent Card discovery.
- Support Agent to Order Agent communication.
- Basic service availability error handling.
- Six integration tests.

### Testing

- Total: 10 automated tests passed.

### Known Limitations

- Hardcoded order data.
- Keyword-based routing.
- Limited error handling.

## [0.1.0] — A2A Foundation

### Added

- Initial Python project structure.
- Python virtual environment configuration.
- A2A Python SDK integration.
- Support Agent.
- Agent Card endpoint.
- JSON-RPC communication.
- Basic customer support responses.
- Support logic unit tests.
- GitHub repository setup.
- Dependency configuration.
- Git ignore configuration.

### Testing

- Total: 4 automated tests passed.

### Known Limitations

- Single-agent architecture.
- Rule-based responses.
- No database or LLM integration.

## Versioning Strategy

Major development milestones will be documented using version numbers.

- v0.1.0 — A2A Foundation
- v0.2.0 — Agent Communication
- v0.3.0 — Multi-Agent Collaboration
- v0.4.0 — Supervisor Architecture
- v0.5.0 — Local AI Integration
- v0.6.0 — Database and Frontend
- v1.0.0 — Portfolio Release

Each major milestone requires functional verification, automated testing, documentation updates, and a GitHub push.
