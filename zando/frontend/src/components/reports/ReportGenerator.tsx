import React, { useState } from 'react';
import { FaFileAlt, FaSpinner, FaDownload, FaCheckCircle } from 'react-icons/fa';
import { useAnalysis } from '../../hooks/useAnalysis';
import { useNotification } from '../../hooks/useNotification';
import { reportApi } from '../../api/reportApi';
import { ReportResponse } from '../../types/report';

type ReportGeneratorProps = {
  onReportGenerated?: (reportId: string) => void;
};

const ReportGenerator: React.FC<ReportGeneratorProps> = ({ onReportGenerated }) => {
  const [generating, setGenerating] = useState(false);
  const [reportResponse, setReportResponse] = useState<ReportResponse | null>(null);
  // Always use markdown format
  const reportType = 'markdown';
  
  const { currentAnalysis } = useAnalysis();
  const { showNotification } = useNotification();
  
  const generateReport = async () => {
    if (!currentAnalysis?.fileHash && !currentAnalysis?.analysisId) {
      showNotification({
        type: 'error',
        message: 'No analysis data available',
        details: 'You need to upload and analyze a DNA file first'
      });
      return;
    }
    
    setGenerating(true);
    
    try {
      const response = await reportApi.generateReport({
        file_hash: currentAnalysis.fileHash,
        analysis_id: currentAnalysis.analysisId,
        report_type: reportType
      });
      
      setReportResponse(response);
      
      showNotification({
        type: 'success',
        message: 'Report generated successfully',
        details: response.cached ? 'Retrieved from cache' : 'New report created'
      });
      
      if (onReportGenerated) {
        onReportGenerated(response.report_id);
      }
    } catch (error) {
      showNotification({
        type: 'error',
        message: 'Failed to generate report',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    } finally {
      setGenerating(false);
    }
  };
  
  const handleDownload = () => {
    if (reportResponse?.report_id) {
      reportApi.downloadReport(reportResponse.report_id);
    }
  };
  
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-4">
        <FaFileAlt className="text-2xl text-blue-500 mr-3" />
        <h2 className="text-xl font-semibold text-gray-800">Generate Your Personalized Report</h2>
      </div>
      
      <p className="text-gray-600 mb-6">
        Create a comprehensive PDF report based on your genetic analysis. This document includes
        your genetic findings, skin characteristics, and personalized ingredient recommendations.
      </p>
      
      <div className="mb-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-medium text-blue-800 mb-2">Modern Report Format</h3>
          <p className="text-sm text-blue-700">
            Your report will be generated with a modern, beautifully formatted layout with enhanced typography
            and visual elements to make it easy to understand your genetic insights.
          </p>
        </div>
      </div>
      
      {!reportResponse ? (
        <button
          onClick={generateReport}
          disabled={generating || !currentAnalysis}
          className={`w-full py-3 rounded-lg font-medium transition ${
            generating || !currentAnalysis
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {generating ? (
            <span className="flex items-center justify-center">
              <FaSpinner className="animate-spin mr-2" />
              Generating Report...
            </span>
          ) : (
            'Generate Report'
          )}
        </button>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center p-4 bg-green-50 rounded-lg">
            <FaCheckCircle className="text-xl text-green-500 mr-3" />
            <div>
              <p className="font-medium text-gray-800">Report Ready!</p>
              <p className="text-sm text-gray-600">
                {reportResponse.cached
                  ? 'Retrieved from previously generated report'
                  : `Generated in ${reportResponse.processing_time?.toFixed(1) || '0.0'}s`}
              </p>
            </div>
          </div>
          
          <button
            onClick={handleDownload}
            className="w-full py-3 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition flex items-center justify-center"
          >
            <FaDownload className="mr-2" />
            Download PDF Report
          </button>
        </div>
      )}
      
      {!currentAnalysis && (
        <p className="mt-4 text-sm text-amber-600">
          You need to upload and analyze a DNA file before generating a report.
        </p>
      )}
    </div>
  );
};

export default ReportGenerator;