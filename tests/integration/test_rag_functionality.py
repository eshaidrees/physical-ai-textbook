import unittest
import os
from unittest.mock import patch, MagicMock
from backend.src.services.rag_service import RAGService
from backend.src.services.vector_store import VectorStore
from backend.src.services.context_manager import ContextManager
from backend.src.services.response_validator import ResponseValidator


class TestRAGFunctionality(unittest.TestCase):
    def setUp(self):
        # Mock the vector store to avoid needing actual Qdrant connection
        with patch('backend.src.services.vector_store.QdrantClient'):
            self.mock_vector_store = VectorStore()
            self.rag_service = RAGService(self.mock_vector_store)
            self.context_manager = ContextManager()
            self.response_validator = ResponseValidator()

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_rag_query_integration(self, mock_qdrant_client):
        # Arrange: Set up mock search results
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "Artificial intelligence is a branch of computer science.", "metadata": {}}, score=0.9)
        ]

        # Act: Perform a query
        result = self.rag_service.query("What is artificial intelligence?")

        # Assert: Check that the result contains expected elements
        self.assertIn("response", result)
        self.assertIn("sources", result)
        self.assertIn("is_valid", result)
        self.assertIn("query", result)
        self.assertEqual(result["query"], "What is artificial intelligence?")
        self.assertTrue(result["is_valid"])

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_rag_with_conversation_context(self, mock_qdrant_client):
        # Arrange: Set up mock search results and conversation context
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "Machine learning algorithms learn from data.", "metadata": {}}, score=0.85)
        ]

        conversation_context = [
            {"text": "What is AI?", "sender": "user"},
            {"text": "AI is artificial intelligence.", "sender": "bot"}
        ]

        # Act: Perform a query with conversation context
        result = self.rag_service.query("How does it learn?", conversation_context=conversation_context)

        # Assert: Check that the result contains expected elements
        self.assertIn("response", result)
        self.assertIn("sources", result)
        self.assertTrue(result["is_valid"])

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_context_aware_response_generation(self, mock_qdrant_client):
        # Arrange: Set up mock search results
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "Neural networks are computing systems inspired by the brain.", "metadata": {}}, score=0.92)
        ]

        # Create a conversation context
        conversation_context = [
            {"text": "Explain neural networks", "sender": "user"},
            {"text": "Neural networks are like the brain.", "sender": "bot"}
        ]

        # Act: Generate a response considering the context
        response = self.rag_service._generate_response(
            query="How do neural networks work?",
            search_results=[{"text": "Neural networks are computing systems inspired by the brain.", "metadata": {}}],
            conversation_context=conversation_context
        )

        # Assert: Check that the response acknowledges the context
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_response_validation_integration(self):
        # Arrange: Prepare a response and source that should validate as true
        response = "Neural networks are computing systems inspired by the brain."
        sources = [{"text": "Neural networks are computing systems inspired by the brain's structure.", "metadata": {}}]

        # Act: Validate the response
        is_valid = self.response_validator.validate(response, sources)

        # Assert: Check that the validation returns True
        self.assertTrue(is_valid)

    def test_response_validation_fails_with_irrelevant_content(self):
        # Arrange: Prepare a response and source that should not validate
        response = "Quantum computing uses qubits."
        sources = [{"text": "Neural networks are computing systems inspired by the brain.", "metadata": {}}]

        # Act: Validate the response
        is_valid = self.response_validator.validate(response, sources)

        # Assert: Check that the validation returns False
        self.assertFalse(is_valid)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_end_to_end_rag_flow(self, mock_qdrant_client):
        # Arrange: Mock search results for the query
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "Robotics is an interdisciplinary branch of engineering.", "metadata": {}}, score=0.88)
        ]

        query = "What is robotics?"

        # Act: Execute the full RAG flow
        result = self.rag_service.query(query)

        # Assert: Check that all components of the RAG flow worked together
        self.assertEqual(result["query"], query)
        self.assertIn("response", result)
        self.assertIn("sources", result)
        self.assertTrue(isinstance(result["sources"], list))
        self.assertIn("is_valid", result)
        self.assertTrue(isinstance(result["is_valid"], bool))

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_conversation_context_preservation(self, mock_qdrant_client):
        # Arrange: Mock search results
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "AI systems can recognize patterns.", "metadata": {}}, score=0.85)
        ]

        # Create a conversation
        conversation_id = self.context_manager.create_conversation()
        self.context_manager.add_message(conversation_id, "What is AI?", "user")
        self.context_manager.add_message(conversation_id, "AI is artificial intelligence.", "bot")

        # Get the conversation context
        context = self.context_manager.get_conversation_context(conversation_id)

        # Act: Query with the context
        result = self.rag_service.query("How does AI work?", conversation_context=context)

        # Assert: Check that the response was generated with context
        self.assertIn("response", result)
        self.assertTrue(len(result["response"]) > 0)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_content_search_and_filtering_integration(self, mock_qdrant_client):
        # Arrange: Mock search results
        mock_search_results = [
            {"text": "AI in robotics helps with decision making.", "metadata": {"source_file": "chapter3.txt", "topics": ["AI", "Robotics"]}},
            {"text": "Control systems manage robot movement.", "metadata": {"source_file": "chapter5.txt", "topics": ["Control", "Robotics"]}}
        ]
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id=str(i), payload=mock_search_results[i], score=0.8 + i*0.05) for i in range(len(mock_search_results))
        ]

        # Act: Search for content
        search_results = self.rag_service.search_content("AI robotics")

        # Filter the results
        filtered_results = self.rag_service.filter_content(search_results, {"topic": "AI"})

        # Assert: Check that filtering worked correctly
        self.assertLessEqual(len(filtered_results), len(search_results))
        if len(filtered_results) > 0:
            # Verify that filtered results contain the expected topic
            for result in filtered_results:
                self.assertIn("AI", result["metadata"]["topics"])

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_topic_summary_generation_integration(self, mock_qdrant_client):
        # Arrange: Mock search results for topic
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "Machine learning is a method of data analysis.", "metadata": {}}, score=0.9),
            MagicMock(id="2", payload={"text": "Deep learning uses neural networks with multiple layers.", "metadata": {}}, score=0.85)
        ]

        topic = "Machine Learning"

        # Act: Generate a topic summary
        summary_result = self.rag_service.generate_topic_summary(topic)

        # Assert: Check that the summary was generated properly
        self.assertEqual(summary_result["topic"], topic)
        self.assertGreater(summary_result["results_count"], 0)
        self.assertIn("summary", summary_result)
        self.assertIn("content", summary_result)
        self.assertGreater(len(summary_result["summary"]), 0)

    def test_rag_service_with_empty_search_results(self):
        # Arrange: Set up mock to return no results
        with patch('backend.src.services.vector_store.QdrantClient') as mock_qdrant_client:
            mock_qdrant_client.return_value.search.return_value = []

            # Act: Query with no matching results
            result = self.rag_service.query("A completely random query with no matches")

            # Assert: Check that the response handles no results appropriately
            self.assertIn("response", result)
            self.assertIn("I cannot find relevant information", result["response"])
            self.assertEqual(len(result["sources"]), 0)
            self.assertFalse(result["is_valid"])


if __name__ == '__main__':
    unittest.main()