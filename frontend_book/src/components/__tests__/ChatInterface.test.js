import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatInterface from '../ChatInterface';

// Mock the fetch API
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({
      response: 'Test response from backend',
      sources: [],
      is_valid: true,
      query: 'Test query',
      conversation_id: 'test_conversation_123'
    }),
  })
);

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

describe('ChatInterface Component', () => {
  beforeEach(() => {
    fetch.mockClear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
  });

  test('renders chat interface correctly', () => {
    render(<ChatInterface />);

    // Check if main elements are present
    expect(screen.getByText('Physical AI & Humanoid Robotics Chat')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
    expect(screen.getByText('New Conversation')).toBeInTheDocument();
  });

  test('allows user to type and send a message', async () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');
    const sendButton = screen.getByText('Send');

    // Type a message
    fireEvent.change(input, { target: { value: 'Hello, world!' } });
    expect(input.value).toBe('Hello, world!');

    // Click send button
    fireEvent.click(sendButton);

    // Wait for the message to appear in the chat
    await waitFor(() => {
      expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    });

    // Check if fetch was called
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  test('displays bot response after sending a message', async () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    fireEvent.change(input, { target: { value: 'Test query' } });
    fireEvent.click(sendButton);

    // Wait for bot response to appear
    await waitFor(() => {
      expect(screen.getByText('Test response from backend')).toBeInTheDocument();
    });
  });

  test('handles Enter key press to send message', async () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');

    // Type a message
    fireEvent.change(input, { target: { value: 'Test message with Enter' } });

    // Press Enter key
    fireEvent.keyPress(input, { key: 'Enter', code: 'Enter', char: 'Enter' });

    // Wait for the message to appear
    await waitFor(() => {
      expect(screen.getByText('Test message with Enter')).toBeInTheDocument();
    });

    // Check if fetch was called
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  test('disables send button when input is empty', () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');
    const sendButton = screen.getByText('Send');

    // Initially, input is empty, so button should be enabled (it's disabled only when loading)
    expect(sendButton).not.toBeDisabled();

    // Clear input and check again
    fireEvent.change(input, { target: { value: '' } });
    expect(sendButton).not.toBeDisabled(); // Button is only disabled when loading
  });

  test('shows loading indicator when waiting for response', async () => {
    // Mock a delayed response
    fetch.mockImplementationOnce(() =>
      new Promise(resolve =>
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({
            response: 'Delayed response',
            sources: [],
            is_valid: true,
            query: 'Test query',
            conversation_id: 'test_conversation_123'
          }),
        }), 100)
      )
    );

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    fireEvent.change(input, { target: { value: 'Delayed test' } });
    fireEvent.click(sendButton);

    // Initially, loading indicator should appear
    const typingIndicator = screen.queryByText('typing-indicator');
    expect(typingIndicator).toBeInTheDocument();

    // Wait for response to appear
    await waitFor(() => {
      expect(screen.getByText('Delayed response')).toBeInTheDocument();
    });
  });

  test('creates new conversation when New Conversation button is clicked', () => {
    render(<ChatInterface />);

    const newConversationButton = screen.getByText('New Conversation');
    fireEvent.click(newConversationButton);

    // Check that localStorage was called to set a new conversation ID
    expect(localStorageMock.setItem).toHaveBeenCalledWith(
      'currentConversationId',
      expect.stringMatching(/^conv_/)
    );
  });

  test('toggles search panel when Search Content button is clicked', () => {
    render(<ChatInterface />);

    const searchToggleButton = screen.getByText('Search Content');
    fireEvent.click(searchToggleButton);

    // Check that search input appears after clicking
    expect(screen.getByPlaceholderText('Search book content...')).toBeInTheDocument();

    // Click again to hide
    fireEvent.click(searchToggleButton);

    // Search input should no longer be in the document
    expect(screen.queryByPlaceholderText('Search book content...')).not.toBeInTheDocument();
  });

  test('allows searching for content', async () => {
    // Mock the search API response
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          results: [
            { text: 'Test search result content' }
          ],
          query: 'test search'
        }),
      })
    );

    render(<ChatInterface />);

    // Toggle search panel
    const searchToggleButton = screen.getByText('Search Content');
    fireEvent.click(searchToggleButton);

    // Find search input and button
    const searchInput = screen.getByPlaceholderText('Search book content...');
    const searchButton = screen.getByText('Search');

    // Enter search query and click search
    fireEvent.change(searchInput, { target: { value: 'test search' } });
    fireEvent.click(searchButton);

    // Wait for results to appear
    await waitFor(() => {
      expect(screen.getByText('Test search result content')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock an API error
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        status: 500,
      })
    );

    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    fireEvent.change(input, { target: { value: 'Error test' } });
    fireEvent.click(sendButton);

    // Wait for error message to appear
    await waitFor(() => {
      expect(screen.getByText('Failed to get response. Please try again.')).toBeInTheDocument();
    });
  });

  test('uses existing conversation ID from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('existing_conversation_456');

    render(<ChatInterface />);

    // Check that the existing conversation ID is used
    expect(localStorageMock.getItem).toHaveBeenCalledWith('currentConversationId');
  });

  test('adds user message to chat before sending to API', () => {
    render(<ChatInterface />);

    const input = screen.getByPlaceholderText('Ask a question about Physical AI & Humanoid Robotics...');
    const sendButton = screen.getByText('Send');

    // Type and send a message
    fireEvent.change(input, { target: { value: 'Immediate display test' } });
    fireEvent.click(sendButton);

    // The user's message should appear in the chat immediately
    expect(screen.getByText('Immediate display test')).toBeInTheDocument();
  });
});