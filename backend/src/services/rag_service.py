from typing import List, Dict, Any, Optional
from .vector_store import VectorStore
from .response_validator import ResponseValidator
from .response_generator import ResponseGenerator


class RAGService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.response_validator = ResponseValidator()
        self.response_generator = ResponseGenerator()

    def query(self, query: str, k: int = 4, conversation_context: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Query the RAG system to get relevant content and generate a response
        """
        # Preprocess the query to improve search quality
        processed_query = self._preprocess_query(query, conversation_context)

        # Perform similarity search
        search_results = self.vector_store.similarity_search(processed_query, k)

        # Generate response based on search results using the response generator
        response_text = self.response_generator.generate_response(query, search_results, conversation_context)

        # Validate that response is based on book content
        is_valid = self.response_validator.validate(response_text, search_results)

        return {
            "response": response_text,
            "sources": search_results,
            "is_valid": is_valid,
            "query": query
        }

    def _preprocess_query(self, query: str, conversation_context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Preprocess the query to improve search quality by incorporating conversation context
        """
        if not conversation_context:
            return query

        # Extract recent user queries and bot responses to create a more contextual query
        recent_context = conversation_context[-3:] if len(conversation_context) > 3 else conversation_context

        # Build a contextual query that includes relevant conversation history
        context_parts = []
        for item in recent_context:
            if item["sender"] == "user":
                context_parts.append(f"User asked: {item['text']}")
            elif item["sender"] == "bot":
                # Include bot responses that might provide context for the current query
                context_parts.append(f"Assistant replied: {item['text'][:200]}")  # Limit length

        # Combine the context with the current query
        if context_parts:
            contextual_query = " ".join(context_parts) + f" Current query: {query}"
            return contextual_query

        return query

    def search_content(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for content without generating a full response
        """
        # Preprocess the query to improve search quality
        processed_query = self._preprocess_query_for_search(query)
        return self.vector_store.similarity_search(processed_query, k)

    def _preprocess_query_for_search(self, query: str) -> str:
        """
        Preprocess query specifically for search optimization
        """
        # Remove common stop words that might interfere with search
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = query.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]

        # Reconstruct query with important terms
        processed_query = ' '.join(filtered_words)

        # If the query is too short after filtering, return the original
        if len(processed_query.strip()) < 3:
            return query

        return processed_query

    def query_optimized(self, query: str, k: int = 4, conversation_context: Optional[List[Dict[str, str]]] = None,
                       use_cache: bool = True, rerank_results: bool = True) -> Dict[str, Any]:
        """
        Optimized query method with additional performance features
        """
        # Check cache first if enabled
        if use_cache:
            cached_result = self._check_cache(query, conversation_context)
            if cached_result:
                return cached_result

        # Preprocess the query to improve search quality
        processed_query = self._preprocess_query(query, conversation_context)

        # Perform similarity search
        search_results = self.vector_store.similarity_search(processed_query, k * 2)  # Get more results for reranking

        # Rerank results if requested and we have multiple results
        if rerank_results and len(search_results) > 1:
            search_results = self._rerank_results(query, search_results)[:k]

        # Generate response based on search results
        response_text = self._generate_response(query, search_results, conversation_context)

        # Validate that response is based on book content
        is_valid = self.response_validator.validate(response_text, search_results)

        result = {
            "response": response_text,
            "sources": search_results[:k],
            "is_valid": is_valid,
            "query": query
        }

        # Cache the result if caching is enabled
        if use_cache:
            self._cache_result(query, conversation_context, result)

        return result

    def _rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank search results based on relevance to the query
        """
        # Simple reranking based on keyword matching
        def calculate_relevance(result: Dict[str, Any]) -> float:
            text = result['text'].lower()
            query_words = query.lower().split()
            matches = sum(1 for word in query_words if word in text)
            return matches / len(query_words) if query_words else 0

        # Sort results by relevance score
        reranked_results = sorted(results, key=calculate_relevance, reverse=True)
        return reranked_results

    def _check_cache(self, query: str, conversation_context: Optional[List[Dict[str, str]]]) -> Optional[Dict[str, Any]]:
        """
        Check if the query result is in cache
        """
        # This is a basic implementation - in production, use Redis or similar
        return None  # Placeholder - will implement proper caching later

    def _cache_result(self, query: str, conversation_context: Optional[List[Dict[str, str]]], result: Dict[str, Any]):
        """
        Cache the query result
        """
        # This is a basic implementation - in production, use Redis or similar
        pass  # Placeholder - will implement proper caching later

    def search_by_section(self, section_title: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for content by specific section title
        """
        # This would search for content that specifically relates to the section title
        # For now, we'll use the same similarity search but in the future this could
        # use more sophisticated section-based search
        query_with_section = f"section: {section_title} OR {section_title}"
        return self.vector_store.similarity_search(query_with_section, k)

    def search_by_topic(self, topic: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for content by specific topic across the book
        """
        # Enhanced search for a specific topic
        topic_query = f"topic: {topic} OR about {topic} OR related to {topic}"
        return self.vector_store.similarity_search(topic_query, k)

    def search_by_keyword(self, keyword: str, k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for content containing a specific keyword
        """
        # Search for content containing the exact keyword
        return self.vector_store.similarity_search(keyword, k)

    def filter_content(self, content_list: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter content based on metadata or other criteria
        """
        filtered_content = content_list
        for key, value in filters.items():
            if key == "source_file":
                if isinstance(value, str):
                    filtered_content = [item for item in filtered_content if value in item.get("metadata", {}).get("source_file", "")]
                elif isinstance(value, list):
                    # If value is a list, check if any of the values match
                    filtered_content = [item for item in filtered_content if any(v in item.get("metadata", {}).get("source_file", "") for v in value)]
            elif key == "section":
                if isinstance(value, str):
                    filtered_content = [item for item in filtered_content if value in item.get("metadata", {}).get("section", "")]
                elif isinstance(value, list):
                    filtered_content = [item for item in filtered_content if any(v in item.get("metadata", {}).get("section", "") for v in value)]
            elif key == "topic":
                # Filter based on topic keywords in metadata
                if isinstance(value, str):
                    filtered_content = [item for item in filtered_content if value in item.get("metadata", {}).get("topics", [])]
                elif isinstance(value, list):
                    filtered_content = [item for item in filtered_content if any(v in item.get("metadata", {}).get("topics", []) for v in value)]
            elif key == "min_relevance_score":
                # Filter based on minimum relevance score
                try:
                    min_score = float(value)
                    filtered_content = [item for item in filtered_content if item.get("score", 0) >= min_score]
                except ValueError:
                    # If conversion to float fails, skip this filter
                    continue
            elif key == "content_length":
                # Filter based on content length
                try:
                    min_length = int(value)
                    filtered_content = [item for item in filtered_content if len(item.get("text", "")) >= min_length]
                except ValueError:
                    # If conversion to int fails, skip this filter
                    continue

        return filtered_content

    def advanced_search(self, query: str, filters: Dict[str, Any], k: int = 4) -> List[Dict[str, Any]]:
        """
        Perform an advanced search with filters applied
        """
        # First perform the basic search
        search_results = self.search_content(query, k * 2)  # Get more results to have more to filter from

        # Then apply filters
        filtered_results = self.filter_content(search_results, filters)

        # Return the top k results after filtering
        return filtered_results[:k]

    def generate_content_summary(self, content_list: List[Dict[str, Any]], max_length: int = 300) -> str:
        """
        Generate a summary of the provided content list
        """
        if not content_list:
            return "No content available to summarize."

        # Combine all content texts
        all_text = " ".join([item["text"] for item in content_list])

        # Simple summarization by truncating to max_length and adding context
        if len(all_text) <= max_length:
            return all_text

        # For a more sophisticated approach, we could use extractive or abstractive summarization
        # For now, we'll return the first portion with an indication of truncation
        summary = all_text[:max_length].rsplit(' ', 1)[0]  # Truncate at the last word boundary

        return f"{summary}..."

    def generate_topic_summary(self, topic: str, k: int = 4) -> Dict[str, Any]:
        """
        Generate a summary for a specific topic from the book
        """
        search_results = self.search_by_topic(topic, k)

        if not search_results:
            return {
                "topic": topic,
                "summary": f"No content found for topic: {topic}",
                "results_count": 0,
                "content": []
            }

        # Generate a summary of the topic based on search results
        topic_summary = self.generate_content_summary(search_results)

        return {
            "topic": topic,
            "summary": topic_summary,
            "results_count": len(search_results),
            "content": search_results
        }

    def generate_section_summary(self, section_title: str, k: int = 4) -> Dict[str, Any]:
        """
        Generate a summary for a specific section from the book
        """
        search_results = self.search_by_section(section_title, k)

        if not search_results:
            return {
                "section": section_title,
                "summary": f"No content found for section: {section_title}",
                "results_count": 0,
                "content": []
            }

        # Generate a summary of the section based on search results
        section_summary = self.generate_content_summary(search_results)

        return {
            "section": section_title,
            "summary": section_summary,
            "results_count": len(search_results),
            "content": search_results
        }

    def add_content(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add content to the vector store
        """
        return self.vector_store.add_texts(texts, metadatas)