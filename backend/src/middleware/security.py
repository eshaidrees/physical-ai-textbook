"""
Security validation middleware for the RAG Chatbot API
Provides input validation, sanitization, and protection against common web vulnerabilities
"""
import re
import os
from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from urllib.parse import unquote
import html
import json
from ..utils.logging import app_logger


class SecurityValidator:
    """
    Security validation class with methods to validate and sanitize inputs
    """

    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|UNION\s+ALL)\b)",
            r"(--\s+.*$)",
            r"(\b(OR|AND)\s+[\d=']+\s*[\d=']+\s*$)",
            r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC))",
            r"('(?:--|#|/\*).*?\*/)",
        ]

        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
            r"<form[^>]*>.*?</form>",
        ]

        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"(\.{2}[/\\]){2,}",
            r"(%2e%2e%2f|%2e%2e%5c)",
        ]

        # Dangerous file extensions
        self.dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
            '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh',
            '.msi', '.msp', '.msp', '.htaccess', '.htpasswd'
        }

        self.logger = app_logger

    def validate_input(self, input_data: str) -> Dict[str, Any]:
        """
        Validate input against common attack patterns
        """
        if not isinstance(input_data, str):
            input_data = str(input_data)

        issues = []

        # Check for SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                issues.append("SQL injection attempt detected")
                break

        # Check for XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, input_data, re.IGNORECASE | re.DOTALL):
                issues.append("XSS attempt detected")
                break

        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, input_data, re.IGNORECASE):
                issues.append("Path traversal attempt detected")
                break

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "sanitized_input": self.sanitize_input(input_data) if len(issues) > 0 else input_data
        }

    def sanitize_input(self, input_data: str) -> str:
        """
        Sanitize input to remove potentially dangerous content
        """
        if not isinstance(input_data, str):
            return str(input_data)

        # HTML encode potentially dangerous characters
        sanitized = html.escape(input_data)

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        # URL decode to check for encoded attacks
        try:
            decoded = unquote(sanitized)
            # Re-encode to ensure safety
            sanitized = html.escape(decoded)
        except:
            pass  # If URL decoding fails, continue with original sanitized string

        return sanitized

    def validate_file_upload(self, filename: str, content_type: str = None, file_size: int = None) -> Dict[str, Any]:
        """
        Validate file uploads for security
        """
        issues = []

        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext in self.dangerous_extensions:
            issues.append(f"Dangerous file extension: {file_ext}")

        # Check file size if provided (limit to 10MB)
        if file_size and file_size > 10 * 1024 * 1024:  # 10MB
            issues.append("File size exceeds 10MB limit")

        # Check for path traversal in filename
        if any(pattern in filename for pattern in ['../', '..\\', '..%2f', '..%5c']):
            issues.append("Path traversal detected in filename")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    def validate_json_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate JSON payload for security issues
        """
        issues = []

        def check_recursive(obj, path=""):
            if isinstance(obj, str):
                validation_result = self.validate_input(obj)
                if not validation_result["is_valid"]:
                    issues.extend([f"{path}: {issue}" for issue in validation_result["issues"]])
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    check_recursive(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_recursive(item, f"{path}[{i}]" if path else f"[{i}]")

        check_recursive(payload)

        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    def validate_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Validate request headers for security issues
        """
        issues = []

        for header_name, header_value in headers.items():
            # Validate header name
            header_name_validation = self.validate_input(header_name)
            if not header_name_validation["is_valid"]:
                issues.append(f"Header name '{header_name}': {', '.join(header_name_validation['issues'])}")

            # Validate header value
            header_value_validation = self.validate_input(header_value)
            if not header_value_validation["is_valid"]:
                issues.append(f"Header value for '{header_name}': {', '.join(header_value_validation['issues'])}")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    def validate_url_path(self, path: str) -> Dict[str, Any]:
        """
        Validate URL path for security issues
        """
        issues = []

        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                issues.append("Path traversal attempt detected in URL path")
                break

        # Check for SQL injection in path
        for pattern in self.sql_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                issues.append("SQL injection attempt detected in URL path")
                break

        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }


# Global security validator instance
security_validator = SecurityValidator()


async def security_middleware(request: Request, call_next):
    """
    Security middleware to validate all incoming requests
    """

    # Allow FastAPI docs & schema without security checks
    if request.url.path.startswith(("/docs", "/redoc", "/openapi.json")):
        return await call_next(request)

    # Validate URL path
    path_validation = security_validator.validate_url_path(request.url.path)
    if not path_validation["is_valid"]:
        security_validator.logger.warning(
            "Security validation failed for URL path",
            extra={
                "path": request.url.path,
                "method": request.method,
            }
        )


    # Validate headers
    headers_dict = dict(request.headers)
    headers_validation = security_validator.validate_headers(headers_dict)
    if not headers_validation["is_valid"]:
        security_validator.logger.warning(
            "Security validation failed for headers",
            extra={
                "path": request.url.path,
                "method": request.method,
                "issues": headers_validation["issues"],
                "client_ip": request.client.host
            }
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid headers",
                "issues": headers_validation["issues"]
            }
        )

    # For POST/PUT requests, validate body content
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.body()
            if body:
                # Try to parse as JSON if content type suggests it
                content_type = request.headers.get("content-type", "").lower()

                if "application/json" in content_type:
                    try:
                        json_data = json.loads(body.decode("utf-8"))
                        json_validation = security_validator.validate_json_payload(json_data)
                        if not json_validation["is_valid"]:
                            security_validator.logger.warning(
                                "Security validation failed for JSON payload",
                                extra={
                                    "path": request.url.path,
                                    "method": request.method,
                                    "issues": json_validation["issues"],
                                    "client_ip": request.client.host
                                }
                            )
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": "Invalid JSON payload",
                                    "issues": json_validation["issues"]
                                }
                            )
                    except json.JSONDecodeError:
                        # If JSON parsing fails, treat as string
                        body_str = body.decode("utf-8")
                        body_validation = security_validator.validate_input(body_str)
                        if not body_validation["is_valid"]:
                            security_validator.logger.warning(
                                "Security validation failed for request body",
                                extra={
                                    "path": request.url.path,
                                    "method": request.method,
                                    "issues": body_validation["issues"],
                                    "client_ip": request.client.host
                                }
                            )
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": "Invalid request body",
                                    "issues": body_validation["issues"]
                                }
                            )
                else:
                    # For non-JSON content, validate as string
                    body_str = body.decode("utf-8")
                    body_validation = security_validator.validate_input(body_str)
                    if not body_validation["is_valid"]:
                        security_validator.logger.warning(
                            "Security validation failed for request body",
                            extra={
                                "path": request.url.path,
                                "method": request.method,
                                "issues": body_validation["issues"],
                                "client_ip": request.client.host
                            }
                        )
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": "Invalid request body",
                                "issues": body_validation["issues"]
                            }
                        )
        except Exception as e:
            security_validator.logger.error(
                f"Error during security validation: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host
                }
            )
            return JSONResponse(
                status_code=500,
                content={"error": "Security validation error"}
            )

    response = await call_next(request)
    return response


def add_security_headers(response):
    """
    Add security headers to responses
    """
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"

    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"

    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"

    # Strict transport security
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Content security policy - allow docs and swagger UI elements
    # Note: We need to allow 'unsafe-inline' for styles and 'self' for scripts to support Swagger UI
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self';"

    return response


def get_security_validator() -> SecurityValidator:
    """
    Get the global security validator instance
    """
    return security_validator