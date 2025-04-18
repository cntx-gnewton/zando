import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AppRoutes from './routes';
import { AnalysisProvider } from './contexts/AnalysisContext';
import { NotificationProvider } from './contexts/NotificationContext';
import './App.css';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <NotificationProvider>
        <AnalysisProvider>
          <AppRoutes />
        </AnalysisProvider>
      </NotificationProvider>
    </BrowserRouter>
  );
};

export default App;