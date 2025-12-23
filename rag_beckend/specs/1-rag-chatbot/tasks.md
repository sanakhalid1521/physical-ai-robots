# Tasks: RAG Chatbot

**Feature**: RAG Chatbot
**Branch**: 1-rag-chatbot
**Generated**: 2025-12-16

## Implementation Strategy

This implementation follows the user story priorities from the specification. User Story 1 (Full Book Mode Chat) is the core functionality and MVP. User Story 2 (Selected Text Mode) and User Story 3 (Multilingual Support) build on the foundational implementation. Each user story is designed to be independently testable and deliverable.

## Phase 1: Setup

**Goal**: Initialize project structure and configure dependencies

- [X] T001 Create backend directory structure: backend/src/{models,services,api,utils}, backend/tests, backend/requirements.txt
- [X] T002 Create frontend directory structure: frontend/src/{components,services,utils}, frontend/package.json
- [X] T003 [P] Create requirements.txt with FastAPI, Pydantic, OpenAI, Qdrant, Neon Postgres connector, langdetect, python-dotenv
- [X] T004 [P] Create package.json with React, axios, and necessary frontend dependencies
- [X] T005 Create .env file template with OPENAI_API_KEY, QDRANT_URL, QDRANT_API_KEY, DATABASE_URL placeholders
- [X] T006 Create .gitignore for Python and Node.js projects

## Phase 2: Foundational

**Goal**: Implement core infrastructure and services that all user stories depend on

- [X] T007 Initialize FastAPI app in backend/src/api/main.py with basic configuration
- [X] T008 Create environment variable loading utility in backend/src/utils/config.py
- [X] T009 [P] Create ChatRequest and ChatResponse models in backend/src/models/chat.py following data model specification
- [X] T010 [P] Create BookContent and Embedding models in backend/src/models/book.py and backend/src/models/embedding.py
- [X] T011 Create language detection utility in backend/src/utils/language_detector.py
- [X] T012 Create text processing utility in backend/src/utils/text_processor.py for chunking with 500 tokens and 100 token overlap
- [X] T013 Create markdown loader utility in backend/src/utils/markdown_loader.py
- [X] T014 Setup Qdrant client and create collection management service in backend/src/services/qdrant_service.py
- [X] T015 Setup Neon Postgres connection in backend/src/services/database_service.py
- [X] T016 Create embedding service in backend/src/services/embedding_service.py using OpenAI embeddings
- [X] T017 Create LLM service in backend/src/services/llm_service.py using OpenAI for RAG responses
- [X] T018 Create RAG service in backend/src/services/rag_service.py that orchestrates embedding, retrieval, and LLM interaction
- [X] T019 Setup API router structure in backend/src/api/chat_router.py

## Phase 3: User Story 1 - Full Book Mode Chat (Priority: P1)

**Goal**: Enable users to ask questions about the entire book content and receive accurate answers based on the book's information

**Independent Test**: Can be fully tested by submitting a question in "book" mode and verifying that the response is based on book content with appropriate sources cited.

- [X] T020 [US1] Implement book mode retrieval in backend/src/services/rag_service.py to retrieve relevant chunks from entire book
- [X] T021 [US1] Implement context building for full book mode in backend/src/services/rag_service.py
- [X] T022 [US1] Create API endpoint POST /api/chat for book mode in backend/src/api/chat_router.py
- [X] T023 [US1] Add request validation for book mode in backend/src/api/chat_router.py
- [X] T024 [US1] Implement response generation that follows context-bound rules in backend/src/services/llm_service.py
- [X] T025 [US1] Add fallback response "Is sawal ka jawab kitab ke matn mein mojood nahi hai." when no context found
- [X] T026 [US1] Add source citation to responses in backend/src/services/rag_service.py
- [X] T027 [US1] Create basic chat UI component in frontend/src/components/ChatWidget.jsx
- [X] T028 [US1] Implement API integration in frontend/src/services/api_client.js
- [X] T029 [US1] Add loading states to frontend chat UI
- [ ] T030 [US1] Test full book mode functionality with sample book content

## Phase 4: User Story 2 - Selected Text Mode Chat (Priority: P2)

**Goal**: Allow users to ask questions specifically about selected text without searching the entire book

**Independent Test**: Can be fully tested by selecting text, submitting a question in "selection" mode with the selected text, and verifying the response is based only on that text.

