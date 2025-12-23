# Feature Specification: RAG Chatbot

**Feature Branch**: `1-rag-chatbot`
**Created**: 2025-12-16
**Status**: Draft
**Input**: User description: " RAG Chatbot

## Chat Modes
1. Full Book Mode
   - Retrieve relevant chunks from entire book

2. Selected Text Mode
   - Use only user-highlighted text as context
   - Ignore vector search

## Backend API
POST /api/chat
Request:
- message: string
- mode: "book" | "selection"
- selectedText?: string

Response:
- answer: string
- sources?: string[]

## Embedding Pipeline
- Markdown loader for book chapters
- Chunk size: 500 tokens
- Overlap: 100 tokens
- Store embeddings in Qdrant

## LLM Prompt Rules
- Answer only from provided context
- If answer not found, clearly refuse
- Keep answers concise
- Prefer Urdu if user asks in Urdu

## Performance
- Async FastAPI endpoints
- Caching for embeddings


cluster_id f642796b-80e8-4b3c-b0bc-819420941889 qdrant_client url=\"https://f642796b-80e8-4b3c-b0bc-819420941889.us-east4-0.gcp.cloud.qdrant.io:6333\", api_key=\"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.qwqu3Rfy4M8j7hH29mjBSSQXAnskQZNVHYJNxr2z2vo\", cohere api key eIRMrI2BiMtrwOh9gsneELnA2G1PpJF1HZGXD6qr neon psql 'postgresql://neondb_owner:npg_qvCjVGHx9PR5@ep-purple-morning-a454lr8t-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Full Book Mode Chat (Priority: P1)

A user wants to ask questions about the entire book content and receive accurate answers based on the book's information. The user types a question and gets a response that is grounded in the book's content.

**Why this priority**: This is the core functionality of the RAG chatbot - allowing users to interact with the entire book content through natural language queries.

**Independent Test**: Can be fully tested by submitting a question in "book" mode and verifying that the response is based on book content with appropriate sources cited.

**Acceptance Scenarios**:

1. **Given** a user has access to the book content, **When** the user submits a question in "book" mode, **Then** the system returns an answer based on the book content with relevant sources.
2. **Given** a user submits a question with no relevant book content, **When** the user uses "book" mode, **Then** the system responds with "Is sawal ka jawab kitab ke matn mein mojood nahi hai."
3. **Given** a user submits a question in English or Urdu, **When** the user uses "book" mode, **Then** the system responds in the same language or preferred language.

---

### User Story 2 - Selected Text Mode Chat (Priority: P2)

A user has highlighted specific text in the book and wants to ask questions specifically about that selected text, without the system searching the entire book.

**Why this priority**: This provides a focused interaction mode that allows users to get answers based on specific sections they're reading or interested in.

**Independent Test**: Can be fully tested by selecting text, submitting a question in "selection" mode with the selected text, and verifying the response is based only on that text.

**Acceptance Scenarios**:

1. **Given** a user has selected text in the book, **When** the user submits a question in "selection" mode with the selected text, **Then** the system returns an answer based only on the selected text without vector search.

---

### User Story 3 - Multilingual Support (Priority: P3)

A user asks questions in either English or Urdu and expects appropriate responses in the same language or their preferred language.

**Why this priority**: The feature specification explicitly mentions support for both Urdu and English, which is critical for the target audience.

**Independent Test**: Can be fully tested by submitting questions in both languages and verifying appropriate language handling and responses.

**Acceptance Scenarios**:

1. **Given** a user submits a question in Urdu, **When** the user interacts with the chatbot, **Then** the system preferably responds in Urdu.
2. **Given** a user submits a question in English, **When** the user interacts with the chatbot, **Then** the system responds in English.

---

### Edge Cases

- What happens when a user submits a very long question that exceeds token limits?
- How does the system handle questions that are ambiguous or could be interpreted in multiple ways?
- What happens when the selected text is empty or invalid in selection mode?
- How does the system handle requests during high load or when the LLM service is temporarily unavailable?
- What happens when a user asks a question in a language other than English or Urdu?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support two chat modes: "book" mode that retrieves relevant chunks from the entire book and "selection" mode that uses only user-highlighted text as context
- **FR-002**: System MUST provide a backend API endpoint at POST /api/chat that accepts message, mode, and optional selectedText parameters
- **FR-003**: System MUST return responses with an answer string and optional sources array
- **FR-004**: System MUST load book chapters from Markdown files for the embedding pipeline
- **FR-005**: System MUST chunk book content with 500-token chunks and 100-token overlap for embedding
- **FR-006**: System MUST store embeddings in Qdrant vector database
- **FR-007**: System MUST answer only from provided context and respond with "Is sawal ka jawab kitab ke matn mein mojood nahi hai." when no relevant context is found
- **FR-008**: System MUST keep answers concise and to the point
- **FR-009**: System MUST prefer Urdu responses if the user asks in Urdu
- **FR-010**: System MUST implement async FastAPI endpoints for performance
- **FR-011**: System MUST implement caching for embeddings to improve performance

### Key Entities

- **Chat Request**: Represents a user's query with message text, mode ("book" or "selection"), and optional selected text
- **Chat Response**: Contains the answer string and optional array of sources that informed the response
- **Book Content**: Represents the book chapters loaded from Markdown files, processed into chunks for embedding
- **Embedding**: Represents vector representations of book content chunks stored in Qdrant for retrieval

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can submit questions and receive relevant answers from book content within 5 seconds response time
- **SC-002**: The system correctly responds with "Is sawal ka jawab kitab ke matn mein mojood nahi hai." when no relevant context is found, with 99% accuracy
- **SC-003**: Users can switch between "book" and "selection" modes seamlessly, with 95% of users successfully using both modes
- **SC-004**: The system maintains multilingual support with appropriate language detection and response, supporting both English and Urdu with 90% accuracy
- **SC-005**: The system processes and stores book content embeddings with 99% success rate during initial setup