# RAG Chatbot Backend

This is the backend implementation for a Retrieval-Augmented Generation (RAG) chatbot that allows users to ask questions about book content in both English and Urdu.

## Features

- **Dual Language Support**: Handles queries in both English and Urdu
- **Two Chat Modes**:
  - Full Book Mode: Retrieve relevant chunks from entire book
  - Selected Text Mode: Use only user-highlighted text as context
- **Vector Search**: Uses Qdrant for efficient similarity search
- **Context Injection Protection**: Strictly answers only from provided context
- **Query Logging**: Stores queries and timestamps in Neon database

## Architecture

The system consists of:
- FastAPI backend with async endpoints
- Qdrant vector database for embeddings
- Neon Postgres for metadata and query logging
- OpenAI for LLM responses

## Deployment

### Environment Variables

Create a `.env` file with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
DATABASE_URL=your_neon_database_url
```

### Vercel Deployment

The project is configured for Vercel deployment with serverless functions:

1. Push code to a GitHub repository
2. Connect to Vercel and deploy
3. Add environment variables in the Vercel dashboard

### Docker Deployment

Build and run with Docker:

```bash
docker build -t rag-chatbot-backend .
docker run -p 8000:8000 -e OPENAI_API_KEY=... -e QDRANT_URL=... -e QDRANT_API_KEY=... -e DATABASE_URL=... rag-chatbot-backend
```

### Docker Compose

For local development with all services:

```bash
docker-compose up -d
```

## API Endpoints

- `POST /api/chat` - Main chat endpoint supporting both modes
- `POST /api/chat/book` - Book mode specific endpoint
- `GET /health` - Health check
- `GET /api/chat/health` - Chat service health check

## Book Ingestion

To add books to the system:

```bash
cd backend
python -m src.scripts.process_book path/to/book.md --book-id book_unique_id --title "Book Title"
```

## Development

1. Set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Run the development server:
   ```bash
   cd backend
   python -m src.api.main
   ```

## Rate Limiting

The API includes rate limiting to prevent abuse:
- 10 requests per minute per IP address

## Security

- API keys are loaded from environment variables
- Input validation on all endpoints
- Context injection protection prevents hallucinations
- CORS configured appropriately

## Monitoring

- Query logging in Neon database
- Structured logging with timestamps
- Health check endpoints

## Technologies Used

- **Framework**: FastAPI
- **Vector DB**: Qdrant Cloud
- **Database**: Neon Postgres
- **LLM**: OpenAI GPT models
- **Deployment**: Vercel (serverless)