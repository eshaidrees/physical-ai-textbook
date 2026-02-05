from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
from ..models.chat import Message, Conversation


class ContextManager:
    def __init__(self, default_max_messages: int = 10):
        self.conversations: Dict[str, Conversation] = {}
        self.default_max_messages = default_max_messages
        self.conversation_timeout = timedelta(hours=1)  # 1 hour timeout

    def create_conversation(self, conversation_id: Optional[str] = None) -> str:
        """Create a new conversation and return its ID"""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        conversation = Conversation(
            id=conversation_id,
            max_messages=self.default_max_messages
        )
        # Set the last accessed time to now when creating the conversation
        conversation.last_accessed = datetime.now()

        self.conversations[conversation_id] = conversation
        return conversation_id

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID, cleaning up expired ones"""
        # Clean up expired conversations
        self._cleanup_expired_conversations()

        conversation = self.conversations.get(conversation_id)
        if conversation:
            # Update the last accessed time
            conversation.last_accessed = datetime.now()

        return conversation

    def add_message(self, conversation_id: str, text: str, sender: str, metadata: Optional[Dict[str, Any]] = None) -> Conversation:
        """Add a message to a conversation"""
        if metadata is None:
            metadata = {}

        conversation = self.get_conversation(conversation_id)
        if conversation is None:
            conversation = Conversation(
                id=conversation_id,
                max_messages=self.default_max_messages
            )
            # Set the last accessed time when creating a new conversation
            conversation.last_accessed = datetime.now()
            self.conversations[conversation_id] = conversation

        message = Message(
            id=str(uuid.uuid4()),
            text=text,
            sender=sender,
            timestamp=datetime.now(),
            metadata=metadata
        )

        conversation.add_message(message)
        # Update the last accessed time when adding a message
        conversation.last_accessed = datetime.now()
        return conversation

    def get_conversation_context(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get the context for a specific conversation"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            return conversation.get_context()
        return []

    def detect_topic_shift(self, conversation_id: str, new_message: str) -> bool:
        """Detect if the new message represents a topic shift"""
        conversation = self.get_conversation(conversation_id)
        if conversation:
            return conversation.detect_topic_shift(new_message)
        return False

    def _cleanup_expired_conversations(self):
        """Remove conversations that haven't been accessed in more than the timeout period"""
        now = datetime.now()
        expired_ids = [
            conv_id for conv_id, conversation in self.conversations.items()
            if now - conversation.last_accessed > self.conversation_timeout
        ]

        for conv_id in expired_ids:
            del self.conversations[conv_id]

    def clear_conversation(self, conversation_id: str):
        """Clear all messages from a conversation"""
        if conversation_id in self.conversations:
            # Keep the conversation object but clear messages
            self.conversations[conversation_id].messages = []