# Backend API for Physical AI & Humanoid Robotics textbook RAG system
# This file will contain the main FastAPI application

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from typing import List, Optional
import os
from pathlib import Path
import uuid
from pydantic import BaseModel

# Import required libraries for embeddings and vector database
try:
    from sentence_transformers import SentenceTransformer
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    import torch
except ImportError as e:
    print(f"Missing required packages: {e}")
    print("Please install required packages: pip install -r requirements.txt")

app = FastAPI(
    title="Physical AI & Humanoid Robotics Textbook API",
    description="RAG API for the Physical AI & Humanoid Robotics textbook",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class QueryResponse(BaseModel):
    results: List[dict]

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    sources: List[dict]

# Initialize the embedding model
model = None
qdrant_client = None

def embed_text(text: str) -> list:
    """Generate embedding for a given text using the loaded model."""
    if not model:
        raise HTTPException(status_code=500, detail="Embedding model not initialized")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        embedding = model.encode(text)
        return embedding.tolist()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

@app.on_event("startup")
async def startup_event():
    global model, qdrant_client
    try:
        print("Initializing embedding model...")
        model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model for free-tier compatibility

        print("Connecting to Qdrant...")
        # For local development, use local Qdrant instance
        qdrant_client = QdrantClient(":memory:")  # In-memory for testing, replace with actual server in production

        # Create collection if it doesn't exist
        try:
            qdrant_client.get_collection("textbook_content")
            print("Connected to existing Qdrant collection")
        except:
            print("Creating new Qdrant collection")
            qdrant_client.create_collection(
                collection_name="textbook_content",
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),  # all-MiniLM-L6-v2 outputs 384-dim vectors
            )

        print("Startup completed successfully")
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise

@app.post("/embed", summary="Embed textbook content")
async def embed_content(text: str, source: str = "unknown"):
    """
    Embed text content into the vector database.

    - **text**: The text content to embed
    - **source**: Source identifier (e.g., chapter name, section)
    """
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Text content cannot be empty")

    if len(text) > 10000:  # Limit text length to prevent abuse
        raise HTTPException(status_code=400, detail="Text content too long (max 10000 characters)")

    if not qdrant_client:
        raise HTTPException(status_code=500, detail="Qdrant client not initialized")

    try:
        # Generate embedding for the text
        embedding = embed_text(text)

        # Generate a unique ID for this text entry
        point_id = str(uuid.uuid4())

        # Store in Qdrant
        qdrant_client.upsert(
            collection_name="textbook_content",
            points=[
                models.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "text": text,
                        "source": source,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                )
            ]
        )

        return {
            "status": "success",
            "id": point_id,
            "message": "Content embedded successfully"
        }
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error embedding content: {str(e)}")

@app.post("/query", response_model=QueryResponse, summary="Semantic search in textbook content")
async def query_content(request: QueryRequest):
    """
    Perform semantic search on the embedded textbook content.

    - **query**: The search query
    - **top_k**: Number of results to return (default: 5)
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    if request.top_k <= 0 or request.top_k > 100:  # Limit results to prevent abuse
        raise HTTPException(status_code=400, detail="top_k must be between 1 and 100")

    if not qdrant_client:
        raise HTTPException(status_code=500, detail="Qdrant client not initialized")

    try:
        # Generate embedding for the query
        query_embedding = embed_text(request.query)

        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name="textbook_content",
            query_vector=query_embedding,
            limit=request.top_k,
            with_payload=True
        )

        # Format results
        results = []
        for result in search_results:
            results.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "source": result.payload.get("source", ""),
                "score": result.score,
                "timestamp": result.payload.get("timestamp", 0)
            })

        return QueryResponse(results=results)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying content: {str(e)}")

def generate_response(query: str, context: List[str]) -> str:
    """
    Generate a response based on the query and retrieved context.
    In a real implementation, this would use a language model like OpenAI or a local LLM.
    For this implementation, we'll create a simple response based on the context.
    """
    context_str = "\n\n".join(context)

    # Simple response generation based on context
    # In a production system, you would use a proper LLM here
    response = f"Based on the textbook content:\n\n{context_str}\n\nIf you need more specific information about '{query}', please refer to the relevant sections in the textbook."
    return response

@app.post("/chat", response_model=ChatResponse, summary="Chat with textbook content")
async def chat_with_textbook(request: ChatRequest):
    """
    Chat with the textbook content using RAG (Retrieval-Augmented Generation).

    - **message**: The user's message or question
    - **history**: Conversation history (optional)
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    if len(request.message) > 1000:  # Limit message length
        raise HTTPException(status_code=400, detail="Message too long (max 1000 characters)")

    if not qdrant_client:
        raise HTTPException(status_code=500, detail="Qdrant client not initialized")

    try:
        # First, search for relevant content
        query_embedding = embed_text(request.message)

        # Search in Qdrant for relevant content
        search_results = qdrant_client.search(
            collection_name="textbook_content",
            query_vector=query_embedding,
            limit=5,  # Get top 5 most relevant results
            with_payload=True
        )

        # Extract the text content from results
        context_texts = []
        sources = []
        for result in search_results:
            context_texts.append(result.payload.get("text", ""))
            sources.append({
                "id": result.id,
                "text": result.payload.get("text", "")[:200] + "...",  # Truncate for display
                "source": result.payload.get("source", ""),
                "score": result.score
            })

        # Generate a response based on the context
        response = generate_response(request.message, context_texts)

        return ChatResponse(response=response, sources=sources)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)