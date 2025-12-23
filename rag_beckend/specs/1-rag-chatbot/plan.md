# Implementation Plan: RAG Chatbot

**Branch**: `1-rag-chatbot` | **Date**: 2025-12-16 | **Spec**: [link](../specs/1-rag-chatbot/spec.md)
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a Retrieval-Augmented Generation (RAG) chatbot that allows users to ask questions about book content in both English and Urdu. The system supports two modes: Full Book Mode (retrieving relevant chunks from entire book) and Selected Text Mode (using only user-highlighted text as context). The backend uses FastAPI with async endpoints, Neon Postgres for storage, and Qdrant Cloud for vector storage of embeddings.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Qdrant, OpenAI SDK, Neon Postgres connector, Pydantic
**Storage**: Neon Serverless Postgres (for metadata), Qdrant Cloud (for vector embeddings)
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: Web
**Performance Goals**: <5 seconds response time for queries, handle 100 concurrent users
**Constraints**: <200ms p95 for API calls, <1GB memory, support for both English and Urdu
**Scale/Scope**: Support 10k book queries per day, handle 1M+ document chunks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Context-Bound Responses**: All responses must be grounded in book content with no hallucination
2. **Dual-Mode Operation**: System must support both full book and selected text modes
3. **Multilingual Support**: Both Urdu and English must be supported as specified
4. **Security-First Implementation**: API keys must be in environment variables, no sensitive data exposure
5. **Technology Stack Compliance**: Must use FastAPI, Neon Postgres, Qdrant Cloud, OpenAI
6. **Simple UX Design**: Frontend must have simple chat UI with loading states

## Project Structure

### Documentation (this feature)

```text
specs/1-rag-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── chat.py          # Chat request/response models
│   │   ├── book.py          # Book content models
│   │   └── embedding.py     # Embedding models
│   ├── services/
│   │   ├── rag_service.py   # Core RAG logic
│   │   ├── embedding_service.py # Embedding generation and storage
│   │   ├── qdrant_service.py # Vector database operations
│   │   └── llm_service.py   # LLM interaction
│   ├── api/
│   │   ├── chat_router.py   # Chat API endpoints
│   │   └── main.py          # FastAPI app
│   └── utils/
│       ├── text_processor.py # Text chunking and processing
│       ├── language_detector.py # Urdu/English detection
│       └── markdown_loader.py # Markdown file processing
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
└── requirements.txt

frontend/
├── src/
│   ├── components/
│   │   ├── ChatWidget.jsx    # Main chat interface
│   │   ├── ModeSelector.jsx  # Book vs selected text mode
│   │   └── LoadingSpinner.jsx # Loading indicators
│   ├── services/
│   │   └── api_client.js     # API communication
│   └── utils/
│       └── text_selection.js # Text selection handling
└── package.json
```

**Structure Decision**: Web application structure with separate backend and frontend directories. The backend handles RAG logic, API endpoints, and data processing, while the frontend provides the chat widget embedded in the book website.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |