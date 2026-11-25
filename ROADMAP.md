# Project Roadmap

## Project Objective

Build a zero-paid-API-cost multi-agent customer support system using the Agent-to-Agent (A2A) Protocol, local LLMs, and open-source technologies.

The project demonstrates practical AI engineering, multi-agent communication, intelligent routing, system reliability, automated testing, and deployment.

## Current Progress

- Development stage: Phase 4 in progress (Phase 4.1 completed)
- Implemented agents: 4
- Planned agents: 5
- Automated tests: 45/45 passed
- Paid AI API cost: RM0
- Current architecture: Rule-based multi-agent system with shared A2A components

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

Target version: v0.4.0

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

- [ ] Implement Supervisor Agent
- [ ] Register Supervisor Agent
- [ ] Implement centralized orchestration

### Phase 4.3 — Support Agent Routing Refactoring

- [ ] Separate routing from Support Agent
- [ ] Centralize intent routing
- [ ] Preserve existing agent functionality

### Phase 4.4 — Structured Agent Responses

- [ ] Improve structured agent responses
- [ ] Standardize response format

### Phase 4.5 — Error Handling and Logging

- [ ] Improve error handling
- [ ] Implement logging

### Phase 4.6 — Testing and Documentation

- [ ] Add offline agent tests
- [ ] Add routing tests
- [ ] Run regression tests
- [ ] Update documentation
- [ ] Push to GitHub
- [ ] Create milestone version tag

## Phase 5 — Local LLM Integration

Target version: v0.5.0

- [ ] Integrate Ollama
- [ ] Test Qwen 3 4B
- [ ] Test Qwen 3 8B
- [ ] Implement LLM client
- [ ] Implement intelligent intent classification
- [ ] Implement structured JSON output
- [ ] Validate LLM responses
- [ ] Implement rule-based fallback
- [ ] Create an evaluation dataset
- [ ] Benchmark classification accuracy
- [ ] Benchmark response latency
- [ ] Measure hardware resource usage
- [ ] Test prompt injection resistance
- [ ] Document benchmark results
- [ ] Push to GitHub

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

- Intent routing currently relies on keyword matching.
- Order and product data are stored in Python dictionaries.
- Agent discovery uses predefined Agent Card URLs.
- Refund eligibility is preliminary and does not verify delivery dates.
- Refund transactions are not actually processed.
- Agent services require manual startup.
- No local LLM is currently integrated.
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