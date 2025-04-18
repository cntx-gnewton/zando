import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaFileDownload, FaSpinner } from 'react-icons/fa';
import axios from 'axios';
import FileUpload from '../components/dna/FileUpload';
import { useAnalysis } from '../hooks/useAnalysis';
import { useNotification } from '../hooks/useNotification';
import { analysisApi } from '../api/analysisApi';
import { reportApi } from '../api/reportApi';
import { ReportType } from '../types/report';
import { API_URL } from '../config';

const ReportPage: React.FC = () => {
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportId, setReportId] = useState<string | null>(null);
  const [reportUrl, setReportUrl] = useState<string | null>(null);
  const [selectedReportType, setSelectedReportType] = useState<ReportType>(ReportType.FULL);
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
        details: 'Please upload a DNA file before generating a report'
      });
      return;
    }
    
    try {
      setGeneratingReport(true);
      
      // We're not using useMockReport variable anymore, just debugMode directly
      
      // REAL REPORT GENERATION
      
      // Use the actual file hash and analysis ID from the current analysis
      let analysisId = currentAnalysis?.analysisId;
      let fileHash = currentAnalysis?.fileHash;
      
      // Step 1: Process the analysis if not already done
      if (currentAnalysis.status !== 'analyzed' || !currentAnalysis.analysisId) {
        console.log('Analysis not yet processed, running analysis first');
        try {
          const analysisResponse = await analysisApi.processAnalysis({
            file_hash: currentAnalysis.fileHash
          });
          
          if (!analysisResponse.analysis_id) {
            throw new Error('Failed to process DNA analysis');
          }
          
          analysisId = analysisResponse.analysis_id;
          console.log('Analysis completed with ID:', analysisId);
        } catch (error) {
          console.error('Analysis processing error:', error);
          throw new Error('Failed to process analysis: ' + (error instanceof Error ? error.message : String(error)));
        }
      }
      
      // Log analysis information
      console.log('Current analysis state before report generation:', currentAnalysis);
      
      // Step 2: Generate the report
      const reportRequest = {
        file_hash: fileHash,
        analysis_id: analysisId,
        report_type: selectedReportType
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
          Upload your DNA data file and generate a personalized report with insights about your genetic profile,
          skin characteristics, and product recommendations based on your unique genetic makeup.
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
          
          {/* Report Type Selection */}
          <div className="w-full mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Report Type:
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div 
                className={`border rounded-md p-3 cursor-pointer transition-colors ${
                  selectedReportType === ReportType.FULL 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-300'
                }`}
                onClick={() => setSelectedReportType(ReportType.FULL)}
              >
                <div className="flex items-center mb-1">
                  <input 
                    type="radio" 
                    checked={selectedReportType === ReportType.FULL} 
                    readOnly 
                    className="mr-2"
                  />
                  <span className="font-medium">Full Report</span>
                </div>
                <p className="text-xs text-gray-600">
                  Comprehensive analysis with all genetic insights and detailed recommendations.
                </p>
              </div>
              
              <div 
                className={`border rounded-md p-3 cursor-pointer transition-colors ${
                  selectedReportType === ReportType.SKIN_ONLY 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-300'
                }`}
                onClick={() => setSelectedReportType(ReportType.SKIN_ONLY)}
              >
                <div className="flex items-center mb-1">
                  <input 
                    type="radio" 
                    checked={selectedReportType === ReportType.SKIN_ONLY} 
                    readOnly 
                    className="mr-2"
                  />
                  <span className="font-medium">Skin-Focused Report</span>
                </div>
                <p className="text-xs text-gray-600">
                  Focused on skin characteristics and targeted skincare product recommendations.
                </p>
              </div>
              
              <div 
                className={`border rounded-md p-3 cursor-pointer transition-colors ${
                  selectedReportType === ReportType.SUMMARY 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-300'
                }`}
                onClick={() => setSelectedReportType(ReportType.SUMMARY)}
              >
                <div className="flex items-center mb-1">
                  <input 
                    type="radio" 
                    checked={selectedReportType === ReportType.SUMMARY} 
                    readOnly 
                    className="mr-2"
                  />
                  <span className="font-medium">Summary Report</span>
                </div>
                <p className="text-xs text-gray-600">
                  Brief overview of key genetic findings with concise recommendations.
                </p>
              </div>
              
              <div 
                className={`border rounded-md p-3 cursor-pointer transition-colors ${
                  selectedReportType === ReportType.STANDARD 
                    ? 'border-blue-500 bg-blue-50' 
                    : 'border-gray-300 hover:border-blue-300'
                }`}
                onClick={() => setSelectedReportType(ReportType.STANDARD)}
              >
                <div className="flex items-center mb-1">
                  <input 
                    type="radio" 
                    checked={selectedReportType === ReportType.STANDARD} 
                    readOnly 
                    className="mr-2"
                  />
                  <span className="font-medium">Standard Report</span>
                </div>
                <p className="text-xs text-gray-600">
                  Balanced report with important genetic markers and general recommendations.
                </p>
              </div>
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
              `Generate ${selectedReportType.charAt(0).toUpperCase() + selectedReportType.slice(1)} Report`
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