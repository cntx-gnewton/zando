import React, { ReactNode } from 'react';
import { AnalysisProvider } from './AnalysisContext';
import { NotificationProvider } from './NotificationContext';
import { AuthProvider } from './AuthContext';

interface AppProvidersProps {
  children: ReactNode;
}

/**
 * Combined provider component for the application
 */
export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
  return (
    <AuthProvider>
      <NotificationProvider>
        <AnalysisProvider>
          {children}
        </AnalysisProvider>
      </NotificationProvider>
    </AuthProvider>
  );
};