from typing import Optional
from pydantic import BaseModel, validator, Field
import re


class QueryValidator:
    @staticmethod
    def validate_query_message(message: str) -> bool:
        """
        Validate user input to prevent malicious queries
        """
        if not message or not message.strip():
            return False

        # Check for length limits
        if len(message) > 1000:  # Limit to 1000 characters
            return False

        # Check for potentially malicious patterns
        malicious_patterns = [
            r"(\b(select|drop|delete|update|insert)\b)",  # SQL injection
            r"(<script|javascript:|vbscript:)",  # XSS attempts
            r"(union\s+select)",  # SQL union attacks
            r"(\b(eval|exec|execute)\b)",  # Code execution attempts
        ]

        message_lower = message.lower()
        for pattern in malicious_patterns:
            if re.search(pattern, message_lower):
                return False

        # Check for excessive special characters that might indicate injection attempts
        special_char_ratio = sum(1 for c in message if not c.isalnum() and not c.isspace()) / len(message)
        if special_char_ratio > 0.5:  # If more than 50% are special characters
            return False

        return True

    @staticmethod
    def sanitize_query_message(message: str) -> str:
        """
        Sanitize the query message to remove potentially harmful content
        """
        # Remove potential script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', message, flags=re.IGNORECASE | re.DOTALL)
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'vbscript:', '', sanitized, flags=re.IGNORECASE)

        # Remove potential SQL keywords (in a non-functional way to prevent injection)
        sanitized = re.sub(r'\b(select|drop|delete|update|insert)\b', '', sanitized, flags=re.IGNORECASE)

        # Strip leading/trailing whitespace
        sanitized = sanitized.strip()

        return sanitized


class ConversationValidator:
    @staticmethod
    def validate_conversation_id(conversation_id: Optional[str]) -> bool:
        """
        Validate conversation ID format
        """
        if not conversation_id:
            return True  # Allow None/empty for creating new conversations

        # Basic validation: should be a reasonable length and contain only alphanumeric, hyphens, or underscores
        if len(conversation_id) > 100:
            return False

        # Check if it contains only allowed characters
        if not re.match(r'^[a-zA-Z0-9_-]+$', conversation_id):
            return False

        return True


# Additional validation functions for other inputs
def validate_k_value(k: int) -> int:
    """
    Validate and normalize the k value (number of results to return)
    """
    if k < 1:
        return 1
    if k > 20:  # Set a reasonable upper limit
        return 20
    return k


def validate_message_length(message: str, max_length: int = 1000) -> str:
    """
    Validate and truncate message if necessary
    """
    if len(message) > max_length:
        return message[:max_length]
    return message