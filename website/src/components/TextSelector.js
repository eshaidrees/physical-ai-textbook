import React, { useState, useEffect } from 'react';

const TextSelector = ({ onTextSelected }) => {
  const [showButton, setShowButton] = useState(false);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [selectedText, setSelectedText] = useState('');

  useEffect(() => {
    const handleSelection = () => {
      const selection = window.getSelection();
      const text = selection.toString().trim();

      if (text.length > 0) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        setPosition({
          x: rect.left + rect.width / 2,
          y: rect.top - 10
        });

        setSelectedText(text);
        setShowButton(true);
      } else {
        setShowButton(false);
      }
    };

    const handleClick = () => {
      setTimeout(() => {
        const selection = window.getSelection();
        if (!selection.toString().trim()) {
          setShowButton(false);
        }
      }, 1);
    };

    document.addEventListener('mouseup', handleSelection);
    document.addEventListener('keyup', handleSelection);
    document.addEventListener('click', handleClick);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
      document.removeEventListener('keyup', handleSelection);
      document.removeEventListener('click', handleClick);
    };
  }, []);

  const handleAskAI = () => {
    if (selectedText && onTextSelected) {
      onTextSelected(selectedText);
    }
    setShowButton(false);
  };

  if (!showButton) {
    return null;
  }

  return (
    <button
      style={{
        position: 'fixed',
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: 'translateX(-50%)',
        zIndex: 10000,
        background: '#2563eb',
        color: 'white',
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        cursor: 'pointer',
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.2)',
        border: 'none',
        // Make sure it works well on mobile
        userSelect: 'none',
        WebkitUserSelect: 'none',
      }}
      onClick={handleAskAI}
      aria-label={`Ask AI about selected text: ${selectedText.substring(0, 30)}${selectedText.length > 30 ? '...' : ''}`}
      title="Ask AI about selected text"
    >
      Ask AI
    </button>
  );
};

export default TextSelector;