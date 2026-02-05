from fastapi import Request, HTTPException
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading


class RateLimiter:
    def __init__(self, requests: int = 10, window: int = 60):
        """
        Initialize rate limiter
        :param requests: Number of requests allowed per window
        :param window: Time window in seconds
        """
        self.requests = requests
        self.window = window
        self.requests_log: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()  # Thread safety for concurrent requests

    def is_allowed(self, identifier: str) -> bool:
        """
        Check if a request from the identifier is allowed
        :param identifier: Unique identifier for the requester (e.g., IP address)
        :return: True if allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            # Clean up old requests outside the window
            self.requests_log[identifier] = [
                req_time for req_time in self.requests_log[identifier]
                if now - req_time < self.window
            ]

            # Check if the number of requests is within the limit
            if len(self.requests_log[identifier]) < self.requests:
                # Add current request to the log
                self.requests_log[identifier].append(now)
                return True

            return False


# Default rate limiter instance (10 requests per minute per IP)
default_rate_limiter = RateLimiter(requests=10, window=60)


def get_client_ip(request: Request) -> str:
    """
    Get the client's IP address from the request
    """
    # Check for X-Forwarded-For header (common with proxies/load balancers)
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Take the first IP if multiple are provided
        return forwarded.split(",")[0].strip()

    # Check for X-Real-IP header
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # Fallback to client host
    return request.client.host


async def rate_limit_middleware(request: Request, call_next):
    """
    Middleware function to enforce rate limiting
    """
    client_ip = get_client_ip(request)

    # Skip rate limiting for health checks and static files
    if request.url.path in ["/api/v1/health", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        return response

    # Check if the request is allowed
    if not default_rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Rate limit exceeded",
                "message": f"You have exceeded the rate limit of {default_rate_limiter.requests} requests per {default_rate_limiter.window} seconds",
                "retry_after": default_rate_limiter.window
            }
        )

    response = await call_next(request)
    return response


class CustomRateLimiter:
    """
    A more customizable rate limiter that allows different limits for different endpoints
    """
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}

    def add_limiter(self, endpoint: str, requests: int, window: int):
        """
        Add a rate limiter for a specific endpoint
        :param endpoint: The endpoint path (e.g., "/api/v1/chat")
        :param requests: Number of requests allowed per window
        :param window: Time window in seconds
        """
        self.limiters[endpoint] = RateLimiter(requests, window)

    def is_allowed(self, endpoint: str, identifier: str) -> bool:
        """
        Check if a request to the endpoint is allowed for the identifier
        """
        limiter = self.limiters.get(endpoint)
        if limiter:
            return limiter.is_allowed(identifier)
        # If no specific limiter is defined, use the default
        return default_rate_limiter.is_allowed(identifier)

    def get_limiter(self, endpoint: str) -> RateLimiter:
        """
        Get the rate limiter for an endpoint, or return the default if none exists
        """
        return self.limiters.get(endpoint, default_rate_limiter)


# Example of creating specific limiters for different endpoints
custom_rate_limiter = CustomRateLimiter()

# Chat endpoint: 5 requests per minute
custom_rate_limiter.add_limiter("/api/v1/chat", requests=5, window=60)

# Search endpoint: 20 requests per minute
custom_rate_limiter.add_limiter("/api/v1/search", requests=20, window=60)

# Health check: 100 requests per minute (very permissive)
custom_rate_limiter.add_limiter("/api/v1/health", requests=100, window=60)


def get_endpoint_rate_limiter(request: Request) -> RateLimiter:
    """
    Get the appropriate rate limiter for the current endpoint
    """
    endpoint = request.url.path
    return custom_rate_limiter.get_limiter(endpoint)


def check_rate_limit(request: Request) -> bool:
    """
    Check if the current request is within the rate limit
    """
    client_ip = get_client_ip(request)
    rate_limiter = get_endpoint_rate_limiter(request)
    return rate_limiter.is_allowed(client_ip)