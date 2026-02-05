import React, { useState, useEffect, useRef } from 'react';
import './ChatInterface.css';

const ChatInterface = ({ isFloating = false }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [availableConversations, setAvailableConversations] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchPanel, setShowSearchPanel] = useState(false);
  const messagesEndRef = useRef(null);

  // Function to scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize a new conversation when component mounts
  useEffect(() => {
    const initializeConversation = async () => {
      try {
        // For now, we'll just create a new conversation ID locally
        // In a real app, you might fetch an existing conversation or create a new one via API
        const newConversationId = localStorage.getItem('currentConversationId') || `conv_${Date.now()}`;
        setConversationId(newConversationId);
        localStorage.setItem('currentConversationId', newConversationId);
      } catch (err) {
        console.error('Error initializing conversation:', err);
      }
    };

    initializeConversation();
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    // Add user message to chat
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      // Call backend API to get response
      const response = await fetch('http://localhost:8000/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          conversation_id: conversationId
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();

      // Update conversation ID if it was newly created
      if (data.conversation_id && !conversationId) {
        setConversationId(data.conversation_id);
        localStorage.setItem('currentConversationId', data.conversation_id);
      }

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        sender: 'bot',
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      setError('Failed to get response. Please try again.');
      console.error('Error sending message:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Function to load conversation history
  const loadConversationHistory = async (convId) => {
    if (!convId) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/chat/history/${convId}`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages);
      }
    } catch (err) {
      console.error('Error loading conversation history:', err);
    }
  };

  // Function to start a new conversation
  const startNewConversation = () => {
    setMessages([]);
    const newConversationId = `conv_${Date.now()}`;
    setConversationId(newConversationId);
    localStorage.setItem('currentConversationId', newConversationId);
  };

  // Function to search for specific content in the book
  const searchBookContent = async (query) => {
    if (!query.trim()) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          k: 4
        }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error searching book content:', err);
      throw err;
    }
  };

  // Function to search by topic
  const searchByTopic = async (topic) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/search/topic/${encodeURIComponent(topic)}?k=4`);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error searching by topic:', err);
      throw err;
    }
  };

  // Function to get topic summary
  const getTopicSummary = async (topic) => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/summary/topic/${encodeURIComponent(topic)}?k=4`);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      console.error('Error getting topic summary:', err);
      throw err;
    }
  };

  // Function to handle search
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const results = await searchBookContent(searchQuery);
      setSearchResults(results);
    } catch (err) {
      setError('Failed to search book content. Please try again.');
      console.error('Error during search:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Function to handle topic search
  const handleTopicSearch = async (topic) => {
    if (!topic.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const results = await searchByTopic(topic);
      setSearchResults(results);
    } catch (err) {
      setError('Failed to search by topic. Please try again.');
      console.error('Error during topic search:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Function to handle topic summary
  const handleGetTopicSummary = async (topic) => {
    if (!topic.trim()) return;

    setIsSearching(true);
    setError(null);

    try {
      const summary = await getTopicSummary(topic);
      setSearchResults(summary);
    } catch (err) {
      setError('Failed to get topic summary. Please try again.');
      console.error('Error getting topic summary:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Function to toggle search panel
  const toggleSearchPanel = () => {
    setShowSearchPanel(!showSearchPanel);
  };

  return (
    <div className={`chat-interface ${isFloating ? 'floating' : ''}`}>
      {!isFloating && (
        <div className="chat-header">
          <h2>Physical AI & Humanoid Robotics Chat</h2>
          <div className="conversation-controls">
            <button onClick={startNewConversation} className="new-conversation-button">
              New Conversation
            </button>
            <button onClick={toggleSearchPanel} className="search-panel-toggle-button">
              {showSearchPanel ? 'Hide Search' : 'Search Content'}
            </button>
            {conversationId && (
              <span className="conversation-id">ID: {conversationId.substring(0, 8)}...</span>
            )}
          </div>
        </div>
      )}

      {/* Search Panel */}
      {!isFloating && showSearchPanel && (
        <div className="search-panel">
          <div className="search-controls">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search book content..."
              className="search-input"
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button onClick={handleSearch} disabled={isSearching} className="search-button">
              {isSearching ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Quick topic search buttons */}
          <div className="quick-search-buttons">
            <button onClick={() => handleTopicSearch('AI')} className="quick-search-button">AI</button>
            <button onClick={() => handleTopicSearch('Robotics')} className="quick-search-button">Robotics</button>
            <button onClick={() => handleTopicSearch('Humanoid')} className="quick-search-button">Humanoid</button>
            <button onClick={() => handleTopicSearch('Control Systems')} className="quick-search-button">Control</button>
          </div>

          {/* Search results display */}
          {searchResults && (
            <div className="search-results">
              <h3>Search Results</h3>
              {searchResults.topic ? (
                // Topic summary results
                <div className="topic-summary-results">
                  <h4>Topic: {searchResults.topic}</h4>
                  <p><strong>Summary:</strong> {searchResults.summary}</p>
                  <p><strong>Results Count:</strong> {searchResults.results_count}</p>
                  {searchResults.content && searchResults.content.length > 0 && (
                    <div className="search-content-results">
                      <h5>Content:</h5>
                      {searchResults.content.map((item, index) => (
                        <div key={index} className="search-result-item">
                          <p>{item.text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                // Regular search results
                <div className="regular-search-results">
                  {searchResults.results && searchResults.results.length > 0 ? (
                    searchResults.results.map((result, index) => (
                      <div key={index} className="search-result-item">
                        <p>{result.text}</p>
                      </div>
                    ))
                  ) : (
                    <p>No results found for your query.</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      <div className="chat-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`message ${message.sender}-message`}
          >
            <div className="message-content">
              {message.text}
            </div>
            <div className="message-timestamp">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="message bot-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="chat-input-area">
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask a question about Physical AI & Humanoid Robotics..."
          className="chat-input"
          rows="3"
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;