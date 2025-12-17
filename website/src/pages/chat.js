import React from 'react';
import Layout from '@theme/Layout';
import ChatInterface from '../components/ChatInterface';

function ChatPage() {
  return (
    <Layout
      title="AI Chatbot"
      description="Chat with the Physical AI & Humanoid Robotics textbook using our AI-powered assistant">
      <div className="container margin-vert--lg">
        <div className="row">
          <div className="col col--12">
            <h1>AI-Powered Textbook Assistant</h1>
            <p>
              Ask questions about Physical AI & Humanoid Robotics, and our AI assistant will provide answers
              based on the textbook content. Select text on any page and ask questions about it for more context.
            </p>
            <ChatInterface />
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default ChatPage;