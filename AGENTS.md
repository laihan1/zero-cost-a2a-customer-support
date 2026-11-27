# AI Agent Development Instructions

## 1. Project Information

- Project: Zero-Cost A2A Customer Support System
- Repository: https://github.com/laihan1/zero-cost-a2a-customer-support
- Purpose: AI Engineer portfolio project
- Primary language: Python
- Communication protocol: A2A
- Transport: JSON-RPC
- Paid AI API budget: RM0

## 2. Mandatory Context Review

Before starting any development task:

1. Read README.md.
2. Read ROADMAP.md.
3. Read CHANGELOG.md.
4. Read AGENTS.md.
5. Inspect the relevant source code.
6. Inspect existing automated tests.
7. Review recent Git commits.
8. Check the current Git working tree.
9. Identify the current development milestone.
10. Identify inconsistencies between documentation and implementation.

Never assume that a planned feature has already been implemented.

Treat the actual source code and verified test results as the primary evidence of implementation status.

Do not rebuild the project from scratch.

## 3. Communication Preferences

- Explain technical concepts using simple language.
- Use Traditional Chinese for development guidance unless requested otherwise.
- Use English for source code, code comments, Git commits, and project documentation.
- Provide step-by-step instructions.
- Explain why each major change is necessary.
- Avoid unnecessary technical complexity.
- Provide exact file paths and terminal commands.
- Clearly state whether to create, append to, or replace a file.
- Wait for user confirmation before moving to the next major step.
- Explain expected results and potential errors.

## 4. Development Environment

Current development environment:

- Operating system: Windows 11
- Editor: Visual Studio Code
- Terminal: PowerShell
- Python: 3.13.15
- CPU: AMD Ryzen 5 7500F
- RAM: 32 GB
- GPU: AMD Radeon RX 7600 XT
- VRAM: 16 GB
- Ollama: 0.40.17

Previous verification environment for Phases 5.1–5.4: Windows 11 laptop with an Intel Core i5-12450H, 16 GB RAM, an NVIDIA GeForce RTX 4050 Laptop GPU with 6 GB VRAM, Python 3.14.7, and Ollama 0.40.18.

Open each new PowerShell terminal at the root of your local clone and activate the project virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Use the existing virtual environment.

Do not install unnecessary dependencies.

Verify dependency compatibility before upgrading packages.

## 5. Architecture Decisions

The project uses a modular multi-agent architecture.

Implemented agent responsibilities:

| Agent | Responsibility |
|---|---|
| Supervisor Agent | Intent classification, routing and orchestration |
| Support Agent | General customer support and FAQ |
| Order Agent | Order information and tracking |
| Refund Agent | Refund policies and eligibility |
| Product Agent | Product information, pricing and stock |

Architecture requirements:

- Preserve A2A communication between independent agents.
- Use JSON-RPC transport.
- Use Agent Cards for service discovery.
- Keep agent responsibilities separated.
- Avoid unnecessary coupling between agents.
- Centralize reusable communication logic.
- Keep business rules outside the LLM.
- Validate all AI-generated structured outputs.
- Avoid replacing A2A communication with direct Python function calls between independent agent services.

Approved Phase 5.4 design: use LLM-first routing with deterministic keyword fallback for explicitly expected LLM failures. Reject invalid customer input before routing. Apply a cooperative Supervisor-level classification deadline. Preserve the existing A2A and AgentResponse contracts with minimal changes.

## 6. Current Implementation Baseline

Released baseline: Phase 4 completed and published via Git tag `v0.4.0` at commit `cf17927`.

Current branch: `feature/phase-5-local-llm`. The Phase 5.4.7 documentation checkpoint was committed as `ccf4cc8` after regression verification on `0a6fbe0`. Local and remote HEAD matched at `ccf4cc89dbe13a13b237453e63cefca139b48dbf` at the Phase 5.5.0.6 pre-check.

Phase 5.5.0.6 environment documentation and content review are complete. Phase 5.5.1 benchmarking remains pending and requires explicit user approval.

Implemented agents:

| Agent | Port |
|---|---:|
| Support Agent | 9999 |
| Order Agent | 9998 |
| Refund Agent | 9997 |
| Product Agent | 9996 |
| Supervisor Agent | 9995 |

Current capabilities:

