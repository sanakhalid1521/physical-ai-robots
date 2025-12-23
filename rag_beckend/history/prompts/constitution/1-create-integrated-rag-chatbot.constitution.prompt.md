---
id: 1
title: Create Integrated RAG Chatbot
stage: constitution
date: 2025-12-16
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: 001-ai-k12-efficiency-paper
user:
command: /sp.constitution
labels: [constitution, rag, chatbot]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

```text
create Integrated RAG Chatbot

## Purpose
Build an integrated Retrieval-Augmented Generation (RAG) chatbot embedded inside a published book website.

## Core Rules
- Chatbot MUST answer questions only from the book content.
- If no relevant context is found, reply:
  "Is sawal ka jawab kitab ke matn mein mojood nahi hai."
- Support answering questions based on:
  1. Entire book
  2. User-selected text only
- No hallucination allowed.
- Urdu and English both supported.

## Security
- API keys must be stored in environment variables.
- No sensitive data exposure.

## Tech Constraints
- Backend: FastAPI
- Database: Neon Serverless Postgres
- Vector Store: Qdrant Cloud (Free Tier)
- LLM: OpenAI (Agents / ChatKit SDK)
- Frontend: Embedded widget inside book (Docusaurus / Next.js)

## UX Principles
- Simple chat UI
- Clear loading states
- Selected-text mode toggle
```

## Response snapshot

Updated the project constitution file (.specify/memory/constitution.md) with specific principles and requirements for the Integrated RAG Chatbot project, including:
- Context-Bound Responses principle: Chatbot must answer only from book content with specific fallback message
- Dual-Mode Operation: Support for entire book and selected text modes
- Multilingual Support: Both Urdu and English language support
- Security-First Implementation: API key storage and data exposure requirements
- Technology Stack Compliance: Specific tech stack requirements (FastAPI, Neon Postgres, Qdrant, OpenAI, Docusaurus/Next.js)
- Simple UX Design: Simple chat UI with loading states
- Security Requirements section with detailed security measures
- Development Workflow section with development practices
- Governance section with compliance requirements

## Outcome

- ✅ Impact: Created initial project constitution for RAG Chatbot project
- 🧪 Tests: No tests required for constitution creation
- 📁 Files: Updated .specify/memory/constitution.md with project-specific principles
- 🔁 Next prompts: Plan and implement RAG backend components
- 🧠 Reflection: Constitution properly captures all requirements from user input

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): Not applicable
- Next experiment (smallest change to try): Begin backend implementation following constitution