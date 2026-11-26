# Project Roadmap

## Project Objective

Build a zero-paid-API-cost multi-agent customer support system using the Agent-to-Agent (A2A) Protocol, local LLMs, and open-source technologies.

The project demonstrates practical AI engineering, multi-agent communication, intelligent routing, system reliability, automated testing, and deployment.

## Current Progress

- Development stage: Phases 1–4 complete. Phase 4 was published via Git tag `v0.4.0` at commit `cf17927`.
- Phase 5.4.5 automated pipeline verification committed and pushed as `0d494b2`. Phase 5.4.6 live verification is complete.
- Implemented agents: 5
- Planned agents: 5
- Automated tests: 361/361 passed (Phase 5.4.4 baseline: 334/334)
- Paid AI API cost: RM0
- Current architecture: Supervisor-based multi-agent system with shared A2A components

## Phase 1 — A2A Foundation

Target version: v0.1.0

- [x] Set up Python development environment
- [x] Install A2A Python SDK
- [x] Implement Support Agent
- [x] Implement Agent Card
- [x] Implement JSON-RPC communication
- [x] Add unit tests
- [x] Push to GitHub

## Phase 2 — Order Agent and A2A Communication

Target version: v0.2.0

- [x] Implement Order Agent
- [x] Implement mock order data
- [x] Implement order tracking
- [x] Implement A2A client
- [x] Implement Agent Card discovery
- [x] Implement agent-to-agent communication
- [x] Add basic error handling
- [x] Add integration tests
- [x] Push to GitHub

## Phase 3 — Multi-Agent Collaboration

Target version: v0.3.0

- [x] Implement Refund Agent
- [x] Implement refund policy and eligibility checks
- [x] Enable Refund Agent to communicate with Order Agent
- [x] Implement Product Agent
- [x] Implement product price and stock enquiries
- [x] Implement basic product recommendations
- [x] Integrate all four agents
- [x] Pass all 32 automated tests
- [x] Push source code to GitHub
- [x] Update project documentation
- [x] Create milestone version tag

## Phase 4 — Supervisor Agent and Architecture Refactoring

Published version: v0.4.0

### Phase 4.1 — Shared A2A Client and Agent Registry

- [x] Implement centralized Agent Registry
- [x] Implement shared A2A client
- [x] Centralize agent configuration
- [x] Implement shared Agent Card discovery
- [x] Refactor Support and Refund A2A clients
- [x] Standardize agent imports and startup commands
- [x] Remove duplicated discovery code
- [x] Add 13 automated tests
- [x] Pass all 45 regression tests

### Phase 4.2 — Supervisor Agent

- [x] Implement Supervisor Agent
- [x] Register Supervisor Agent
- [x] Implement centralized orchestration
- [x] Implement rule-based intent detection
- [x] Implement Supervisor Agent Card and A2A server
- [x] Add Supervisor unit and integration tests
- [x] Pass all 58 regression tests

### Phase 4.3 — Support Agent Routing Refactoring

- [x] Separate routing from Support Agent
- [x] Centralize intent routing in Supervisor Agent
- [x] Consolidate intent detection keywords
- [x] Remove unused Support A2A client
- [x] Update integration tests to use Supervisor
- [x] Preserve existing business functionality
- [x] Verify Support Agent isolation
- [x] Pass all 62 regression tests

### Phase 4.4 — Structured Agent Responses

- [x] Improve structured agent responses
- [x] Standardize response format
- [x] Implement shared AgentResponse schema
- [x] Support native A2A Text and Data Parts
- [x] Refactor all specialist agents
- [x] Replace refund text parsing with structured data
- [x] Implement Supervisor structured response forwarding
- [x] Maintain backward compatibility
- [x] Add 15 structured response tests
- [x] Pass all 77 regression tests

### Phase 4.5 — Error Handling and Logging

