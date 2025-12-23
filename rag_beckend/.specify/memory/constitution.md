<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.0 (initial constitution)
- Added sections: All principles and sections for RAG Chatbot project
- Templates requiring updates: N/A (initial constitution)
- Follow-up TODOs: None
-->

# Integrated RAG Chatbot Constitution

## Core Principles

### I. Context-Bound Responses
<!-- Example: I. Library-First -->
Chatbot MUST answer questions only from the book content; If no relevant context is found, reply with "Is sawal ka jawab kitab ke matn mein mojood nahi hai."; No hallucination allowed under any circumstances.
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### II. Dual-Mode Operation
<!-- Example: II. CLI Interface -->
Support answering questions based on both entire book and user-selected text only; Clear toggle mechanism required for selected-text mode.
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### III. Multilingual Support (NON-NEGOTIABLE)
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
System must support both Urdu and English languages; Responses must be in the same language as the question or user preference; Language detection and processing required.
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### IV. Security-First Implementation
<!-- Example: IV. Integration Testing -->
API keys must be stored in environment variables; No sensitive data exposure in logs, responses, or client-side code; All external service connections must use secure protocols.
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### V. Technology Stack Compliance
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
Backend: FastAPI; Database: Neon Serverless Postgres; Vector Store: Qdrant Cloud (Free Tier); LLM: OpenAI (Agents / ChatKit SDK); Frontend: Embedded widget inside book (Docusaurus / Next.js).
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

### VI. Simple UX Design


Frontend must have simple chat UI with clear loading states; User experience must be intuitive and responsive; Loading indicators required during processing.

## Security Requirements
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

API keys must be stored in environment variables; No sensitive data exposure in logs, responses, or client-side code; All external service connections must use secure protocols; Input validation required to prevent injection attacks; Rate limiting implemented to prevent abuse.
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## Development Workflow
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

All code changes must pass automated tests; Code review required before merging; Security scanning must pass before deployment; Clear documentation required for all new features; Performance benchmarks must be maintained.
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

All PRs/reviews must verify compliance with context-bound responses; Changes to core principles require explicit approval; All implementations must follow the technology stack requirements; Use CLAUDE.md for runtime development guidance.
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: 1.0.0 | **Ratified**: 2025-12-16 | **Last Amended**: 2025-12-16
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
