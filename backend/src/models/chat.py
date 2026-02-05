from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


class QueryRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    k: Optional[int] = 4  # Number of results to retrieve


class QueryResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]]
    is_valid: bool
    query: str
    conversation_id: str


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    sender: str  # 'user' or 'bot'
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = {}


class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_accessed: datetime = Field(default_factory=datetime.now)  # Track when conversation was last accessed
    max_messages: int = 10  # Limit conversation history to last 10 messages

    def add_message(self, message: Message):
        """Add a message to the conversation, respecting max_messages limit"""
        self.messages.append(message)
        self.updated_at = datetime.now()

        # Keep only the last max_messages
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> List[Dict[str, str]]:
        """Get the conversation context as a list of dictionaries"""
        return [
            {
                "id": msg.id,
                "text": msg.text,
                "sender": msg.sender,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self.messages
        ]

    def detect_topic_shift(self, new_message: str, threshold: float = 0.3) -> bool:
        """
        Detect if the new message represents a topic shift from the conversation history
        This is a more sophisticated implementation that considers multiple aspects
        """
        if len(self.messages) < 2:
            return False

        # Get recent messages for context
        recent_messages = " ".join([msg.text for msg in self.messages[-3:]])
        new_message_lower = new_message.lower()
        recent_lower = recent_messages.lower()

        # Define topic-related keywords for Physical AI & Humanoid Robotics
        ai_related = [
            'ai', 'artificial', 'intelligence', 'machine', 'learning', 'neural', 'algorithm',
            'deep learning', 'training', 'model', 'prediction', 'classification', 'regression',
            'reinforcement learning', 'supervised', 'unsupervised', 'data', 'dataset'
        ]
        robotics_related = [
            'robot', 'robotics', 'humanoid', 'actuator', 'sensor', 'locomotion', 'control',
            'motor', 'servo', 'gait', 'walking', 'balance', 'manipulation', 'kinematics',
            'dynamics', 'trajectory', 'motion planning', 'path planning', 'navigation'
        ]
        physics_related = [
            'physics', 'force', 'torque', 'dynamics', 'kinematics', 'equation', 'motion',
            'velocity', 'acceleration', 'mass', 'inertia', 'friction', 'collision', 'contact'
        ]
        control_related = [
            'control', 'controller', 'pid', 'feedback', 'stability', 'tracking', 'regulation',
            'system', 'state', 'output', 'input', 'response', 'performance', 'tuning'
        ]

        # Check for topic content in recent messages and new message
        prev_ai_content = any(word in recent_lower for word in ai_related)
        prev_robotics_content = any(word in recent_lower for word in robotics_related)
        prev_physics_content = any(word in recent_lower for word in physics_related)
        prev_control_content = any(word in recent_lower for word in control_related)

        new_ai_content = any(word in new_message_lower for word in ai_related)
        new_robotics_content = any(word in new_message_lower for word in robotics_related)
        new_physics_content = any(word in new_message_lower for word in physics_related)
        new_control_content = any(word in new_message_lower for word in control_related)

        # Count how many topic categories were in the previous context
        prev_topics = sum([prev_ai_content, prev_robotics_content, prev_physics_content, prev_control_content])
        new_topics = sum([new_ai_content, new_robotics_content, new_physics_content, new_control_content])

        # If there's a significant shift in topic coverage
        if prev_topics > 0 and new_topics == 0:
            return True  # New message doesn't match any previous topics
        elif prev_topics == 0 and new_topics > 0:
            return True  # New message introduces new topics
        elif prev_topics > 1 and new_topics == 1:
            # If previous context covered multiple topics but new message focuses on just one
            return True

        # Check for specific topic shifts (e.g., from AI to robotics)
        if (prev_ai_content and new_robotics_content and not prev_robotics_content) or \
           (prev_robotics_content and new_ai_content and not prev_ai_content):
            return True

        # Additional check: if the new message introduces a completely different subtopic
        # For example, if previous conversation was about control systems and now it's about ethics
        other_keywords = [
            'ethics', 'society', 'future', 'job', 'employment', 'privacy', 'security', 'safety',
            'design', 'manufacturing', 'cost', 'economics', 'history', 'philosophy', 'culture'
        ]
        prev_other_content = any(word in recent_lower for word in other_keywords)
        new_other_content = any(word in new_message_lower for word in other_keywords)

        if prev_other_content and new_other_content and prev_other_content != new_other_content:
            return True

        return False

    def get_recent_context_summary(self, max_messages: int = 5) -> str:
        """
        Get a summary of recent conversation context for use in generating responses
        """
        recent_messages = self.messages[-max_messages:] if len(self.messages) >= max_messages else self.messages
        if not recent_messages:
            return ""

        context_parts = []
        for msg in recent_messages:
            sender = "User" if msg.sender == "user" else "Assistant"
            context_parts.append(f"{sender}: {msg.text}")

        return "\n".join(context_parts)

    def get_topic_keywords(self) -> List[str]:
        """
        Extract and return key topics discussed in the conversation
        """
        all_text = " ".join([msg.text for msg in self.messages])
        all_text_lower = all_text.lower()

        # Keywords related to Physical AI & Humanoid Robotics
        keywords = []

        ai_keywords = [word for word in ['ai', 'artificial intelligence', 'machine learning', 'neural network', 'algorithm']
                      if word in all_text_lower]
        robotics_keywords = [word for word in ['robot', 'robotics', 'humanoid', 'actuator', 'sensor', 'locomotion']
                            if word in all_text_lower]
        physics_keywords = [word for word in ['physics', 'dynamics', 'kinematics', 'force', 'torque']
                           if word in all_text_lower]
        control_keywords = [word for word in ['control', 'controller', 'feedback', 'stability']
                           if word in all_text_lower]

        keywords.extend(ai_keywords)
        keywords.extend(robotics_keywords)
        keywords.extend(physics_keywords)
        keywords.extend(control_keywords)

        # Remove duplicates while preserving order
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        return unique_keywords


class ChatHistoryResponse(BaseModel):
    conversation_id: str
    messages: List[Message]


class HealthResponse(BaseModel):
    status: str = "OK"
    timestamp: datetime = Field(default_factory=datetime.now)


class ContentSearchRequest(BaseModel):
    query: str
    k: Optional[int] = 4


class ContentSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str


# Additional models for selected-text-only response logic
class ValidatedResponse(BaseModel):
    """
    Model for responses that have been validated to contain only book-sourced information
    """
    original_response: str
    validated_response: str
    is_from_book: bool
    sources: List[Dict[str, Any]]
    validation_notes: Optional[str] = None


class BookContent(BaseModel):
    """
    Model for book content that will be used in the RAG system
    """
    text: str
    source_file: str
    chunk_index: int
    total_chunks: int
    metadata: Optional[Dict[str, Any]] = {}
    section: Optional[str] = None
    topics: Optional[List[str]] = []
    page_number: Optional[int] = None
    chapter: Optional[str] = None
    relevance_score: Optional[float] = None


class ContentFilterRequest(BaseModel):
    """
    Model for content filtering requests
    """
    query: str
    filters: Dict[str, Any] = {}
    k: int = 4


class ContentFilterResponse(BaseModel):
    """
    Model for content filtering responses
    """
    query: str
    filters: Dict[str, Any]
    results: List[Dict[str, Any]]
    filtered_results_count: int


class ContentSearchByTopicRequest(BaseModel):
    """
    Model for topic-based content search requests
    """
    topic: str
    k: int = 4


class ContentSearchByTopicResponse(BaseModel):
    """
    Model for topic-based content search responses
    """
    topic: str
    summary: str
    results_count: int
    content: List[Dict[str, Any]]
    query: str