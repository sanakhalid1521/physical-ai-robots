# Quickstart: RAG Chatbot Development

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend development)
- Access to OpenAI API
- Access to Qdrant Cloud (Free Tier)
- Neon Serverless Postgres database

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-chatbot
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the backend directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   QDRANT_URL=https://your-cluster.qdrant.io:6333
   QDRANT_API_KEY=your_qdrant_api_key
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

## Running the Application

1. **Start the Backend**
   ```bash
   cd backend
   uvicorn src.api.main:app --reload --port 8000
   ```

2. **Start the Frontend** (in a separate terminal)
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Key Components

### Backend Structure
- `src/models/` - Pydantic models for data validation
- `src/services/` - Business logic services (RAG, embeddings, LLM)
- `src/api/` - FastAPI routes and application setup
- `src/utils/` - Utility functions (text processing, language detection)

### Frontend Structure
- `src/components/` - React components for the chat interface
- `src/services/` - API client for backend communication
- `src/utils/` - Helper functions (text selection)

## Development Workflow

1. **Process Book Content**
   ```bash
   python -m src.scripts.process_book --input-path /path/to/book/markdown --collection-name book_chunks
   ```

2. **Run Tests**
   ```bash
   # Backend tests
   pytest tests/

   # Frontend tests
   npm test
   ```

3. **API Documentation**
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## Common Tasks

### Add a New Book
1. Place markdown files in `data/books/{book-name}/`
2. Run the processing script: `python -m src.scripts.process_book --book-name {book-name}`
3. Verify embeddings are stored in Qdrant

### Test Chat Functionality
1. Start the backend server
2. Use the API directly or the frontend widget
3. Test both "book" and "selection" modes

### Update Embeddings
1. If book content changes, re-run the processing script
2. Old embeddings will be replaced with new ones
3. Consider versioning for production deployments