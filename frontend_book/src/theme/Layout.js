import React from 'react';
import Layout from '@theme-original/Layout';
import FloatingChatbot from '@site/src/components/FloatingChatbot';

export default function LayoutWrapper(props) {
  return (
    <>
      <Layout {...props}>
        {props.children}
        <FloatingChatbot />
      </Layout>
    </>
  );
}