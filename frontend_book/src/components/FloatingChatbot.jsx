import React, { useState } from 'react';
import ChatInterface from './ChatInterface';
import './FloatingChatbot.css';

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [showFullChat, setShowFullChat] = useState(false);

  const toggleChat = () => {
    if (!isOpen) {
      setIsOpen(true);
      // Small delay to allow the chat to open before showing full interface
      setTimeout(() => setShowFullChat(true), 10);
    } else {
      setShowFullChat(false);
      // Small delay to allow the close animation to complete
      setTimeout(() => setIsOpen(false), 300);
    }
  };

  return (
    <div className="floating-chatbot">
      {isOpen && (
        <div className={`chat-window ${showFullChat ? 'show' : ''}`}>
          <div className="chat-header">
            <h3>AI Assistant</h3>
            <button className="close-button" onClick={toggleChat}>×</button>
          </div>
          <div className="chat-content">
            <ChatInterface isFloating={true} />
          </div>
        </div>
      )}

      <button
        className={`chat-icon ${isOpen ? 'open' : ''}`}
        onClick={toggleChat}
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H16.42L15.17 19.74C14.95 20.2 14.5 20.5 14 20.5C13.5 20.5 13.05 20.2 12.83 19.74L11.58 17H5C4.46957 17 3.96086 16.7893 3.58579 16.4142C3.21071 16.0391 3 15.5304 3 15V6C3 5.46957 3.21071 4.96086 3.58579 4.58579C3.96086 4.21071 4.46957 4 5 4H19C19.5304 4 20.0391 4.21071 20.4142 4.58579C20.7893 4.96086 21 5.46957 21 6V15Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <path d="M9 9H15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
          <path d="M9 12H15" stroke="white" strokeWidth="2" strokeLinecap="round"/>
        </svg>
      </button>
    </div>
  );
};

export default FloatingChatbot;