- A2A JSON-RPC communication.
- Agent Card discovery.
- Keyword-based intent routing.
- Customer support FAQ.
- Order tracking.
- Preliminary refund eligibility.
- Product information and recommendations.
- Refund Agent to Order Agent collaboration.
- Centralized Supervisor routing using keyword or local LLM intent resolution and the existing A2A specialist path.
- Shared A2A client, registry, discovery and configuration.
- Native A2A Text and Data Parts using AgentResponse.
- Centralized communication error handling and structured response validation.
- Configurable console logging using LOG_LEVEL (default INFO).

Verified test baselines (Phases 4–5.4 used the previous laptop):

- Phase 4 release: 126 automated tests passed.
- Phase 5.2: 63 LLM unit tests passed in 0.27 s and all 189 regression tests passed in 3.66 s.
- Phase 5.2 live client smoke test: 2/2 passed with `qwen3:4b` and matching `order` intents. First request: 5.86 s, with cold-start state unconfirmed. Warm request: 0.55 s. The test used a temporary 180-second HTTPX timeout.

- Phase 5.3: 134 targeted tests passed in 0.51 s (74 existing and 60 new). All 249 regression tests passed in 3.75 s with `LLM_ENABLED=false`. Seven live classifier cases passed at 64 tokens with `qwen3:4b` already loaded and a temporary 180-second HTTPX timeout.

- Phase 5.4.2: 139 targeted tests passed in 0.64 s, 60 validation and executor tests passed in 0.85 s, and all 302 regression tests passed in 4.31 s with `LLM_ENABLED=false`.

- Phase 5.4.3: 66 Supervisor/executor tests passed in 0.89 s, 152 shared validation/LLM tests in 0.62 s, 11 focused A2A integration tests in 1.48 s, and 321 regression tests in 4.40 s with `LLM_ENABLED=false`. Enabled-mode tests mocked inference.

- Phase 5.4.4: 79 Supervisor and executor tests passed in 1.11 s, 152 shared validation and LLM tests in 0.69 s, 11 focused integration tests in 1.48 s, and 334 full regression tests in 4.49 s with `LLM_ENABLED=false` for the service runs.

- Phase 5.4.5: 27 pipeline tests passed in 1.14 s, 79 Supervisor and executor tests in 1.10 s, 152 shared validation and LLM tests in 0.67 s, 11 focused integration tests in 1.77 s, and 361 full regression tests in 6.35 s. Each of three timing-sensitive repeats passed all seven selected tests.

- Phase 5.4.6: cold request 9.4827 s with LLM routing. All 12 warm cases used LLM routing (mean 0.5953 s end to end). All four offline workflows passed with enabled keyword fallback and with disabled keyword routing. The disabled full regression passed 361 tests in 5.87 s with Ollama reachable and 361 in 5.59 s with Ollama unavailable.

- Phase 5.4.7: 361 regression tests passed in 5.10 s with zero failures, errors, or skips. All five Agent Cards returned HTTP 200. Services and Pytest used `LLM_ENABLED=false`. Ollama was reachable at the before and after checks.

