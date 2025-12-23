# Data Model: RAG Chatbot

## Entities

### ChatRequest
**Description**: Represents a user's query with mode and optional selected text
- **message**: string - The user's question
- **mode**: "book" | "selection" - The chat mode being used
- **selectedText**: string (optional) - The highlighted text when in selection mode
- **userId**: string (optional) - Identifier for the user session
- **language**: "en" | "ur" (optional) - Detected or specified language

### ChatResponse
**Description**: Contains the answer and sources that informed the response
- **answer**: string - The chatbot's response to the user's question
- **sources**: string[] (optional) - List of source identifiers used to generate the answer
- **language**: "en" | "ur" - The language of the response
- **timestamp**: datetime - When the response was generated

### BookContent
**Description**: Represents book chapters loaded from Markdown files
- **id**: string - Unique identifier for the content chunk
- **title**: string - Title of the chapter/section
- **content**: string - The actual text content
- **sourceFile**: string - Path to the original markdown file
- **chunkIndex**: number - Position of this chunk in the original document
- **metadata**: object - Additional metadata about the content

### Embedding
**Description**: Vector representation of book content chunks for retrieval
- **chunkId**: string - Reference to the source content chunk
- **vector**: number[] - The embedding vector values
- **content**: string - The text that was embedded
- **bookId**: string - Reference to the book this belongs to
- **createdAt**: datetime - When the embedding was generated

### UserSession
**Description**: Tracks user interactions and preferences
- **sessionId**: string - Unique identifier for the session
- **preferences**: object - User preferences (language, mode preferences)
- **history**: ChatRequest[] - Recent chat history for context
- **createdAt**: datetime - When the session started
- **lastActive**: datetime - When the session was last used

## Relationships

- **ChatRequest** → **UserSession**: Many-to-one (multiple requests per session)
- **Embedding** → **BookContent**: Many-to-one (multiple embeddings per content chunk)
- **ChatResponse** ← **ChatRequest**: One-to-one (each request generates one response)

## Validation Rules

- ChatRequest.message must not be empty
- ChatRequest.mode must be either "book" or "selection"
- If ChatRequest.mode is "selection", selectedText must not be empty
- BookContent.content must not exceed 10000 characters per chunk
- Embedding.vector must have consistent dimensions based on the embedding model
- UserSession.history should maintain only the last 10 interactions

## State Transitions

- UserSession: active → expired (after 24 hours of inactivity)
- ChatRequest: received → processing → completed