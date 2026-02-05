import React from 'react';
import Layout from '@theme/Layout';
import ChatInterface from '@site/src/components/ChatInterface';

export default function ChatPage() {
  return (
    <Layout title="Chat with Physical AI & Humanoid Robotics Book" description="Interactive chat interface for the Physical AI & Humanoid Robotics book">
      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
        <ChatInterface />
      </div>
    </Layout>
  );
}