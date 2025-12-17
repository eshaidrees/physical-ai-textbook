# Physical AI & Humanoid Robotics Textbook API Documentation

This document provides comprehensive documentation for the RAG (Retrieval-Augmented Generation) API that powers the AI chatbot for the Physical AI & Humanoid Robotics textbook.

## Overview

The API provides endpoints for:
- Embedding textbook content into a vector database
- Performing semantic search on the embedded content
- Chatting with the textbook content using natural language

## Base URL

```
http://localhost:8000
```

## Endpoints

### 1. POST /embed - Embed Textbook Content

Embeds text content into the vector database for later retrieval.

#### Parameters
- `text` (string, required): The text content to embed
- `source` (string, optional): Source identifier (e.g., chapter name, section). Default: "unknown"

#### Request Example
```bash
curl -X POST "http://localhost:8000/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Physical AI represents a convergence of artificial intelligence and physical systems, where AI algorithms are tightly integrated with real-world physical processes.",
    "source": "Chapter 1: Introduction to Physical AI"
  }'
```

#### Response
```json
{
  "status": "success",
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Content embedded successfully"
}
```

#### Error Responses
- `400 Bad Request`: Text is empty or too long (>10,000 characters)
- `500 Internal Server Error`: Server error during embedding

### 2. POST /query - Semantic Search

Performs semantic search on the embedded textbook content.

#### Request Body
- `query` (string, required): The search query
- `top_k` (integer, optional): Number of results to return. Default: 5, Range: 1-100

#### Request Example
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is Physical AI?",
    "top_k": 3
  }'
```

#### Response
```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Physical AI represents a convergence of artificial intelligence and physical systems...",
      "source": "Chapter 1: Introduction to Physical AI",
      "score": 0.85,
      "timestamp": 1234567890.123
    }
  ]
}
```

#### Error Responses
- `400 Bad Request`: Query is empty or top_k is out of range
- `500 Internal Server Error`: Server error during search

### 3. POST /chat - Chat with Textbook Content

Chat with the textbook content using RAG (Retrieval-Augmented Generation).

#### Request Body
- `message` (string, required): The user's message or question
- `history` (array, optional): Conversation history (not currently used in this implementation)

#### Request Example
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain the concept of Physical AI",
    "history": []
  }'
```

#### Response
```json
{
  "response": "Based on the textbook content:\n\nPhysical AI represents a convergence of artificial intelligence and physical systems, where AI algorithms are tightly integrated with real-world physical processes.\n\nIf you need more specific information about 'Explain the concept of Physical AI', please refer to the relevant sections in the textbook.",
  "sources": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "text": "Physical AI represents a convergence of artificial intelligence and physical...",
      "source": "Chapter 1: Introduction to Physical AI",
      "score": 0.85
    }
  ]
}
```

#### Error Responses
- `400 Bad Request`: Message is empty or too long (>1000 characters)
- `500 Internal Server Error`: Server error during chat processing

## Running the API

To run the API locally:

1. Ensure Python 3.7+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python main.py`
4. The API will be available at `http://localhost:8000`
5. API documentation will be available at `http://localhost:8000/docs`

## Configuration

The API uses the following configuration:

- **Embedding Model**: `all-MiniLM-L6-v2` (lightweight, free-tier friendly)
- **Vector Database**: Qdrant (in-memory for local development)
- **Port**: 8000
- **CORS**: All origins allowed (change in production)

## Security Considerations

- Input validation is implemented to prevent abuse
- Rate limiting should be added in production
- Authentication may be needed for sensitive operations
- CORS settings should be restricted in production