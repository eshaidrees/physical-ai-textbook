from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import logging
from ...models.chat import QueryRequest, QueryResponse, ChatHistoryResponse, Message
from ...services.vector_store import VectorStore
from ...services.rag_service import RAGService
from ...services.context_manager import ContextManager
from ...services.response_validator import ResponseValidator
from ...config import settings
from .validators import QueryValidator, validate_k_value, validate_message_length

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)

# Lazy initialization of services
_vector_store = None
_rag_service = None
_context_manager = None
_response_validator = None


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


def get_response_validator():
    global _response_validator
    if _response_validator is None:
        _response_validator = ResponseValidator()
    return _response_validator


@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Main chat endpoint with conversation history
    """
    try:
        # Validate the query message
        if not QueryValidator.validate_query_message(request.message):
            raise HTTPException(status_code=400, detail="Invalid query message")

        # Sanitize the query message
        sanitized_message = QueryValidator.sanitize_query_message(request.message)

        # Validate and normalize k value
        validated_k = validate_k_value(request.k)

        # Create or get conversation ID
        conversation_id = request.conversation_id or get_context_manager().create_conversation()

        # Get conversation context
        conversation_context = get_context_manager().get_conversation_context(conversation_id)

        # Process the query using RAG service
        result = get_rag_service().query(
            query=sanitized_message,
            k=validated_k,
            conversation_context=conversation_context
        )

        # Add user message to context
        get_context_manager().add_message(conversation_id, sanitized_message, "user")

        # Add bot response to context
        get_context_manager().add_message(conversation_id, result["response"], "bot")

        # Validate the response to ensure it's from book content
        is_valid = get_response_validator().validate(result["response"], result["sources"])

        # Create response
        response = QueryResponse(
            response=result["response"],
            sources=result["sources"],
            is_valid=is_valid,
            query=sanitized_message,
            conversation_id=conversation_id
        )

        return response
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/history/{conversation_id}", response_model=ChatHistoryResponse)
async def get_chat_history(conversation_id: str):
    """
    Get conversation history for a specific conversation
    """
    try:
        conversation = get_context_manager().get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Create response with conversation messages
        response = ChatHistoryResponse(
            conversation_id=conversation_id,
            messages=conversation.messages
        )

        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/chat/history/{conversation_id}")
async def clear_chat_history(conversation_id: str):
    """
    Clear conversation history for a specific conversation
    """
    try:
        get_context_manager().clear_conversation(conversation_id)
        return {"message": "Chat history cleared successfully", "conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/chat/validate-response")
async def validate_response_endpoint(query: str, response: str, sources: List[Dict[str, Any]]):
    """
    Validate a response to ensure it contains only book-sourced information
    """
    try:
        is_valid = get_response_validator().validate(response, sources)

        return {
            "response": response,
            "is_valid": is_valid,
            "query": query
        }
    except Exception as e:
        logger.error(f"Error validating response: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/chat/detect-topic-shift/{conversation_id}")
async def detect_topic_shift_endpoint(conversation_id: str, query: str):
    """
    Detect if a new query represents a topic shift from the current conversation
    """
    try:
        is_topic_shift = get_context_manager().detect_topic_shift(conversation_id, query)

        # Get topic keywords from the conversation
        conversation = get_context_manager().get_conversation(conversation_id)
        topic_keywords = []
        if conversation:
            topic_keywords = conversation.get_topic_keywords()

        return {
            "conversation_id": conversation_id,
            "query": query,
            "is_topic_shift": is_topic_shift,
            "topic_keywords": topic_keywords
        }
    except Exception as e:
        logger.error(f"Error detecting topic shift: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/chat/context-summary/{conversation_id}")
async def get_context_summary_endpoint(conversation_id: str):
    """
    Get a summary of the current conversation context
    """
    try:
        conversation = get_context_manager().get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        context_summary = conversation.get_recent_context_summary()
        topic_keywords = conversation.get_topic_keywords()

        return {
            "conversation_id": conversation_id,
            "context_summary": context_summary,
            "topic_keywords": topic_keywords,
            "message_count": len(conversation.messages)
        }
    except Exception as e:
        logger.error(f"Error getting context summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")