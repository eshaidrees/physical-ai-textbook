from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from ...models.chat import QueryRequest, QueryResponse, ContentSearchRequest, ContentSearchResponse
from ...services.rag_service import RAGService
from ...services.vector_store import VectorStore
from ...services.context_manager import ContextManager
from ...config import settings

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)

# Lazy initialization of services
_vector_store = None
_rag_service = None
_context_manager = None


def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def get_rag_service():
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService(get_vector_store())
    return _rag_service


def get_context_manager():
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


@router.post("/chat-content", response_model=QueryResponse)
async def content_chat_endpoint(request: QueryRequest):
    """
    Main chat endpoint that processes user queries and returns responses based on book content
    """
    try:
        # Create or get conversation ID
        conversation_id = request.conversation_id or "default"

        # Get conversation context
        conversation_context = get_context_manager().get_conversation_context(conversation_id)

        # Process the query using RAG service
        result = get_rag_service().query(
            query=request.message,
            k=request.k,
            conversation_context=conversation_context
        )

        # Add user message to context
        get_context_manager().add_message(conversation_id, request.message, "user")

        # Add bot response to context
        get_context_manager().add_message(conversation_id, result["response"], "bot")

        # Create response
        response = QueryResponse(
            response=result["response"],
            sources=result["sources"],
            is_valid=result["is_valid"],
            query=request.message,
            conversation_id=conversation_id
        )

        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/search", response_model=ContentSearchResponse)
async def search_content(request: ContentSearchRequest):
    """
    Search for specific content in the book without generating a full response
    """
    try:
        results = get_rag_service().search_content(request.query, request.k)
        return ContentSearchResponse(results=results, query=request.query)
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get the history of a specific conversation
    """
    try:
        conversation = get_context_manager().get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {
            "conversation_id": conversation_id,
            "messages": conversation.get_context(),
            "message_count": len(conversation.messages)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/conversations/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """
    Clear the history of a specific conversation
    """
    try:
        get_context_manager().clear_conversation(conversation_id)
        return {"message": "Conversation cleared successfully", "conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")