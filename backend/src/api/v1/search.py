from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import logging
from ...models.chat import ContentSearchRequest, ContentSearchResponse, ContentFilterRequest, ContentFilterResponse, ContentSearchByTopicResponse
from ...services.rag_service import RAGService
from ...services.vector_store import VectorStore
from ...services.response_validator import ResponseValidator
from ...config import settings

router = APIRouter()

# Set up logging
logger = logging.getLogger(__name__)

# Lazy initialization of services
_vector_store = None
_rag_service = None
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


def get_response_validator():
    global _response_validator
    if _response_validator is None:
        _response_validator = ResponseValidator()
    return _response_validator


@router.post("/search", response_model=ContentSearchResponse)
async def content_search_endpoint(request: ContentSearchRequest):
    """
    Search for content in the book based on a query
    """
    try:
        # Perform content search
        search_results = get_rag_service().search_content(request.query, request.k)

        response = ContentSearchResponse(
            results=search_results,
            query=request.query
        )

        return response
    except Exception as e:
        logger.error(f"Error performing content search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/section/{section_title}")
async def search_by_section_endpoint(
    section_title: str,
    k: int = Query(default=4, ge=1, le=10, description="Number of results to return")
):
    """
    Search for content by specific section title
    """
    try:
        search_results = get_rag_service().search_by_section(section_title, k)

        return {
            "section_title": section_title,
            "results": search_results,
            "query": section_title
        }
    except Exception as e:
        logger.error(f"Error searching by section: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/topic/{topic}")
async def search_by_topic_endpoint(
    topic: str,
    k: int = Query(default=4, ge=1, le=10, description="Number of results to return")
):
    """
    Search for content by specific topic
    """
    try:
        search_results = get_rag_service().search_by_topic(topic, k)

        return {
            "topic": topic,
            "results": search_results,
            "query": topic
        }
    except Exception as e:
        logger.error(f"Error searching by topic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/search/keyword/{keyword}")
async def search_by_keyword_endpoint(
    keyword: str,
    k: int = Query(default=4, ge=1, le=10, description="Number of results to return")
):
    """
    Search for content containing a specific keyword
    """
    try:
        search_results = get_rag_service().search_by_keyword(keyword, k)

        return {
            "keyword": keyword,
            "results": search_results,
            "query": keyword
        }
    except Exception as e:
        logger.error(f"Error searching by keyword: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/search/filtered", response_model=ContentFilterResponse)
async def filtered_search_endpoint(request: ContentFilterRequest):
    """
    Search for content with filters applied
    """
    try:
        # Use the advanced search functionality
        filtered_results = get_rag_service().advanced_search(request.query, request.filters, request.k)

        response = ContentFilterResponse(
            query=request.query,
            filters=request.filters,
            results=filtered_results,
            filtered_results_count=len(filtered_results)
        )

        return response
    except Exception as e:
        logger.error(f"Error performing filtered search: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary/topic/{topic}", response_model=ContentSearchByTopicResponse)
async def topic_summary_endpoint(
    topic: str,
    k: int = Query(default=4, ge=1, le=10, description="Number of results to use for summary")
):
    """
    Generate a summary for a specific topic from the book
    """
    try:
        topic_summary = get_rag_service().generate_topic_summary(topic, k)

        response = ContentSearchByTopicResponse(
            topic=topic_summary["topic"],
            summary=topic_summary["summary"],
            results_count=topic_summary["results_count"],
            content=topic_summary["content"],
            query=topic
        )

        return response
    except Exception as e:
        logger.error(f"Error generating topic summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/summary/section/{section_title}", response_model=ContentSearchByTopicResponse)
async def section_summary_endpoint(
    section_title: str,
    k: int = Query(default=4, ge=1, le=10, description="Number of results to use for summary")
):
    """
    Generate a summary for a specific section from the book
    """
    try:
        section_summary = get_rag_service().generate_section_summary(section_title, k)

        response = ContentSearchByTopicResponse(
            topic=section_summary["section"],  # Using "topic" field to store section name
            summary=section_summary["summary"],
            results_count=section_summary["results_count"],
            content=section_summary["content"],
            query=section_title
        )

        return response
    except Exception as e:
        logger.error(f"Error generating section summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")