- Phase 5.5.0 desktop migration (2026-11-26): 361 regression tests passed in 30.45 s with all five agents reachable, `LLM_ENABLED=false`, and the model unloaded. All six live Supervisor smoke cases routed correctly via `qwen3:4b` with zero fallbacks. See the [desktop migration verification](README.md#phase-550-desktop-migration-verification) for settings, timings, and limitations.

Always verify the latest implementation status using the roadmap, source code, Git history, and current test results.

## 7. A2A SDK Compatibility

The current implementation was developed using A2A Python SDK 1.3.1.

Verified implementation details:

- JSON-RPC method: SendMessage
- A2A protocol version: 1.0
- HTTP header: A2A-Version: 1.0
- User role: ROLE_USER
- Agent Card endpoint: /.well-known/agent-card.json
- Agent Card interface field: supportedInterfaces
- Text message helper: a2a.helpers.new_text_message

Current response extraction uses `shared.a2a_client`: `call_agent` finds the first text part, while `call_agent_data_by_name` validates the structured Data Part before returning it.

Do not assume that examples from older A2A SDK versions are compatible.

Inspect the installed SDK and existing implementation before introducing new imports or protocol changes.

The current response extraction is specific to the implemented message response format and is not a complete handler for all A2A task responses.

## 8. Development Workflow

For every development task:

1. Understand the existing implementation.
2. Identify the actual problem or requirement.
3. Explain the proposed solution.
4. Identify affected files.
5. Identify potential risks.
6. Obtain user approval for major architectural changes.
7. Implement one logical change at a time.
8. Add or update relevant tests.
9. Run regression tests.
10. Review the results.
11. Document completed changes.
12. Prepare the next milestone.

Do not make unrelated changes.

Do not remove working functionality without justification.

Do not claim that a task is completed without supporting evidence.

## 9. Testing Requirements

Use Pytest for automated testing.

Current regression test command:

```powershell
python -m pytest tests/ -v
```

Integration tests require all five agent services to be running. Start each from the project root using `python -m agents.<agent_name>.main`. Mocked communication failure and logging tests do not require running services.

Testing requirements:

- Test newly implemented functionality.
- Test existing functionality after changes.
- Test invalid input.
- Test missing data.
- Test unavailable agent services.
- Test communication failures.
- Preserve existing text responses and customer-facing error codes.
- Verify real offline behavior, fault isolation and recovery for major communication changes.
- Test routing accuracy.
- Test LLM output validation when implemented.
- In Supervisor pipeline tests, keep validation, routing, classifier, LLM client, and response construction real. Inject HTTPX `MockTransport` at the LLM client boundary and mock specialist communication. Use real timeout contexts, synchronize in-flight cancellation and concurrent requests, and await all test-created tasks. Keep live Ollama verification separate.
- For live verification, confirm model residency before generation and use process-local configuration. Verify Agent Cards and track owned processes. Stop only test-owned or explicitly authorized services, restore authorized pre-existing services, and verify port release. Keep the same enabled Supervisor running throughout the outage and recovery sequence.

Do not modify tests simply to hide implementation failures.

Do not claim complete code coverage based only on passing tests.

If tests cannot be executed, clearly state that they remain unverified.

## 10. Local LLM Requirements

Phase 5.1 verified local setup with Ollama 0.40.18 and `qwen3:4b` at `http://localhost:11434/api/chat`.

Current shared client:

- `shared.config.load_llm_config(environ=None)` loads settings on demand and returns an immutable `LLMConfig`. The default is disabled with a 15-second HTTPX timeout.
- `shared.llm_client.chat(messages, *, response_format=None, require_complete=False)` sends non-streaming Ollama chat requests through HTTPX, forwards an optional JSON Schema, and returns validated, non-empty message text.
- The client accepts loopback HTTP origins and disables environment proxies and redirects. It preserves native HTTP status errors and uses the independent LLM exception hierarchy for client failures.
- Application logs omit sensitive payloads. The client makes one request per call. Existing A2A communication and specialist business logic remain independent of local inference.

Shared input boundary:

- `shared.customer_message.validate_customer_message(message)` requires a non-blank string of up to 400 Unicode code points with valid UTF-8 encoding. It preserves the original text and raises a sanitized `TypeError` or `ValueError` before any inference or routing. The character limit is not a guaranteed token budget.
- Invalid input reaching the Supervisor executor returns native A2A Text and Data Parts with `agent="supervisor"`, `success=false`, `data={}`, `error_code="INVALID_INPUT"`, and the message “Please provide a valid customer message of up to 400 characters.” SDK-level rejections can occur before the executor.

Supervisor intent resolution:

- `agents.supervisor_agent.supervisor_logic.resolve_intent(user_message)` assumes the Supervisor has already validated the message. It loads and validates all LLM configuration on demand, including in disabled mode.
- Disabled mode uses `detect_intent()` without an Ollama call or health check. Enabled mode awaits the existing classifier once and forwards the original customer message to the selected specialist.
- The recoverable allowlist is `LLMDisabledError`, `LLMUnavailableError`, `LLMTimeoutError`, `LLMResponseError`, `httpx.HTTPStatusError`, and confirmed expiration of the Supervisor timeout context. Each triggers one keyword fallback.
- The classification-only `asyncio.timeout()` uses `LLMConfig.timeout` (15 seconds by default). It runs concurrently with HTTPX operation timeouts. Keyword routing and specialist calls are outside the timeout context.
- Invalid configuration, unrelated `TimeoutError`, unexpected errors, and external cancellation propagate. The specialist communication handler still owns `AGENT_UNAVAILABLE`.
- Routing source values are `llm`, `keyword`, and `keyword_fallback`. Fallback reasons are `llm_disabled`, `llm_unavailable`, `llm_timeout`, `llm_response_error`, `llm_http_error`, and `classification_deadline`. Omit customer text, model output, and exception messages from these diagnostics.

Standalone classifier:

- `shared.intent_classifier.classify_intent(user_message: str) -> str` validates input before inference, limits input to 400 characters, separates system and customer messages, and independently validates structured JSON. It rejects duplicate keys and returns only `order`, `refund`, `product`, or `support`.
- The classifier enables strict completion validation, requiring `done is True` and `done_reason == "stop"`. Invalid output raises `LLMResponseError`. Existing client exceptions propagate.
- Defaults are `LLM_ENABLED=false`, `LLM_BASE_URL=http://localhost:11434`, `LLM_MODEL=qwen3:4b`, `LLM_TIMEOUT=15.0`, `LLM_TEMPERATURE=0`, `LLM_NUM_CTX=2048`, `LLM_NUM_PREDICT=64`, `LLM_THINK=false`, and `LLM_KEEP_ALIVE=10m`.
- Preserve backend validation and keep fallback limited to the approved error categories.

Models for future benchmarking:

- Qwen 3 4B
- Qwen 3 8B

Requirements:

- No paid AI API dependency.
- Compare models using actual benchmarks.
- Measure intent classification accuracy.
- Measure response latency.
- Monitor RAM and VRAM usage with tools available for the current hardware. Confirm support on the AMD desktop before selecting a GPU monitoring tool. Record Ollama model residency separately from measured utilization and peak VRAM.
- Validate structured model outputs.
- Provide a deterministic fallback when the LLM is unavailable.
- Prevent the LLM from inventing business data.
- Do not allow the LLM to directly authorize sensitive business operations.

Do not assume a larger model is automatically better.

Select the model based on measured performance and available hardware.

## 11. Database and Business Rules

Planned database: SQLite.

Requirements:

- Replace hardcoded mock data with persistent storage.
- Use synthetic customer data.
- Validate database inputs.
- Use parameterized SQL queries.
- Keep database access separated from agent routing.
- Keep refund eligibility rules deterministic.
- Validate delivery dates before confirming refund eligibility.
- Do not execute real financial transactions.

The LLM is responsible for understanding customer intent.

The backend is responsible for enforcing business rules.

The database is responsible for providing factual business information.

## 12. Security Requirements

Never expose or commit:

- API keys.
- Passwords.
- Authentication tokens.
- Real customer information.
- Private credentials.
- Sensitive environment variables.
- Local virtual environments.
- Large downloaded LLM model files.

Additional requirements:

- Validate external inputs.
- Treat customer messages as untrusted input.
- Treat agent responses as untrusted data until validated.
- Protect against prompt injection.
- Apply appropriate timeouts.
- Avoid exposing unnecessary internal information.
- Do not intentionally log customer messages, order IDs, credentials or full response payloads.
- Use shared communication exceptions and logging; preserve native HTTP status errors and existing fallback codes.
- Use synthetic data in public demonstrations.
- Require appropriate authentication and authorization before handling private data or sensitive operations.

Do not describe the system as production-ready unless production requirements have been implemented and verified.

## 13. Cost Constraints

The project must not require paid AI APIs.

Prefer:

- Open-source libraries.
- Local LLM inference.
- Local development tools.
- Free-tier services where feasible.

Do not subscribe to paid services without explicit user approval.

Free hosting is not guaranteed.

Zero paid API cost does not include hardware, electricity, or potential infrastructure costs.

## 14. Deployment Strategy

Planned deployment modes:

### Public Demo Mode

- Accessible to interviewers where free hosting is feasible.
- Uses synthetic data.
- May use rule-based routing.
- Demonstrates A2A communication and agent collaboration.
- Clearly indicates whether an LLM is active.

### Full Local AI Mode

- Uses Ollama and a local Qwen model.
- Demonstrates intelligent intent classification.
- Runs using local computing resources.

Planned deployment technologies:

- Streamlit
- Docker
- Docker Compose
- GitHub Actions

Do not misrepresent rule-based routing as LLM-powered reasoning.

## 15. GitHub Development Strategy

Every major development milestone must be tested, documented, committed, and pushed to GitHub.

Before preparing a commit:

1. Run relevant tests.
2. Run regression tests.
3. Review Git status and changes.
4. Check for sensitive information.
5. Update README.md where necessary.
6. Update ROADMAP.md.
7. Update CHANGELOG.md.
8. Update AGENTS.md if development rules or architecture decisions change.
9. Report completed functionality and remaining limitations.

Use Conventional Commit messages:

- feat: new functionality
- fix: bug fixes
- refactor: code improvements
- test: automated tests
- docs: documentation
- ci: continuous integration
- chore: maintenance

Example:

```powershell
git status
git diff
git add .
git status
git diff --cached
git commit -m "feat: add supervisor agent"
git push origin main
```

Review staged files before committing.

Do not automatically commit, push, create tags, or modify remote branches without user approval.

Never force-push or rewrite Git history without explicit approval.

## 16. Milestone Versioning

| Version | Milestone |
|---|---|
| v0.1.0 | A2A Foundation |
| v0.2.0 | Agent Communication |
| v0.3.0 | Multi-Agent Collaboration |
| v0.4.0 | Supervisor Architecture |
| v0.5.0 | Local AI Integration |
| v0.6.0 | Database and Frontend |
| v1.0.0 | Portfolio Release |

These are planned milestone versions.

Verify existing Git tags before creating new tags.

## 17. Known Technical Limitations

Current system limitations:
- Hardcoded mock data.
- Predefined Agent Card URLs.
- Manual service startup.
- No persistent database.
- No persistent conversation memory.
- No authentication or authorization.
- Incomplete A2A task lifecycle support.
- Task cancellation is not implemented.
- Refund delivery dates are not verified.
- No actual refund transactions.
- Automated tests do not cover every failure scenario.
- No automatic retry or complete A2A task response handling.
- A fresh virtual environment and dependency installation were verified on the desktop. CI-based regression remains unverified.

LLM verification boundaries:

- Phase 5.3 verified seven warm standalone cases using a temporary 180-second timeout. Phase 5.4.6 verified a model-unloaded Supervisor request within the default 15-second classification budget. General accuracy, broad prompt-injection resistance, and comprehensive performance remain unverified. HTTPX operation timeouts provide no strict end-to-end deadline.
- Pipeline tests simulate Ollama HTTP behavior and verify real deadline expiration, cooperative cancellation, concurrent request isolation, and response compatibility. A dependency that suppresses external cancellation can let routing continue. Scheduling, blocking work, and cancellation cleanup can delay the cooperative deadline. Live enabled-mode routing, a model-unloaded request at the default classification budget, outage fallback, and same-Supervisor recovery are verified. Cold-start fallback, server-side cancellation, and production performance remain unverified.

Phase 5.4 handoff:
- Phase 5.4.6 recovered LLM routing on Supervisor PID 28276 without restart or reconfiguration. The first recovered Order request took 5.5553 s. The warm semantic dispatch request selected Order via LLM in 0.6748 s. All owned agent processes exited and ports 9995–9999 were released. The original Ollama endpoint and model were verified after the final manual restart.
- “When are you open?” correctly reaches Support but returns a clarification prompt. The standard opening-hours request returns the business hours.
- Phase 5.4.7 worktree access issues were observed before its documentation checkpoint. The Phase 5.5.0.6 pre-check verified worktree access, a clean status, and `git diff --check` at `ccf4cc8`.

Consult the latest source code and documentation to determine which limitations have been resolved.

## 18. AI Session Handover

Before ending a major development session, provide:

### Completed

- Implemented functionality.
- Modified files.
- Verified test results.

### Pending

- Unfinished tasks.
- Unverified changes.
- Known bugs.
- Technical limitations.

### Next Step

- Recommended next development task.
- Reason for the recommendation.
- Expected outcome.

### GitHub Status

- Current branch.
- Latest verified commit.
- Uncommitted changes.
- Push status.
- Current milestone.

Never invent test results, commit hashes, or deployment status.

The GitHub repository should contain enough documentation for another AI coding agent or developer to continue the project without relying on previous conversation history.

## 19. Definition of Done

A major development milestone is complete only when:

- Planned functionality is implemented.
- Relevant tests pass.
- Regression tests pass.
- Known limitations are documented.
- Documentation matches the implementation.
- Sensitive files are excluded.
- Changes are reviewed.
- The user approves the milestone.
- GitHub upload is verified.

Prioritize correctness, maintainability, reproducibility, and measurable results over development speed.
