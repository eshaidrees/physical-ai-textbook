// API service for connecting frontend chat to backend RAG endpoints
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

class ApiService {
  static async sendMessage(message, conversationId = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          conversation_id: conversationId
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  static async getConversationHistory(conversationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/history/${conversationId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting conversation history:', error);
      throw error;
    }
  }

  static async detectTopicShift(conversationId, query) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/detect-topic-shift/${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error detecting topic shift:', error);
      throw error;
    }
  }

  static async getContextSummary(conversationId) {
    try {
      const response = await fetch(`${API_BASE_URL}/chat/context-summary/${conversationId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting context summary:', error);
      throw error;
    }
  }

  static async getHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error checking health:', error);
      throw error;
    }
  }
}

export default ApiService;