import React, { useState, useRef, useEffect } from 'react';
import { useColorMode } from '@docusaurus/theme-common';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);
  const { colorMode } = useColorMode();

  // Initialize input value with prepopulated text from localStorage (only on client)
  useEffect(() => {
    // Check if there's prepopulated text from text selection
    const savedText = localStorage.getItem('prepopulatedChatText');
    if (savedText) {
      localStorage.removeItem('prepopulatedChatText'); // Clear after use
      setInputValue(savedText);
    }
  }, []);

  // Function to scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to handle sending messages to the backend
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { role: 'user', content: inputValue, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          history: messages.map(msg => ({ role: msg.role, content: msg.content }))
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const botMessage = {
        role: 'assistant',
        content: data.response,
        sources: data.sources || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Function to handle text selection
  const handleTextSelection = () => {
    const selectedText = window.getSelection().toString().trim();
    if (selectedText) {
      setSelectedText(selectedText);
      // Auto-focus the input and add the selected text
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.focus();
          setInputValue(prev => prev + (prev ? ' ' : '') + selectedText);
        }
      }, 100);
    }
  };

  // Set up text selection listener
  useEffect(() => {
    const handleSelection = () => {
      setTimeout(handleTextSelection, 0);
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleTextSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleTextSelection);
    };
  }, []);

  // Handle Enter key press (without Shift for new line)
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Function to copy text to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className={`chat-container ${colorMode}`} role="main" aria-label="AI Chat Interface">
      <div className="chat-header" role="banner">
        <h3>AI Textbook Assistant</h3>
        <p>Ask questions about Physical AI & Humanoid Robotics</p>
      </div>

      <div className="chat-messages" role="log" aria-live="polite">
        {messages.length === 0 ? (
          <div className="welcome-message" role="article">
            <p>Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook.</p>
            <p>Ask me anything about the content, or select text on the page and I can provide more information.</p>
            <ul>
              <li>Ask about concepts like "Physical AI", "Humanoid Robotics", "ROS 2", etc.</li>
              <li>Select text on the page and I'll provide more context</li>
              <li>Ask for explanations of complex topics</li>
            </ul>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.role}`}
              role="article"
              aria-label={`${message.role} message`}
            >
              <div className="message-content">
                <div className="message-text" tabIndex="0" aria-label={`Message content: ${message.content}`}>
                  {message.content}
                </div>
                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    <details>
                      <summary aria-label="Toggle sources visibility">Sources:</summary>
                      <ul>
                        {message.sources.map((source, idx) => (
                          <li key={idx} aria-label={`Source: ${source.source}`}>
                            <strong>{source.source}</strong>: {source.text}
                          </li>
                        ))}
                      </ul>
                    </details>
                  </div>
                )}
                <button
                  className="copy-button"
                  onClick={() => copyToClipboard(message.content)}
                  title="Copy to clipboard"
                  aria-label={`Copy message to clipboard: ${message.content.substring(0, 50)}...`}
                >
                  Copy
                </button>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message assistant" role="status" aria-label="Assistant is typing">
            <div className="message-content">
              <div className="typing-indicator" aria-label="Assistant is typing">
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
                <span aria-hidden="true"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} aria-hidden="true" />
      </div>

      <div className="chat-input-area" role="form" aria-label="Chat input area">
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the textbook content..."
          rows="3"
          disabled={isLoading}
          aria-label="Type your message here"
          aria-required="true"
        />
        <button
          onClick={sendMessage}
          disabled={!inputValue.trim() || isLoading}
          className="send-button"
          aria-label="Send message"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>

      {selectedText && (
        <div
          className="selected-text-notification"
          role="status"
          aria-live="polite"
          aria-label={`Selected text: ${selectedText}`}
        >
          Selected: "{selectedText.substring(0, 50)}{selectedText.length > 50 ? '...' : ''}"
        </div>
      )}

      <style jsx>{`
        .chat-container {
          max-width: 800px;
          margin: 2rem auto;
          border: 1px solid var(--ifm-color-emphasis-300);
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
          display: flex;
          flex-direction: column;
          height: 600px;
          background-color: var(--ifm-background-surface-color);
          color: var(--ifm-font-color-base);
        }

        .chat-container.dark {
          background-color: #242526;
          color: #e4e5e6;
        }

        .chat-header {
          background-color: var(--ifm-color-primary);
          color: white;
          padding: 1rem;
        }

        .chat-header h3 {
          margin: 0 0 0.5rem 0;
        }

        .chat-header p {
          margin: 0;
          font-size: 0.9rem;
          opacity: 0.9;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .welcome-message {
          text-align: center;
          padding: 2rem;
          color: var(--ifm-color-emphasis-600);
        }

        .welcome-message ul {
          text-align: left;
          max-width: 500px;
          margin: 1rem auto;
        }

        .message {
          max-width: 85%;
          align-self: ${props => props.role === 'user' ? 'flex-end' : 'flex-start'};
        }

        .message.user {
          align-self: flex-end;
        }

        .message.assistant {
          align-self: flex-start;
        }

        .message-content {
          position: relative;
          padding: 0.75rem 1rem;
          border-radius: 12px;
          position: relative;
        }

        .message.user .message-content {
          background-color: var(--ifm-color-primary);
          color: white;
        }

        .message.assistant .message-content {
          background-color: var(--ifm-color-emphasis-100);
          color: var(--ifm-font-color-base);
        }

        .dark .message.assistant .message-content {
          background-color: #3a3b3c;
        }

        .message-text {
          margin-bottom: 0.5rem;
          line-height: 1.5;
        }

        .sources {
          font-size: 0.85rem;
          margin-top: 0.5rem;
          padding-top: 0.5rem;
          border-top: 1px solid var(--ifm-color-emphasis-300);
        }

        .sources summary {
          cursor: pointer;
          margin-bottom: 0.5rem;
        }

        .sources ul {
          margin: 0.5rem 0 0 0;
          padding-left: 1rem;
        }

        .sources li {
          margin-bottom: 0.5rem;
        }

        .copy-button {
          position: absolute;
          top: 0.25rem;
          right: 0.25rem;
          background: none;
          border: none;
          color: var(--ifm-color-emphasis-600);
          cursor: pointer;
          font-size: 0.75rem;
          opacity: 0.6;
        }

        .copy-button:hover {
          opacity: 1;
        }

        .typing-indicator {
          display: flex;
          gap: 0.25rem;
        }

        .typing-indicator span {
          width: 8px;
          height: 8px;
          background-color: var(--ifm-color-emphasis-600);
          border-radius: 50%;
          display: inline-block;
          animation: typing 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(2) {
          animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
          animation-delay: 0.4s;
        }

        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-5px); }
        }

        .chat-input-area {
          padding: 1rem;
          border-top: 1px solid var(--ifm-color-emphasis-300);
          display: flex;
          gap: 0.5rem;
        }

        textarea {
          flex: 1;
          padding: 0.75rem;
          border: 1px solid var(--ifm-color-emphasis-300);
          border-radius: 6px;
          resize: none;
          font-family: inherit;
          background-color: var(--ifm-background-surface-color);
          color: var(--ifm-font-color-base);
        }

        textarea:focus {
          outline: none;
          border-color: var(--ifm-color-primary);
        }

        .send-button {
          padding: 0.75rem 1.5rem;
          background-color: var(--ifm-color-primary);
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          white-space: nowrap;
        }

        .send-button:disabled {
          background-color: var(--ifm-color-emphasis-300);
          cursor: not-allowed;
        }

        .selected-text-notification {
          background-color: #e3f2fd;
          color: #1976d2;
          padding: 0.5rem 1rem;
          font-size: 0.85rem;
          text-align: center;
          border-top: 1px solid #bbdefb;
        }

        .dark .selected-text-notification {
          background-color: #193a56;
          color: #90caf9;
          border-top: 1px solid #152d4a;
        }

        /* Responsive design */
        @media (max-width: 768px) {
          .chat-container {
            margin: 1rem 1rem;
            height: 500px;
            max-width: 100%;
          }

          .chat-header {
            padding: 0.75rem;
          }

          .chat-header h3 {
            font-size: 1.25rem;
          }

          .chat-messages {
            padding: 0.75rem;
          }

          .message {
            max-width: 90%;
          }

          .chat-input-area {
            padding: 0.75rem;
            flex-direction: column;
          }

          textarea {
            width: 100%;
          }

          .send-button {
            align-self: flex-end;
            width: auto;
            min-width: 80px;
          }
        }

        @media (max-width: 480px) {
          .chat-container {
            height: 400px;
            margin: 0.5rem 0.5rem;
          }

          .chat-header h3 {
            font-size: 1.1rem;
          }

          .welcome-message {
            padding: 1rem;
          }

          .welcome-message ul {
            padding-left: 1rem;
          }

          .message-content {
            padding: 0.5rem 0.75rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;