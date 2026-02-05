from fastapi import HTTPException, Request
from typing import Optional
import os


class AuthMiddleware:
    """
    Basic authentication middleware for the RAG chatbot API
    For this implementation, we're using a simple API key approach
    In production, you'd want to use more robust authentication like OAuth or JWT
    """

    @staticmethod
    async def authenticate_request(request: Request) -> bool:
        """
        Authenticate the incoming request
        For this implementation, we'll check for an optional API key
        """
        # Check for API key in header
        api_key_header = request.headers.get("X-API-Key")
        expected_api_key = os.getenv("API_KEY")  # Optional API key for basic auth

        # If an API key is configured, validate it
        if expected_api_key:
            if not api_key_header or api_key_header != expected_api_key:
                raise HTTPException(status_code=401, detail="Invalid API key")

        # For this implementation, we allow all requests if no API key is configured
        return True


# Async function that can be used as a dependency
async def require_auth(request: Request):
    """
    Dependency function to require authentication on specific endpoints
    """
    is_authenticated = await AuthMiddleware.authenticate_request(request)
    if not is_authenticated:
        raise HTTPException(status_code=401, detail="Authentication required")
    return True