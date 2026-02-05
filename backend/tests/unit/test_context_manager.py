import unittest
from datetime import datetime, timedelta
from backend.src.services.context_manager import ContextManager, Message, Conversation


class TestContextManager(unittest.TestCase):
    def setUp(self):
        self.context_manager = ContextManager(default_max_messages=5)

    def test_create_conversation(self):
        # Act
        conversation_id = self.context_manager.create_conversation()

        # Assert
        self.assertIsNotNone(conversation_id)
        self.assertIn(conversation_id, self.context_manager.conversations)

    def test_add_message_to_conversation(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()

        # Act
        self.context_manager.add_message(conversation_id, "Hello", "user")

        # Assert
        conversation = self.context_manager.get_conversation(conversation_id)
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0].text, "Hello")
        self.assertEqual(conversation.messages[0].sender, "user")

    def test_get_conversation_context(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()
        self.context_manager.add_message(conversation_id, "Hello", "user")
        self.context_manager.add_message(conversation_id, "Hi there", "bot")

        # Act
        context = self.context_manager.get_conversation_context(conversation_id)

        # Assert
        self.assertEqual(len(context), 2)
        self.assertEqual(context[0]["text"], "Hello")
        self.assertEqual(context[0]["sender"], "user")
        self.assertEqual(context[1]["text"], "Hi there")
        self.assertEqual(context[1]["sender"], "bot")

    def test_message_limit(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()

        # Act - Add more messages than the limit
        for i in range(10):
            self.context_manager.add_message(conversation_id, f"Message {i}", "user")

        # Assert
        conversation = self.context_manager.get_conversation(conversation_id)
        # Should only keep the last 5 messages due to default_max_messages=5
        self.assertEqual(len(conversation.messages), 5)

    def test_detect_topic_shift_simple(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()
        # Add a message about AI
        self.context_manager.add_message(conversation_id, "What is machine learning?", "user")
        self.context_manager.add_message(conversation_id, "ML is an AI technique", "bot")

        # Act
        is_topic_shift = self.context_manager.detect_topic_shift(conversation_id, "How do humanoid robots walk?")

        # Assert
        # Should detect a shift from AI/ML to robotics/humanoid movement
        self.assertTrue(is_topic_shift)

    def test_detect_topic_shift_no_shift(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()
        # Add messages about robotics
        self.context_manager.add_message(conversation_id, "How do robots move?", "user")
        self.context_manager.add_message(conversation_id, "Robots use actuators", "bot")

        # Act
        is_topic_shift = self.context_manager.detect_topic_shift(conversation_id, "What are actuators?")

        # Assert
        # Should not detect a topic shift since both are about robotics
        self.assertFalse(is_topic_shift)

    def test_conversation_timeout(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()
        # Manually set last_accessed to a time in the past beyond timeout
        conversation = self.context_manager.get_conversation(conversation_id)
        conversation.last_accessed = datetime.now() - timedelta(hours=2)  # Beyond 1-hour timeout

        # Act
        # Accessing the conversation should trigger cleanup
        retrieved_conversation = self.context_manager.get_conversation(conversation_id)

        # Assert
        # The conversation should have been cleaned up due to timeout
        self.assertIsNone(retrieved_conversation)

    def test_clear_conversation(self):
        # Arrange
        conversation_id = self.context_manager.create_conversation()
        self.context_manager.add_message(conversation_id, "Hello", "user")
        self.context_manager.add_message(conversation_id, "Hi", "bot")

        # Act
        self.context_manager.clear_conversation(conversation_id)

        # Assert
        conversation = self.context_manager.get_conversation(conversation_id)
        self.assertEqual(len(conversation.messages), 0)

    def test_get_recent_context_summary(self):
        # Arrange
        conversation = Conversation(id="test")
        conversation.add_message(Message(id="1", text="Hello", sender="user", timestamp=datetime.now()))
        conversation.add_message(Message(id="2", text="Hi there", sender="bot", timestamp=datetime.now()))

        # Act
        summary = conversation.get_recent_context_summary()

        # Assert
        self.assertIn("User: Hello", summary)
        self.assertIn("Assistant: Hi there", summary)

    def test_get_topic_keywords(self):
        # Arrange
        conversation = Conversation(id="test")
        conversation.add_message(Message(id="1", text="What is artificial intelligence?", sender="user", timestamp=datetime.now()))
        conversation.add_message(Message(id="2", text="AI is about neural networks", sender="bot", timestamp=datetime.now()))
        conversation.add_message(Message(id="3", text="How do robots locomote?", sender="user", timestamp=datetime.now()))
        conversation.add_message(Message(id="4", text="Robots use actuators for movement", sender="bot", timestamp=datetime.now()))

        # Act
        keywords = conversation.get_topic_keywords()

        # Assert
        # Should contain keywords related to AI and robotics
        self.assertIn("ai", keywords)
        self.assertIn("robot", keywords)


class TestMessage(unittest.TestCase):
    def test_message_creation(self):
        # Act
        message = Message(id="1", text="Hello", sender="user", timestamp=datetime.now())

        # Assert
        self.assertEqual(message.id, "1")
        self.assertEqual(message.text, "Hello")
        self.assertEqual(message.sender, "user")


class TestConversation(unittest.TestCase):
    def test_conversation_creation(self):
        # Act
        conversation = Conversation(id="test")

        # Assert
        self.assertEqual(conversation.id, "test")
        self.assertEqual(len(conversation.messages), 0)

    def test_add_message(self):
        # Arrange
        conversation = Conversation(id="test")

        # Act
        message = Message(id="1", text="Hello", sender="user", timestamp=datetime.now())
        conversation.add_message(message)

        # Assert
        self.assertEqual(len(conversation.messages), 1)
        self.assertEqual(conversation.messages[0].text, "Hello")

    def test_get_context(self):
        # Arrange
        conversation = Conversation(id="test")
        message = Message(id="1", text="Hello", sender="user", timestamp=datetime.now())
        conversation.add_message(message)

        # Act
        context = conversation.get_context()

        # Assert
        self.assertEqual(len(context), 1)
        self.assertEqual(context[0]["text"], "Hello")
        self.assertEqual(context[0]["sender"], "user")

    def test_message_limiting(self):
        # Arrange
        conversation = Conversation(id="test", max_messages=3)

        # Act
        for i in range(5):
            message = Message(id=str(i), text=f"Message {i}", sender="user", timestamp=datetime.now())
            conversation.add_message(message)

        # Assert
        self.assertEqual(len(conversation.messages), 3)  # Should only keep last 3 messages
        self.assertEqual(conversation.messages[0].text, "Message 2")  # First message should be removed
        self.assertEqual(conversation.messages[2].text, "Message 4")  # Last message should remain


if __name__ == '__main__':
    unittest.main()