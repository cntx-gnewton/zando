import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';

// Page components
import HomePage from './pages/Home';
import DashboardPage from './pages/Dashboard';
import ReportPage from './pages/ReportPage';
import ReportsPage from './pages/Reports';
import AccountPage from './pages/Account';
import NotFoundPage from './pages/NotFound';

// Auth components
import Login from './components/auth/Login';
import Register from './components/auth/Register';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Layout components
import MainLayout from './components/layout/MainLayout';

// Config
import { FEATURES } from './config';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        {/* Public routes */}
        <Route index element={<HomePage />} />
        
        {/* Auth routes - only add if auth feature is enabled */}
        {FEATURES.USER_AUTHENTICATION && (
          <>
            <Route path="login" element={<Login />} />
            <Route path="register" element={<Register />} />
          </>
        )}
        
        {/* Protected routes with authentication */}
        {FEATURES.USER_AUTHENTICATION ? (
          <>
            <Route path="dashboard" element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            } />
            <Route path="report" element={
              <ProtectedRoute>
                <ReportPage />
              </ProtectedRoute>
            } />
            <Route path="reports" element={
              <ProtectedRoute>
                <ReportsPage />
              </ProtectedRoute>
            } />
            <Route path="reports/:reportId" element={
              <ProtectedRoute>
                <ReportsPage />
              </ProtectedRoute>
            } />
            <Route path="account" element={
              <ProtectedRoute>
                <AccountPage />
              </ProtectedRoute>
            } />
          </>
        ) : (
          /* When auth is disabled, don't require authentication */
          <>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="report" element={<ReportPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="reports/:reportId" element={<ReportsPage />} />
            <Route path="account" element={<AccountPage />} />
          </>
        )}
        
        {/* Redirects from old paths */}
        <Route path="upload" element={<Navigate to="/report" replace />} />
        <Route path="analysis" element={<Navigate to="/report" replace />} />
        <Route path="analysis/:analysisId" element={<Navigate to="/report" replace />} />
        
        {/* Catch all route */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;