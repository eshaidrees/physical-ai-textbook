import unittest
from unittest.mock import Mock, MagicMock
from backend.src.services.rag_service import RAGService
from backend.src.services.vector_store import VectorStore
from backend.src.services.response_validator import ResponseValidator


class TestRAGService(unittest.TestCase):
    def setUp(self):
        self.mock_vector_store = Mock(spec=VectorStore)
        self.mock_response_validator = Mock(spec=ResponseValidator)
        self.rag_service = RAGService(self.mock_vector_store)
        self.rag_service.response_validator = self.mock_response_validator

    def test_query_success(self):
        # Arrange
        query = "test query"
        mock_search_results = [{"text": "test content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_search_results
        self.mock_response_validator.validate.return_value = True

        # Act
        result = self.rag_service.query(query)

        # Assert
        self.assertEqual(result["query"], query)
        self.assertEqual(result["sources"], mock_search_results)
        self.assertTrue(result["is_valid"])
        self.assertIn("response", result)
        self.mock_vector_store.similarity_search.assert_called_once_with(query, 4)

    def test_query_with_conversation_context(self):
        # Arrange
        query = "test query"
        conversation_context = [
            {"text": "previous user message", "sender": "user"},
            {"text": "previous bot response", "sender": "bot"}
        ]
        mock_search_results = [{"text": "test content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_search_results
        self.mock_response_validator.validate.return_value = True

        # Act
        result = self.rag_service.query(query, conversation_context=conversation_context)

        # Assert
        self.assertEqual(result["query"], query)
        self.mock_vector_store.similarity_search.assert_called_once_with(query, 4)

    def test_generate_response_without_context(self):
        # Arrange
        query = "test query"
        search_results = [{"text": "test content", "metadata": {}}]

        # Act
        response = self.rag_service._generate_response(query, search_results)

        # Assert
        self.assertIn(query, response)
        self.assertIn("test content", response)

    def test_generate_response_with_context(self):
        # Arrange
        query = "test query"
        search_results = [{"text": "test content", "metadata": {}}]
        conversation_context = [
            {"text": "previous user message", "sender": "user"},
            {"text": "previous bot response", "sender": "bot"}
        ]

        # Act
        response = self.rag_service._generate_response(query, search_results, conversation_context)

        # Assert
        self.assertIn(query, response)

    def test_search_content(self):
        # Arrange
        query = "test query"
        mock_results = [{"text": "test", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_results

        # Act
        results = self.rag_service.search_content(query)

        # Assert
        self.assertEqual(results, mock_results)
        self.mock_vector_store.similarity_search.assert_called_once_with(query, 4)

    def test_search_by_section(self):
        # Arrange
        section_title = "Introduction"
        mock_results = [{"text": "intro content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_results

        # Act
        results = self.rag_service.search_by_section(section_title)

        # Assert
        self.assertEqual(results, mock_results)
        self.mock_vector_store.similarity_search.assert_called_once_with("section: Introduction OR Introduction", 4)

    def test_search_by_topic(self):
        # Arrange
        topic = "AI"
        mock_results = [{"text": "AI content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_results

        # Act
        results = self.rag_service.search_by_topic(topic)

        # Assert
        self.assertEqual(results, mock_results)
        self.mock_vector_store.similarity_search.assert_called_once_with("topic: AI OR about AI OR related to AI", 4)

    def test_search_by_keyword(self):
        # Arrange
        keyword = "neural"
        mock_results = [{"text": "neural network content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_results

        # Act
        results = self.rag_service.search_by_keyword(keyword)

        # Assert
        self.assertEqual(results, mock_results)
        self.mock_vector_store.similarity_search.assert_called_once_with(keyword, 4)

    def test_filter_content_by_source_file(self):
        # Arrange
        content_list = [
            {"text": "content 1", "metadata": {"source_file": "chapter1.txt"}},
            {"text": "content 2", "metadata": {"source_file": "chapter2.txt"}}
        ]
        filters = {"source_file": "chapter1"}

        # Act
        filtered = self.rag_service.filter_content(content_list, filters)

        # Assert
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["text"], "content 1")

    def test_filter_content_by_topic(self):
        # Arrange
        content_list = [
            {"text": "content 1", "metadata": {"topics": ["AI", "ML"]}},
            {"text": "content 2", "metadata": {"topics": ["Robotics"]}}
        ]
        filters = {"topic": "AI"}

        # Act
        filtered = self.rag_service.filter_content(content_list, filters)

        # Assert
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["text"], "content 1")

    def test_generate_content_summary(self):
        # Arrange
        content_list = [
            {"text": "First part of content."},
            {"text": "Second part of content."}
        ]

        # Act
        summary = self.rag_service.generate_content_summary(content_list)

        # Assert
        self.assertIn("First part", summary)
        self.assertIn("Second part", summary)

    def test_generate_topic_summary(self):
        # Arrange
        topic = "Machine Learning"
        mock_search_results = [{"text": "ML content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_search_results
        self.mock_response_validator.validate.return_value = True

        # Act
        summary = self.rag_service.generate_topic_summary(topic)

        # Assert
        self.assertEqual(summary["topic"], topic)
        self.assertEqual(summary["results_count"], 1)
        self.assertIn("content", summary)

    def test_generate_section_summary(self):
        # Arrange
        section_title = "Introduction"
        mock_search_results = [{"text": "Intro content", "metadata": {}}]
        self.mock_vector_store.similarity_search.return_value = mock_search_results
        self.mock_response_validator.validate.return_value = True

        # Act
        summary = self.rag_service.generate_section_summary(section_title)

        # Assert
        self.assertEqual(summary["section"], section_title)
        self.assertEqual(summary["results_count"], 1)
        self.assertIn("content", summary)


if __name__ == '__main__':
    unittest.main()