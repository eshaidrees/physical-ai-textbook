import React, { useState } from 'react';
import TextSelector from './TextSelector';

const LayoutWrapper = ({ children }) => {
  const [selectedText, setSelectedText] = useState('');

  const handleTextSelected = (text) => {
    setSelectedText(text);
    // Scroll to the chat interface or open a modal
    const chatElement = document.querySelector('.chat-container');
    if (chatElement) {
      chatElement.scrollIntoView({ behavior: 'smooth' });
      // Optionally, populate the chat input with the selected text
      const chatInput = document.querySelector('.chat-input-area textarea');
      if (chatInput && text) {
        chatInput.value = text;
        chatInput.focus();
      }
    } else {
      // If no chat container is found, redirect to the chat page
      window.location.href = '/chat';
      // Store the selected text in localStorage to use on the chat page
      localStorage.setItem('prepopulatedChatText', text);
    }
  };

  return (
    <>
      <TextSelector onTextSelected={handleTextSelected} />
      {children}
    </>
  );
};

export default LayoutWrapper;