from typing import List, Dict, Any
from ...models.chat import BookContent, ValidatedResponse


class MessageFormatter:
    @staticmethod
    def format_response_from_sources(query: str, sources: List[Dict[str, Any]],
                                   max_length: int = 1000) -> str:
        """
        Format a response based on retrieved sources
        """
        if not sources:
            return "I cannot find relevant information in the book for your query."

        # Combine the most relevant sources into a coherent response
        response_parts = []
        response_parts.append(f"Based on the book content, here's what I found about '{query}':")
        response_parts.append("")

        for i, source in enumerate(sources):
            text = source.get('text', '')
            # Limit the length of each source to avoid very long responses
            if len(text) > 300:
                text = text[:300] + "..."

            response_parts.append(f"{i+1}. {text}")
            response_parts.append("")

        full_response = "\n".join(response_parts)

        # If the response is too long, truncate it
        if len(full_response) > max_length:
            full_response = full_response[:max_length] + "\n\n[Response truncated for brevity]"

        return full_response.strip()

    @staticmethod
    def format_sources_list(sources: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Format sources into a more readable list
        """
        formatted_sources = []
        for i, source in enumerate(sources):
            formatted_source = {
                "id": str(i + 1),
                "content": source.get('text', '')[:200] + "..." if len(source.get('text', '')) > 200 else source.get('text', ''),
                "file": source.get('metadata', {}).get('file', 'Unknown'),
                "score": str(source.get('score', 0.0))
            }
            formatted_sources.append(formatted_source)

        return formatted_sources

    @staticmethod
    def create_validated_response(original_response: str, sources: List[Dict[str, Any]]) -> ValidatedResponse:
        """
        Create a validated response ensuring it contains only book-sourced information
        """
        # For now, we'll use the original response as the validated response
        # In a more advanced implementation, we might modify the response to ensure
        # it strictly adheres to the source material
        validated_response = original_response

        # Check if the response contains appropriate book content
        has_book_content = len(sources) > 0

        # Create validation notes
        validation_notes = None
        if not has_book_content:
            validation_notes = "Response was generated without relevant book content."

        return ValidatedResponse(
            original_response=original_response,
            validated_response=validated_response,
            is_from_book=has_book_content,
            sources=sources,
            validation_notes=validation_notes
        )

    @staticmethod
    def format_conversation_for_context(conversation_messages: List[Dict[str, str]],
                                     max_context_length: int = 500) -> str:
        """
        Format conversation history for use as context in RAG queries
        """
        if not conversation_messages:
            return ""

        # Build context from the most recent messages
        context_parts = []
        current_length = 0

        # Go through messages in reverse order (most recent first)
        for msg in reversed(conversation_messages):
            msg_text = f"{msg['sender']}: {msg['text']}"
            if current_length + len(msg_text) > max_context_length:
                break

            context_parts.insert(0, msg_text)  # Add to beginning to maintain order
            current_length += len(msg_text)

        return "\n".join(context_parts)

    @staticmethod
    def format_error_message(error_type: str, error_message: str) -> str:
        """
        Format error messages for user display
        """
        error_formats = {
            "external_service_unavailable": "The external service is temporarily unavailable. Please try again later.",
            "content_not_found": "I cannot find relevant information in the book for your query.",
            "validation_failed": "The response could not be validated against the book content.",
            "input_invalid": "Your input is invalid. Please check your query and try again."
        }

        return error_formats.get(error_type, f"An error occurred: {error_message}")