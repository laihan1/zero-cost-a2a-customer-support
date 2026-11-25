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
- Python: 3.14.7
- CPU: Intel Core i5-12450H
- RAM: 16GB
- GPU: NVIDIA GeForce RTX 4050 Laptop GPU
- VRAM: 6GB

Local project directory:

```powershell
C:\Users\user\Documents\zero-cost-a2a-customer-support
```

For every newly opened local terminal:

```powershell
cd C:\Users\user\Documents\zero-cost-a2a-customer-support
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

## 6. Current Implementation Baseline

Baseline: Phase 4 completed and published via Git tag `v0.4.0` at commit `cf17927`.

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
- Centralized Supervisor routing and orchestration.
- Shared A2A client, registry, discovery and configuration.
- Native A2A Text and Data Parts using AgentResponse.
- Centralized communication error handling and structured response validation.
- Configurable console logging using LOG_LEVEL (default INFO).

Last verified test result at this baseline:

- 126 automated tests passed.
- 0 failed tests.

This baseline reflects the latest reported Phase 4 regression results. Always verify the latest implementation status using the roadmap, source code, Git history, and current test results.

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

Do not modify tests simply to hide implementation failures.

Do not claim complete code coverage based only on passing tests.

If tests cannot be executed, clearly state that they remain unverified.

## 10. Local LLM Requirements

Planned local LLM runtime: Ollama.

Planned models:

- Qwen 3 4B
- Qwen 3 8B

Requirements:

- No paid AI API dependency.
- Compare models using actual benchmarks.
- Measure intent classification accuracy.
- Measure response latency.
- Monitor RAM and VRAM usage.
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

At the Phase 4 baseline:

- Keyword-based intent routing.
- Hardcoded mock data.
- Predefined Agent Card URLs.
- Manual service startup.
- No local LLM integration.
- No persistent database.
- No persistent conversation memory.
- No authentication or authorization.
- Incomplete A2A task lifecycle support.
- Task cancellation is not implemented.
- Refund delivery dates are not verified.
- No actual refund transactions.
- Automated tests do not cover every failure scenario.
- No automatic retry or complete A2A task response handling.
- Clean environment installation has not been fully verified.

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
