import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './routes';
import { AnalysisProvider } from './contexts/AnalysisContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { AuthProvider } from './contexts/AuthContext';
import { FEATURES } from './config';
import './App.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <NotificationProvider>
        {FEATURES.USER_AUTHENTICATION ? (
          // When authentication is enabled, wrap the app with AuthProvider
          <AuthProvider>
            <AnalysisProvider>
              <AppRoutes />
            </AnalysisProvider>
          </AuthProvider>
        ) : (
          // When authentication is disabled, don't use AuthProvider
          <AnalysisProvider>
            <AppRoutes />
          </AnalysisProvider>
        )}
      </NotificationProvider>
    </BrowserRouter>
  );
};

export default App;