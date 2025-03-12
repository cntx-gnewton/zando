import React from 'react';
import { Route, Routes } from 'react-router-dom';

// Page components (to be created)
import HomePage from './pages/Home';
import DashboardPage from './pages/Dashboard';
import UploadPage from './pages/Upload';
import AnalysisPage from './pages/Analysis';
import ReportsPage from './pages/Reports';
import AccountPage from './pages/Account';
import NotFoundPage from './pages/NotFound';

// Layout components
import MainLayout from './components/layout/MainLayout';

const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<MainLayout />}>
        <Route index element={<HomePage />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="analysis">
          <Route index element={<AnalysisPage />} />
          <Route path=":analysisId" element={<AnalysisPage />} />
        </Route>
        <Route path="reports">
          <Route index element={<ReportsPage />} />
          <Route path=":reportId" element={<ReportsPage />} />
        </Route>
        <Route path="account" element={<AccountPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;