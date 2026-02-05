from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any, Union
from pydantic import ValidationError
import logging
from traceback import format_exc
from ...utils.logging import app_logger
from ...utils.metrics import performance_monitor


# Create a specific logger for error handling
error_logger = logging.getLogger("error_handler")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions
    """
    error_id = f"err_{hash(request.url.path + str(exc.status_code) + str(exc.detail)) % 1000000}"

    error_details = {
        "error_id": error_id,
        "status_code": exc.status_code,
        "detail": str(exc.detail) if exc.detail else "An error occurred",
        "path": request.url.path,
        "method": request.method,
        "timestamp": "datetime.now().isoformat()"
    }

    # Log the error
    error_logger.error(
        f"HTTP Exception {exc.status_code}: {exc.detail}",
        extra=error_details
    )

    # Increment error count in metrics
    performance_monitor.collector.increment_error_count(f"http_{exc.status_code}")

    return JSONResponse(
        status_code=exc.status_code,
        content=error_details
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors
    """
    error_id = f"val_err_{hash(str(exc)) % 1000000}"

    error_details = {
        "error_id": error_id,
        "status_code": 422,
        "message": "Validation error",
        "errors": [
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            }
            for error in exc.errors()
        ],
        "path": request.url.path,
        "method": request.method,
        "timestamp": "datetime.now().isoformat()"
    }

    # Log the validation error
    error_logger.warning(
        f"Validation error for {request.url.path}",
        extra=error_details
    )

    # Increment error count in metrics
    performance_monitor.collector.increment_error_count("validation_error")

    return JSONResponse(
        status_code=422,
        content=error_details
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors
    """
    error_id = f"pydantic_err_{hash(str(exc)) % 1000000}"

    error_details = {
        "error_id": error_id,
        "status_code": 422,
        "message": "Data validation error",
        "errors": [
            {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            }
            for error in exc.errors()
        ],
        "path": request.url.path,
        "method": request.method,
        "timestamp": "datetime.now().isoformat()"
    }

    # Log the validation error
    error_logger.warning(
        f"Pydantic validation error for {request.url.path}",
        extra=error_details
    )

    # Increment error count in metrics
    performance_monitor.collector.increment_error_count("pydantic_validation_error")

    return JSONResponse(
        status_code=422,
        content=error_details
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions
    """
    error_id = f"gen_err_{hash(str(exc) + request.url.path) % 1000000}"

    # Log the full traceback
    error_logger.error(
        f"Unhandled exception in {request.url.path}: {str(exc)}",
        extra={
            "error_id": error_id,
            "exception_type": type(exc).__name__,
            "path": request.url.path,
            "method": request.method,
            "timestamp": "datetime.now().isoformat()",
            "traceback": format_exc()
        },
        exc_info=True  # Include full traceback in logs
    )

    # Increment error count in metrics
    performance_monitor.collector.increment_error_count(f"general_{type(exc).__name__}")

    # For security, don't expose internal error details to the client
    error_details = {
        "error_id": error_id,
        "status_code": 500,
        "message": "Internal server error",
        "path": request.url.path,
        "method": request.method,
        "timestamp": "datetime.now().isoformat()"
    }

    return JSONResponse(
        status_code=500,
        content=error_details
    )


async def service_unavailable_handler(request: Request, exc: Exception):
    """
    Handle service unavailable scenarios (e.g., when external services are down)
    """
    error_msg = str(exc)
    if "cohere" in error_msg.lower() or "qdrant" in error_msg.lower() or "vector" in error_msg.lower():
        error_id = f"svc_unavailable_{hash(error_msg) % 1000000}"

        logger.warning(f"External service unavailable: {error_msg}")

        # Increment error count in metrics
        performance_monitor.collector.increment_error_count("service_unavailable")

        return JSONResponse(
            status_code=503,
            content={
                "error_id": error_id,
                "error": {
                    "type": "ServiceUnavailable",
                    "message": "External service temporarily unavailable. Please try again later.",
                    "timestamp": "datetime.now().isoformat()"
                }
            },
        )
    else:
        # If it's not a known external service error, handle as general error
        return await general_exception_handler(request, exc)


# Define custom exception for when content is not found
class ContentNotFound(Exception):
    def __init__(self, query: str):
        self.query = query
        super().__init__(f"No relevant content found for query: {query}")


async def content_not_found_handler(request: Request, exc: ContentNotFound):
    """
    Handle content not found scenarios
    """
    error_id = f"content_not_found_{hash(exc.query) % 1000000}"

    logger.info(f"Content not found for query: {exc.query}")

    # Log this as an informational event
    app_logger.info(
        "Content not found",
        extra={
            "error_id": error_id,
            "query": exc.query,
            "path": request.url.path,
            "method": request.method,
            "timestamp": "datetime.now().isoformat()"
        }
    )

    return JSONResponse(
        status_code=200,  # Return 200 as this is not an error, just an informational response
        content={
            "error_id": error_id,
            "response": "I cannot find relevant information in the book for your query.",
            "sources": [],
            "is_valid": True,  # This is a valid response acknowledging the limitation
            "query": exc.query,
            "conversation_id": "unknown",  # In real implementation, this would be passed from context
            "timestamp": "datetime.now().isoformat()"
        },
    )


class CustomException(Exception):
    """
    Custom exception class for business logic errors
    """
    def __init__(self, message: str, error_code: str = None, status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class VectorStoreException(CustomException):
    """
    Exception raised when vector store operations fail
    """
    def __init__(self, message: str):
        super().__init__(message, "VECTOR_STORE_ERROR", 500)


class ConversationNotFoundException(CustomException):
    """
    Exception raised when a conversation is not found
    """
    def __init__(self, message: str = "Conversation not found"):
        super().__init__(message, "CONVERSATION_NOT_FOUND", 404)


class RateLimitExceededException(CustomException):
    """
    Exception raised when rate limit is exceeded
    """
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)


class InvalidQueryException(CustomException):
    """
    Exception raised when a query is invalid
    """
    def __init__(self, message: str = "Invalid query"):
        super().__init__(message, "INVALID_QUERY", 400)


class ResponseValidationException(CustomException):
    """
    Exception raised when response validation fails
    """
    def __init__(self, message: str = "Response validation failed"):
        super().__init__(message, "RESPONSE_VALIDATION_ERROR", 400)


def add_error_handlers(app):
    """
    Add all error handlers to the FastAPI application
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    return app


# Error response utilities
def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response
    """
    response = {
        "status_code": status_code,
        "message": message,
        "timestamp": "datetime.now().isoformat()",
        "error_code": error_code or f"ERR_{status_code}"
    }

    if details:
        response["details"] = details

    return response


def log_error_and_create_response(
    request: Request,
    error: Exception,
    status_code: int = 500,
    message: str = "An error occurred"
) -> JSONResponse:
    """
    Log an error and return an appropriate JSON response
    """
    error_id = f"log_err_{hash(str(error) + request.url.path) % 1000000}"

    error_details = {
        "error_id": error_id,
        "status_code": status_code,
        "message": str(message),
        "original_error": str(error),
        "path": request.url.path,
        "method": request.method,
        "timestamp": "datetime.now().isoformat()"
    }

    # Log the error
    app_logger.error(f"Error in {request.url.path}: {str(error)}", extra=error_details)

    # Increment error count in metrics
    performance_monitor.collector.increment_error_count(f"logged_{type(error).__name__}")

    return JSONResponse(
        status_code=status_code,
        content=error_details
    )