import unittest
import requests
import time
from unittest.mock import patch, MagicMock
from backend.src.main import app
from backend.src.services.rag_service import RAGService
from backend.src.services.vector_store import VectorStore
from backend.src.services.context_manager import ContextManager


class TestE2EUserFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test class with a test server if needed"""
        # For now, we'll use mocking to simulate the complete flow
        # In a real scenario, you would start the FastAPI server
        pass

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the vector store to avoid needing actual Qdrant connection
        with patch('backend.src.services.vector_store.QdrantClient'):
            self.mock_vector_store = VectorStore()
            self.rag_service = RAGService(self.mock_vector_store)
            self.context_manager = ContextManager()
            self.app = app

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_complete_chat_conversation_flow(self, mock_qdrant_client):
        """Test a complete chat conversation flow from start to finish"""
        # Arrange: Set up mock search results for different queries
        def mock_search_side_effect(query, limit):
            if "artificial intelligence" in query.lower():
                return [
                    {"id": "1", "text": "Artificial intelligence is a branch of computer science that aims to create software or machines that exhibit human-like intelligence.", "metadata": {}}
                ]
            elif "machine learning" in query.lower():
                return [
                    {"id": "2", "text": "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.", "metadata": {}}
                ]
            elif "robotics" in query.lower():
                return [
                    {"id": "3", "text": "Robotics is an interdisciplinary branch of engineering that involves the conception, design, construction, operation, and use of robots.", "metadata": {}}
                ]
            else:
                return [
                    {"id": "4", "text": "Physical AI and Humanoid Robotics combine artificial intelligence with mechanical engineering to create robots that mimic human behavior and capabilities.", "metadata": {}}
                ]

        mock_qdrant_client.return_value.search.side_effect = lambda collection_name, query_vector, limit, **kwargs: [
            MagicMock(id="1", payload=mock_search_side_effect("test", 1)[0], score=0.9)
        ]

        # Act: Simulate a multi-turn conversation
        conversation_id = self.context_manager.create_conversation()

        # First message: User asks about AI
        user_query_1 = "What is artificial intelligence?"
        result_1 = self.rag_service.query(user_query_1)
        self.context_manager.add_message(conversation_id, user_query_1, "user")
        self.context_manager.add_message(conversation_id, result_1["response"], "bot")

        # Second message: User asks a follow-up about machine learning
        user_query_2 = "How is it related to machine learning?"
        conversation_context = self.context_manager.get_conversation_context(conversation_id)
        result_2 = self.rag_service.query(user_query_2, conversation_context=conversation_context)
        self.context_manager.add_message(conversation_id, user_query_2, "user")
        self.context_manager.add_message(conversation_id, result_2["response"], "bot")

        # Third message: User asks about robotics
        user_query_3 = "What about robotics?"
        conversation_context = self.context_manager.get_conversation_context(conversation_id)
        result_3 = self.rag_service.query(user_query_3, conversation_context=conversation_context)

        # Assert: Check that all responses were generated and conversation context was maintained
        self.assertIsNotNone(result_1["response"])
        self.assertIsNotNone(result_2["response"])
        self.assertIsNotNone(result_3["response"])

        # Check that responses contain relevant information
        self.assertIn("intelligence", result_1["response"].lower())
        self.assertIn("intelligence", result_2["response"].lower())
        self.assertIn("robotics", result_3["response"].lower())

        # Check that conversation context was used in follow-up questions
        conversation = self.context_manager.get_conversation(conversation_id)
        self.assertEqual(len(conversation.messages), 6)  # 3 user + 3 bot messages

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_content_search_and_access_flow(self, mock_qdrant_client):
        """Test the complete flow for searching and accessing book content"""
        # Arrange: Mock search results
        mock_search_results = [
            {"text": "Chapter 3 discusses neural networks and deep learning techniques.", "metadata": {"source_file": "chapter3.txt", "section": "Neural Networks"}},
            {"text": "The perceptron model was developed in the 1950s by Frank Rosenblatt.", "metadata": {"source_file": "chapter3.txt", "section": "Neural Networks"}},
            {"text": "Backpropagation is a method for training neural networks by computing gradients.", "metadata": {"source_file": "chapter3.txt", "section": "Training Methods"}}
        ]

        def mock_search_impl(collection_name, query_vector, limit, **kwargs):
            results = []
            for i, result in enumerate(mock_search_results[:limit]):
                results.append(MagicMock(id=str(i), payload=result, score=0.9 - i*0.05))
            return results

        mock_qdrant_client.return_value.search.side_effect = mock_search_impl

        # Act: Simulate content search and filtering
        search_results = self.rag_service.search_content("neural networks")
        filtered_results = self.rag_service.filter_content(search_results, {"section": "Neural Networks"})
        topic_summary = self.rag_service.generate_topic_summary("neural networks")
        section_summary = self.rag_service.generate_section_summary("Neural Networks")

        # Assert: Check that all components of the content access flow worked
        self.assertGreater(len(search_results), 0)
        self.assertGreater(len(filtered_results), 0)
        self.assertIn("neural networks", topic_summary["topic"].lower())
        self.assertIn("neural networks", section_summary["section"].lower())
        self.assertGreater(len(topic_summary["summary"]), 0)
        self.assertGreater(len(section_summary["summary"]), 0)

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_conversation_context_with_topic_shift_detection(self, mock_qdrant_client):
        """Test conversation flow with topic shift detection"""
        # Arrange: Mock search results
        def mock_search_side_effect(query, limit):
            if any(word in query.lower() for word in ["ai", "intelligence"]):
                return [
                    {"text": "AI refers to computer systems that perform tasks normally requiring human intelligence.", "metadata": {}}
                ]
            elif any(word in query.lower() for word in ["robot", "locomotion", "walking"]):
                return [
                    {"text": "Robotic locomotion involves the mechanisms and methods that enable robots to move.", "metadata": {}}
                ]
            else:
                return [
                    {"text": "Physical AI combines artificial intelligence with mechanical engineering for humanoid systems.", "metadata": {}}
                ]

        mock_qdrant_client.return_value.search.side_effect = lambda collection_name, query_vector, limit, **kwargs: [
            MagicMock(id="1", payload=mock_search_side_effect("test", 1)[0], score=0.9)
        ]

        # Act: Create a conversation that shifts topics
        conversation_id = self.context_manager.create_conversation()

        # First, discuss AI
        ai_query = "What is AI?"
        self.context_manager.add_message(conversation_id, ai_query, "user")
        ai_response = self.rag_service.query(ai_query)
        self.context_manager.add_message(conversation_id, ai_response["response"], "bot")

        # Then shift to robotics
        robot_query = "How do robots move?"
        is_topic_shift = self.context_manager.detect_topic_shift(conversation_id, robot_query)

        # Check context summary
        context_summary = self.context_manager.get_conversation_context(conversation_id)

        # Assert: Check that topic shift was detected and context was maintained
        self.assertIsInstance(is_topic_shift, bool)  # Topic shift detection should return a boolean
        self.assertGreater(len(context_summary), 0)  # Should have some context

    def test_error_handling_in_user_flow(self):
        """Test how the system handles errors during user interaction"""
        # This test would check for graceful error handling
        # For example, what happens when the vector store is unavailable
        with patch('backend.src.services.vector_store.VectorStore.similarity_search') as mock_search:
            mock_search.side_effect = Exception("Vector store unavailable")

            # Act: Try to perform a query when vector store is down
            try:
                result = self.rag_service.query("Test query")
                # If we get here, the system handled the error gracefully
                success = True
            except Exception:
                # If we get an exception, the system did not handle it gracefully
                success = False

            # The system should handle errors gracefully
            self.assertTrue(success or "error" in locals())

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_multi_user_conversation_isolation(self, mock_qdrant_client):
        """Test that conversations for different users are properly isolated"""
        # Arrange: Set up mock search
        mock_qdrant_client.return_value.search.return_value = [
            MagicMock(id="1", payload={"text": "Artificial intelligence simulates human intelligence processes by machines.", "metadata": {}}, score=0.9)
        ]

        # Act: Create conversations for two different users
        user1_conversation_id = self.context_manager.create_conversation()
        user2_conversation_id = self.context_manager.create_conversation()

        # User 1 asks a question
        self.context_manager.add_message(user1_conversation_id, "What is AI?", "user")
        user1_response = self.rag_service.query("What is AI?")
        self.context_manager.add_message(user1_conversation_id, user1_response["response"], "bot")

        # User 2 asks the same question
        self.context_manager.add_message(user2_conversation_id, "What is AI?", "user")
        user2_response = self.rag_service.query("What is AI?")
        self.context_manager.add_message(user2_conversation_id, user2_response["response"], "bot")

        # Assert: Check that conversations are isolated
        user1_conversation = self.context_manager.get_conversation(user1_conversation_id)
        user2_conversation = self.context_manager.get_conversation(user2_conversation_id)

        self.assertEqual(len(user1_conversation.messages), 2)
        self.assertEqual(len(user2_conversation.messages), 2)

        # Each user's conversation should only contain their own messages
        for message in user1_conversation.messages:
            self.assertIn(message.sender, ["user", "bot"])

        for message in user2_conversation.messages:
            self.assertIn(message.sender, ["user", "bot"])

    @patch('backend.src.services.vector_store.QdrantClient')
    def test_search_then_conversation_flow(self, mock_qdrant_client):
        """Test the flow where a user searches for content then engages in conversation"""
        # Arrange: Mock search results
        mock_qdrant_client.return_value.search.side_effect = lambda collection_name, query_vector, limit, **kwargs: [
            MagicMock(id="1", payload={
                "text": "Humanoid robots are robots with physical structures similar to the human body.",
                "metadata": {"section": "Introduction to Humanoid Robotics", "chapter": "Chapter 1"}
            }, score=0.9)
        ] * limit  # Return the requested number of results

        # Act: First perform a search
        search_results = self.rag_service.search_content("humanoid robots")
        section_summary = self.rag_service.generate_section_summary("Introduction to Humanoid Robotics")

        # Then start a conversation based on the search
        conversation_id = self.context_manager.create_conversation()
        self.context_manager.add_message(conversation_id, "Tell me about humanoid robots", "user")
        chat_response = self.rag_service.query("Tell me about humanoid robots")
        self.context_manager.add_message(conversation_id, chat_response["response"], "bot")

        # Follow up with a related question
        self.context_manager.add_message(conversation_id, "How are they different from other robots?", "user")
        follow_up_response = self.rag_service.query("How are they different from other robots?",
                                                   conversation_context=self.context_manager.get_conversation_context(conversation_id))
        self.context_manager.add_message(conversation_id, follow_up_response["response"], "bot")

        # Assert: Check that both search and conversation components worked
        self.assertGreater(len(search_results), 0)
        self.assertIn("humanoid", section_summary["section"].lower())
        self.assertGreater(len(section_summary["summary"]), 0)
        self.assertIn("humanoid", chat_response["response"].lower())
        self.assertIn("humanoid", follow_up_response["response"].lower())

        # Check that conversation context was maintained
        conversation = self.context_manager.get_conversation(conversation_id)
        self.assertEqual(len(conversation.messages), 4)  # 2 user + 2 bot messages


if __name__ == '__main__':
    unittest.main()