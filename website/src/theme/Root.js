import React from 'react';
import LayoutWrapper from '../components/LayoutWrapper';
import { UserPreferencesProvider } from '../contexts/UserPreferencesContext';

// Default implementation, that you can customize
function Root({ children }) {
  return (
    <UserPreferencesProvider>
      <LayoutWrapper>{children}</LayoutWrapper>
    </UserPreferencesProvider>
  );
}

export default Root;