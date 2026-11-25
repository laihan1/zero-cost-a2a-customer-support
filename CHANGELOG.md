# Changelog

All notable changes to the Zero-Cost A2A Customer Support System will be documented in this file.

## [Unreleased]

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

### Changed

- Refactored Support and Refund Agents to reuse shared A2A components.
- Standardized Python package imports across all four agents.
- Standardized agent startup using Python module execution.
- Removed the requirement for manual PYTHONPATH configuration.
- Updated README and development roadmap.

### Removed

- Duplicated A2A communication logic.
- Legacy Support Agent discovery module.

### Testing

- Phase 4.1 automated tests: 45/45 passed.
- Supervisor Logic: 8/8 passed.
- Supervisor Integration: 4/4 passed.
- Additional Supervisor Registry test: 1/1 passed.
- Total: 58/58 automated tests passed.
- All five agents successfully started.

### Planned

- Improved intent routing
- Structured agent responses
- Enhanced error handling and logging
- Local LLM integration

### Planned

- Supervisor Agent
- Centralized Agent Registry
- Shared A2A communication layer
- Improved intent routing
- Structured agent responses
- Enhanced error handling and logging
- Local LLM integration

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

### TestingUnreleased

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