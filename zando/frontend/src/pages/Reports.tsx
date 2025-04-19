import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FaFileAlt, FaDownload, FaSpinner } from 'react-icons/fa';
import { ReportGenerator } from '../components/reports';
import { useAnalysis } from '../hooks/useAnalysis';
import { reportApi } from '../api/reportApi';

const ReportsPage: React.FC = () => {
  const { reportId } = useParams<{ reportId?: string }>();
  const { currentAnalysis } = useAnalysis();
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<any[]>([]);
  
  useEffect(() => {
    // Simulating report data loading
    const timer = setTimeout(() => {
      setLoading(false);
      // Mock data for demonstration
      setReports([
        {
          id: 'report-123',
          title: 'Genetic Skin Analysis Report',
          created_at: new Date().toISOString(),
          analysis_id: 'analysis-456',
          file_size: '2.4 MB'
        },
        {
          id: 'report-456',
          title: 'Comprehensive Genomic Report',
          created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          analysis_id: 'analysis-789',
          file_size: '3.1 MB'
        }
      ]);
    }, 500);
    
    return () => clearTimeout(timer);
  }, []);
  
  const handleDownload = (id: string) => {
    reportApi.downloadReport(id);
  };
  
  if (reportId) {
    return (
      <div className="py-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-semibold text-gray-900">Report Details</h1>
          <Link to="/reports" className="text-blue-600 hover:text-blue-500">
            Back to Reports
          </Link>
        </div>
        
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-start">
            <div>
              <h2 className="text-xl font-medium text-gray-900">Genetic Skin Analysis Report</h2>
              <p className="text-gray-500">Generated from analysis #{reportId}</p>
            </div>
            <button 
              onClick={() => handleDownload(reportId)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center"
            >
              <FaDownload className="mr-2" />
              Download PDF
            </button>
          </div>
          
          <div className="mt-6 border-t border-gray-200 pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-3">Report Preview</h3>
            <div className="bg-gray-100 rounded-lg p-8 flex justify-center items-center">
              <div className="text-center">
                <FaFileAlt className="h-16 w-16 text-gray-400 mx-auto" />
                <p className="mt-4 text-gray-600">
                  PDF preview not available. Please download to view the full report.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">Your Reports</h1>
      
      {currentAnalysis?.analysisId && (
        <div className="mb-6">
          <ReportGenerator />
        </div>
      )}
      
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generated Reports</h2>
        
        {loading ? (
          <div className="flex justify-center py-12">
            <FaSpinner className="animate-spin text-blue-500 h-8 w-8" />
          </div>
        ) : reports.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {reports.map((report) => (
              <div key={report.id} className="py-4 flex items-center justify-between">
                <div className="flex items-center">
                  <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <FaFileAlt className="h-5 w-5 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <Link to={`/reports/${report.id}`} className="text-sm font-medium text-gray-900 hover:text-blue-600">
                      {report.title}
                    </Link>
                    <p className="text-sm text-gray-500">
                      Created {new Date(report.created_at).toLocaleDateString()} • {report.file_size}
                    </p>
                  </div>
                </div>
                <button 
                  onClick={() => handleDownload(report.id)}
                  className="ml-4 px-3 py-1.5 bg-white border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50 flex items-center"
                >
                  <FaDownload className="mr-1.5 text-gray-500" />
                  Download
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FaFileAlt className="h-12 w-12 text-gray-300 mx-auto" />
            <p className="mt-4 text-gray-500">No reports have been generated yet.</p>
            <p className="text-sm text-gray-400">
              Upload a DNA file and analyze it to generate your first report.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;