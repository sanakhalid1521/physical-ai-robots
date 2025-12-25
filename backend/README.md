---
title: Physical AI RAG Chatbot
emoji: 🤖
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
license: mit
---

# Physical AI RAG Backend

This is the backend service for the Physical AI & Robotics textbook RAG (Retrieval Augmented Generation) system.

## Tech Stack

- **FastAPI**: Web framework for building the API
- **Cohere**: For embeddings and language model generation
- **Qdrant Cloud**: Vector database for semantic search
- **Neon Postgres**: Cloud PostgreSQL database for document storage
- **Python 3.9+**: Programming language

## Setup for Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   # Create .env file from the template
   cp .env.example .env
   # Edit .env with your actual API keys and connection strings
   ```

3. Get required API keys:
   - **Cohere API Key**: Visit [Cohere Dashboard](https://dashboard.cohere.com/) to get your free API key
   - **Qdrant Cloud**: Sign up at [Qdrant Cloud](https://cloud-qdrant-io.preview-domain.com/) for a free tier
   - **Neon Postgres**: Create a free database at [Neon](https://neon.tech/)

4. Update your .env file with the obtained credentials:
   ```env
   COHERE_API_KEY=your-cohere-api-key-here
   QDRANT_URL=your-qdrant-url-here
   QDRANT_API_KEY=your-qdrant-api-key-here
   NEON_DB_URL=your-neon-db-url-here
   ```

5. For testing without API keys:
   - You can run the application with placeholder values in .env
   - The system will use fallback mechanisms for basic functionality
   - Full AI features will be limited without proper API keys

6. Start the server:
   ```bash
   # On Unix/Linux/Mac:
   ./start.sh

   # On Windows:
   start.bat
   ```

## Hugging Face Space Configuration

This application is designed to run on Hugging Face Spaces with Docker SDK. The following environment variables must be configured in the Space settings:

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Your Qdrant Cloud URL
- `QDRANT_API_KEY`: Your Qdrant API key
- `NEON_DB_URL`: Your Neon Postgres connection string

## Features

- **Query System**: Ask questions about Physical AI and Robotics
- **Paper Generation**: Generate research papers on AI and robotics topics
- **Multilingual Support**: Currently supports English and Urdu
- **Document Storage**: Save and retrieve documents using vector search
- **Fallback System**: Works with basic responses when API keys are not configured

## API Endpoints

- `GET /` - Health check
- `POST /api/rag/query` - Query the RAG system
- `POST /api/rag/generate-paper` - Generate a research paper
- `GET /api/health` - Health check

## Architecture

The backend follows a service-oriented architecture:

- `main.py`: FastAPI application with API endpoints
- `services.py`: Business logic for RAG operations
- `database.py`: Database operations and management