- [x] Implement shared communication exceptions
- [x] Handle connection failures, timeouts and invalid responses
- [x] Validate Agent Cards and structured responses
- [x] Implement centralized console logging
- [x] Preserve existing fallback responses and error codes

### Phase 4.6 — Testing and Documentation

- [x] Add mocked offline and communication failure tests
- [x] Verify existing routing tests and add routing failure tests
- [x] Verify real Order Agent offline behavior and recovery
- [x] Add logging configuration tests
- [x] Pass all 126 regression tests
- [x] Update documentation
- [x] Push `main` to GitHub
- [x] Create and push the `v0.4.0` milestone tag

## Phase 5 — Local LLM Integration

Target version: v0.5.0

### Phase 5.1 — Local LLM Environment Setup

- [x] Install Ollama 0.40.18 and verify the local chat API
- [x] Download `qwen3:4b` and verify GPU offloading
- [x] Run standalone intent smoke tests with JSON Schema enum constraints
- [x] Document the smoke results and proposed configuration

The initial cold start (134.14 s) and refund smoke-case latency (4.59 s) remain open for performance follow-up. See [README.md](README.md#phase-51-local-llm-environment) for the smoke-test results.

### Phase 5.2 — Shared Local LLM Client

- [x] Add on-demand immutable LLM configuration and an independent exception hierarchy
- [x] Implement standalone async Ollama chat with optional JSON Schema forwarding
- [x] Pass all 63 new LLM unit tests and all 189 automated regression tests
- [x] Pass both live Ollama client smoke requests with `qwen3:4b`
- [x] Document the client, verified results, and limitations
- [x] Commit Phase 5.2 changes as `98e1468`
- [x] Push the Phase 5.2 commit to `feature/phase-5-local-llm`

### Phase 5.3 — Standalone Structured Intent Classifier

- [x] 5.3.1 — Classifier contract and prompt
- [x] 5.3.2 — Structured JSON Schema
- [x] 5.3.3 — Strict output validation
- [x] 5.3.4 — Completion metadata and error handling
- [x] 5.3.5 — Source review, 134 targeted tests, and seven live smoke tests at 64 tokens
- [x] 5.3.6 — Full regression with LLM disabled and 249 tests passed
- [x] 5.3.7 — Update documentation
- [x] 5.3.7 — Complete manual Git worktree verification, commit, and push (`73aede3`)

### Phase 5.4 — Supervisor LLM Integration and Deterministic Fallback

Approved architecture: Use LLM-first routing with deterministic keyword fallback for explicitly expected LLM failures. Reject invalid input before routing. Enforce a cooperative Supervisor-level classification deadline and preserve the existing A2A and AgentResponse contracts.

- [x] 5.4.1 — Complete and approve the architecture review.
- [x] 5.4.2 — Share input validation across the classifier and Supervisor. Reject invalid Unicode and oversized input before routing. Verify the structured error and pass all 302 regression tests.

- [x] 5.4.2 — Complete Git checkpoint (`6cfb51c`).
- [x] 5.4.3 — Integrate the classifier into the Supervisor, preserve deterministic LLM-disabled routing, and pass all 321 regression tests.

- [x] 5.4.3 — Complete Git checkpoint (`0fb8484`).
- [x] 5.4.4 — Apply keyword fallback for approved LLM failures and confirmed deadline expiration. Verify cancellation propagation and pass all 334 regression tests.

- [x] 5.4.4 — Complete Git checkpoint (`f76b984`).
- [x] 5.4.5 — Verify routing, fallback, deadline and cancellation behavior, concurrency, and A2A response contracts through mocked HTTP transport. Pass all 361 regression tests.

- [x] 5.4.5 — Complete Git checkpoint (`0d494b2`).

- [x] 5.4.6 — Verify live cold and warm routing, semantic differences, native response compatibility, actual Ollama outage fallback, and automatic recovery on the same Supervisor. Pass all 361 tests with Ollama unavailable and inference disabled.
- [ ] 5.4.7 — Run the full regression, document verified results and limitations, and prepare a manual Git checkpoint.

### Phase 5.5 — Accuracy and Performance Benchmarking

- [ ] Build a representative dataset and measure overall and per-intent accuracy, including ambiguous, multi-intent, multilingual, and prompt-injection cases.
- [ ] Compare cold-start and warm inference latency. Evaluate the 400-character input limit and 15-second HTTPX timeout.
- [ ] Compare Qwen3 4B and 8B where hardware permits. Measure CPU, GPU, RAM, and VRAM usage.
- [ ] Document accuracy, latency, and resource trade-offs.

## Phase 6 — Database and Frontend

Target version: v0.6.0

- [ ] Integrate SQLite
- [ ] Implement database schema
- [ ] Implement seed data
- [ ] Replace hardcoded mock data
- [ ] Implement database repository layer
- [ ] Validate refund eligibility using delivery dates
- [ ] Implement simulated refund requests
- [ ] Implement conversation history
- [ ] Implement Streamlit chat interface
- [ ] Display agent execution traces
- [ ] Display agent service status
- [ ] Implement public demo mode
- [ ] Implement local AI mode
- [ ] Add database and frontend tests
- [ ] Push to GitHub

## Phase 7 — Deployment and Portfolio Release

Target version: v1.0.0

- [ ] Implement Docker configuration
- [ ] Implement Docker Compose
- [ ] Configure container networking
- [ ] Implement health checks
- [ ] Automate integration test setup
- [ ] Implement GitHub Actions CI
- [ ] Verify installation in a clean environment
- [ ] Evaluate free hosting options
- [ ] Deploy public demo if feasible
- [ ] Record local AI demonstration video
- [ ] Complete README documentation
- [ ] Add architecture diagrams
- [ ] Document known limitations
- [ ] Review software licenses
- [ ] Create GitHub Release
- [ ] Push final portfolio version

## Current Limitations

- Order and product data are stored in Python dictionaries.
- Agent discovery uses predefined Agent Card URLs.
- Refund eligibility is preliminary and does not verify delivery dates.
- Refund transactions are not actually processed.
- Agent services require manual startup.
- Server-side cancellation, cold-start fallback, and comprehensive performance and accuracy benchmarking remain unverified.
- No persistent conversation memory is available.
- Authentication and authorization are not implemented.
- Full A2A task lifecycle and cancellation are not implemented.
- Automated tests do not yet cover all failure scenarios.
- Free public hosting availability is not guaranteed.

## Development Principles

- Build incrementally.
- Understand the purpose of each component.
- Keep agent responsibilities separated.
- Avoid unnecessary complexity.
- Validate all AI-generated outputs.
- Keep business rules deterministic.
- Use synthetic data for public demonstrations.
- Never expose credentials or sensitive information.
- Measure AI performance using reproducible benchmarks.
- Maintain zero paid AI API costs.

## GitHub Milestone Strategy

For every major development milestone:

1. Complete the planned functionality.
2. Run unit and integration tests.
3. Fix identified issues.
4. Run regression tests.
5. Update README, ROADMAP, and CHANGELOG.
6. Review changes for sensitive information.
7. Create a meaningful Git commit.
8. Push changes to GitHub.
9. Create a version tag when the milestone is complete.

## Definition of Done

The project is considered portfolio-ready when:

- All five agents operate correctly.
- Agents communicate using the A2A Protocol.
- Local LLM routing is implemented and evaluated.
- Persistent database storage is available.
- Agent failures are handled gracefully.
- Automated tests pass.
- A usable frontend is available.
- Installation and startup are reproducible.
- Architecture and limitations are documented.
- A demonstration is available.
- No paid AI API is required.

## Project Notes

The roadmap represents planned development phases rather than fixed daily deadlines. Tasks, architecture, and evaluation targets may be adjusted based on testing results, hardware limitations, and deployment feasibility.