- [X] T031 [US2] Implement selected text mode in backend/src/services/rag_service.py to use only provided text as context
- [X] T032 [US2] Update API endpoint to handle selection mode in backend/src/api/chat_router.py
- [X] T033 [US2] Add validation to ensure selectedText is provided when mode is "selection"
- [X] T034 [US2] Create mode selector component in frontend/src/components/ModeSelector.jsx
- [X] T035 [US2] Implement text selection capture in frontend/src/utils/text_selection.js
- [X] T036 [US2] Update chat UI to support mode switching
- [ ] T037 [US2] Test selected text mode functionality with sample selections

## Phase 5: User Story 3 - Multilingual Support (Priority: P3)

**Goal**: Support both English and Urdu languages with appropriate response handling

**Independent Test**: Can be fully tested by submitting questions in both languages and verifying appropriate language handling and responses.

- [X] T038 [US3] Enhance language detection to properly identify Urdu and English in backend/src/utils/language_detector.py
- [X] T039 [US3] Update LLM service to prefer Urdu responses when input is in Urdu in backend/src/services/llm_service.py
- [X] T040 [US3] Add language parameter to API requests in backend/src/api/chat_router.py
- [X] T041 [US3] Update frontend to detect input language and display responses appropriately
- [ ] T042 [US3] Test multilingual functionality with Urdu and English inputs

## Phase 6: API & Validation

**Goal**: Implement complete API with validation and error handling

- [X] T043 Add comprehensive request validation to /api/chat endpoint in backend/src/api/chat_router.py
- [X] T044 Implement error handling for all API endpoints with appropriate status codes
- [ ] T045 Add rate limiting to prevent abuse
- [X] T046 Add request logging and monitoring
- [X] T047 Create API documentation with FastAPI's automatic docs

## Phase 7: Frontend & UI

**Goal**: Complete frontend implementation with all required features

- [ ] T048 Create complete chat UI with message history in frontend/src/components/ChatWidget.jsx
- [ ] T049 Implement text selection capture and display in frontend/src/utils/text_selection.js
- [ ] T050 Add proper loading indicators and error states to frontend
- [ ] T051 Implement responsive design for chat widget
- [ ] T052 Add accessibility features to frontend components

## Phase 8: Data Pipeline & Embeddings

**Goal**: Implement complete data pipeline for processing book content

- [ ] T053 Create script to load book markdown files and process into chunks in backend/src/scripts/process_book.py
- [ ] T054 Implement embedding generation and storage in Qdrant for book content
- [ ] T055 Add caching mechanism for embeddings to improve performance
- [ ] T056 Create utility for managing multiple books in the system

## Phase 9: Quality Assurance & Testing

**Goal**: Implement testing and quality checks to ensure requirements are met

- [ ] T057 Create unit tests for all backend services
- [ ] T058 Create integration tests for API endpoints
- [ ] T059 Implement hallucination detection tests
- [ ] T060 Create context-only enforcement tests
- [ ] T061 Add performance tests to ensure response time under 5 seconds
- [ ] T062 Create multilingual support tests

## Phase 10: Polish & Cross-Cutting Concerns

**Goal**: Finalize implementation with security, performance, and deployment considerations

- [ ] T063 Add security headers and input validation to prevent injection attacks
- [ ] T064 Implement proper error logging and monitoring
- [ ] T065 Add caching for frequently accessed embeddings
- [ ] T066 Optimize performance for handling 100 concurrent users
- [ ] T067 Create deployment configuration files
- [ ] T068 Update documentation in README.md
- [ ] T069 Perform final integration testing of all features

## Dependencies

- User Story 2 (Selected Text Mode) depends on Phase 2 (Foundational) being completed
- User Story 3 (Multilingual Support) depends on Phase 2 (Foundational) being completed
- API & Validation phase depends on all user stories' core functionality being implemented

## Parallel Execution Examples

- T003 and T004 can be executed in parallel (different files, no dependencies)
- T009, T010 can be executed in parallel (different model files)
- T027, T028 can be executed in parallel (frontend and API client development)
- T034, T035 can be executed in parallel (frontend components)

## MVP Scope

The MVP includes Phase 1 (Setup), Phase 2 (Foundational), and Phase 3 (User Story 1 - Full Book Mode Chat). This provides the core RAG functionality allowing users to ask questions about the entire book content.