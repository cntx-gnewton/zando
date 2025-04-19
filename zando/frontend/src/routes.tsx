import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';

// Page components
import HomePage from './pages/Home';
import DashboardPage from './pages/Dashboard';
import ReportPage from './pages/ReportPage';
import ReportsPage from './pages/Reports';
import AccountPage from './pages/Account';
import NotFoundPage from './pages/NotFound';

// Layout components
import MainLayout from './components/layout/MainLayout';
import { ProtectedRoute } from './components/auth';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="*" element={<NotFoundPage />} />
        
        {/* Protected routes - require authentication */}
        <Route element={<ProtectedRoute />}>
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="report" element={<ReportPage />} />
          <Route path="account" element={<AccountPage />} />
          
          <Route path="reports">
            <Route index element={<ReportsPage />} />
            <Route path=":reportId" element={<ReportsPage />} />
          </Route>
        </Route>
        
        {/* Redirects from old paths */}
        <Route path="upload" element={<Navigate to="/report" replace />} />
        <Route path="analysis" element={<Navigate to="/report" replace />} />
        <Route path="analysis/:analysisId" element={<Navigate to="/report" replace />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;