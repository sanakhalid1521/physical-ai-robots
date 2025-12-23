---
id: 2
title: Create RAG Chatbot Spec
stage: spec
date: 2025-12-16
surface: agent
model: Claude Sonnet 4.5
feature: rag-chatbot
branch: 1-rag-chatbot
user:
command: /sp.specify
labels: [spec, rag, chatbot]
links:
  spec: specs/1-rag-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/1-rag-chatbot/spec.md
 - specs/1-rag-chatbot/checklists/requirements.md
tests:
---

## Prompt

```text
 RAG Chatbot

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


cluster_id f642796b-80e8-4b3c-b0bc-819420941889 qdrant_client url="https://f642796b-80e8-4b3c-b0bc-819420941889.us-east4-0.gcp.cloud.qdrant.io:6333", api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.qwqu3Rfy4M8j7hH29mjBSSQXAnskQZNVHYJNxr2z2vo", cohere api key eIRMrI2BiMtrwOh9gsneELnA2G1PpJF1HZGXD6qr neon psql 'postgresql://neondb_owner:npg_qvCjVGHx9PR5@ep-purple-morning-a454lr8t-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require'
```

## Response snapshot

Created the RAG Chatbot feature specification with:
- User stories for Full Book Mode (P1), Selected Text Mode (P2), and Multilingual Support (P3)
- Functional requirements covering both chat modes, API endpoints, embedding pipeline, and LLM behavior
- Key entities including Chat Request/Response, Book Content, and Embeddings
- Success criteria with measurable outcomes for response time, accuracy, and user experience
- Quality checklist validating all requirements

## Outcome

- ✅ Impact: Created complete feature specification for RAG Chatbot
- 🧪 Tests: No tests required for specification creation
- 📁 Files: Created spec.md and requirements.md in specs/1-rag-chatbot/
- 🔁 Next prompts: Plan the RAG Chatbot implementation with /sp.plan
- 🧠 Reflection: Specification captures all requirements from user input with clear user scenarios and measurable success criteria

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Begin implementation planning