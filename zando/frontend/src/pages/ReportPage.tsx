import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaFileDownload, FaSpinner } from 'react-icons/fa';
import axios from 'axios';
import FileUpload from '../components/dna/FileUpload';
import { useAnalysis } from '../hooks/useAnalysis';
import { useNotification } from '../hooks/useNotification';
import { reportApi } from '../api/reportApi';
import { API_URL } from '../config';

const ReportPage: React.FC = () => {
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportId, setReportId] = useState<string | null>(null);
  const [reportUrl, setReportUrl] = useState<string | null>(null);
  // Always use markdown report type
  const reportType = 'markdown';
  const [debugMode, setDebugMode] = useState(false);
  
  const navigate = useNavigate();
  const { currentAnalysis } = useAnalysis();
  const { showNotification } = useNotification();
  
  const handleFileProcessed = (fileHash: string) => {
    console.log('File processed with hash:', fileHash);
  };
  
  const handleGenerateReport = async () => {
    if (!currentAnalysis?.fileHash && !debugMode) {
      showNotification({
        type: 'error',
        message: 'No DNA file uploaded',
        details: 'Please upload a DNA file first to generate your report'
      });
      return;
    }
    
    try {
      setGeneratingReport(true);
      
      // Use the file hash directly from the current analysis
      const fileHash = currentAnalysis?.fileHash;
      
      // Skip analysis step and directly generate the report
      console.log('Generating report directly from file hash');
      
      // Create report request using just the file hash with markdown format
      const reportRequest = {
        file_hash: fileHash,
        report_type: reportType
      };
      console.log('Report request:', reportRequest);
      
      const reportResponse = await reportApi.generateReport(reportRequest, debugMode);
      console.log('Report response:', reportResponse);
      
      setReportId(reportResponse.report_id);
      
      // Get the download URL
      const downloadUrl = reportApi.getReportDownloadUrl(reportResponse.report_id);
      setReportUrl(downloadUrl);
      
      showNotification({
        type: 'success',
        message: 'Report generated successfully',
        details: 'Your report is ready to download'
      });
      
    } catch (error) {
      console.error('Report Generation Error:', error);
      
      // More detailed error logging for Axios errors
      if (axios.isAxiosError(error)) {
        console.error('API Error Response:', error.response?.data);
        console.error('API Error Status:', error.response?.status);
        console.error('API Error Headers:', error.response?.headers);
        
        // Show more detailed notification with API error details
        showNotification({
          type: 'error',
          message: 'Failed to generate report',
          details: error.response?.data?.detail || 
                   error.response?.data?.message || 
                   `API Error: ${error.response?.status} ${error.message}`
        });
      } else {
        // For non-Axios errors
        showNotification({
          type: 'error',
          message: 'Failed to generate report',
          details: error instanceof Error ? error.message : 'Unknown error occurred'
        });
      }
    } finally {
      setGeneratingReport(false);
    }
  };
  
  const handleDownloadReport = () => {
    if (reportId) {
      reportApi.downloadReport(reportId, debugMode);
    }
  };
  
  // Toggle debug mode
  const toggleDebugMode = () => {
    setDebugMode(!debugMode);
  };
  
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Generate Genetic Report</h2>
          <div className="flex items-center">
            <label className="inline-flex items-center mr-4">
              <input
                type="checkbox"
                checked={debugMode}
                onChange={() => setDebugMode(!debugMode)}
                className="form-checkbox h-4 w-4 text-blue-600"
              />
              <span className="ml-2 text-sm text-gray-600">Debug Mode</span>
            </label>
            
            <button 
              onClick={toggleDebugMode} 
              className="text-xs text-gray-500 hover:text-blue-500"
            >
              {debugMode ? 'Hide Debug Info' : 'Show Debug Info'}
            </button>
          </div>
        </div>
        
        <p className="text-gray-600 mb-6">
          Upload your DNA data file to generate a personalized report with insights about your genetic profile,
          skin characteristics, and product recommendations tailored to your unique DNA.
        </p>
        
        <div className="mb-8">
          <FileUpload onFileProcessed={handleFileProcessed} />
        </div>
        
        <div className="flex flex-col items-center border-t border-gray-200 pt-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to generate your report?</h3>
          
          {currentAnalysis?.fileName && (
            <div className="bg-blue-50 w-full rounded-md p-3 mb-4">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Selected file:</span> {currentAnalysis.fileName}
              </p>
              {currentAnalysis.snpCount && (
                <p className="text-sm text-gray-700">
                  <span className="font-medium">SNPs detected:</span> {currentAnalysis.snpCount.toLocaleString()}
                </p>
              )}
            </div>
          )}
          
          {/* Information about the report - no options for report type */}
          <div className="w-full mb-6">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-medium text-blue-800 mb-2">Personalized Genetic Report</h3>
              <p className="text-sm text-blue-700">
                Your report will include comprehensive analysis with genetic insights and personalized skincare 
                recommendations based on your DNA data.
              </p>
            </div>
          </div>
          
          <button
            onClick={handleGenerateReport}
            disabled={!currentAnalysis?.fileHash || generatingReport}
            className={`flex items-center justify-center w-full px-6 py-3 rounded-md text-white font-medium 
              ${!currentAnalysis?.fileHash || generatingReport ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}
          >
            {generatingReport ? (
              <>
                <FaSpinner className="animate-spin mr-2" />
                Generating Report...
              </>
            ) : (
              "Generate My Personalized Report"
            )}
          </button>
          
          {reportUrl && (
            <div className="mt-8 w-full text-center">
              <div className="bg-green-50 border border-green-100 rounded-md p-4 mb-4">
                <p className="text-green-800 font-medium">Your report is ready!</p>
                <p className="text-sm text-gray-600 mt-1">Click the button below to download your personalized genetic report.</p>
              </div>
              
              <button
                onClick={handleDownloadReport}
                className="flex items-center justify-center mx-auto px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                <FaFileDownload className="mr-2" />
                Download Report
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Debug Console */}
      {debugMode && (
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-auto max-h-96">
          <h3 className="text-white font-bold mb-2">Debug Console</h3>
          <div className="mb-4">
            <p className="text-yellow-300 font-bold">Current Analysis State:</p>
            <pre>{JSON.stringify(currentAnalysis, null, 2)}</pre>
          </div>
          
          <div className="mb-4">
            <p className="text-yellow-300 font-bold">API URL:</p>
            <pre>{API_URL}</pre>
          </div>
          
          <div className="mb-4">
            <p className="text-yellow-300 font-bold">Debug Mode:</p>
            <div className="flex items-center">
              <pre className="mr-3">{debugMode ? 'Enabled' : 'Disabled'}</pre>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              When enabled, debug mode will bypass API calls and use mock data for testing
            </p>
          </div>
          
          <div className="mb-4">
            <button 
              onClick={() => {
                window.open(`${API_URL}/docs`, '_blank');
              }}
              className="bg-blue-700 text-white px-2 py-1 rounded text-xs"
            >
              Open API Docs
            </button>
          </div>
          
          <div className="mt-4">
            <p className="text-white text-xs">
              To see full error details, open the browser's developer console (F12 or Ctrl+Shift+I)
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReportPage;