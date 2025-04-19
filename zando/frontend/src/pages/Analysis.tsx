import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { AnalysisResults } from '../components/analysis';
import { useAnalysis } from '../hooks/useAnalysis';
import { Link } from 'react-router-dom';
import { FaArrowLeft } from 'react-icons/fa';

const AnalysisPage: React.FC = () => {
  const { analysisId } = useParams<{ analysisId?: string }>();
  const { currentAnalysis } = useAnalysis();
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    // Simulating data loading
    const timer = setTimeout(() => {
      setLoading(false);
    }, 500);
    
    return () => clearTimeout(timer);
  }, []);
  
  // Now checks for either analysisId, currentAnalysis.analysisId, OR currentAnalysis.fileHash
  const hasAnalysisData = analysisId || currentAnalysis?.analysisId || currentAnalysis?.fileHash;
  
  return (
    <div className="py-6">
      <h1 className="text-2xl font-semibold text-gray-900 mb-6">
        {hasAnalysisData ? 'Analysis Results' : 'Your Analyses'}
      </h1>
      
      {hasAnalysisData ? (
        <AnalysisResults 
          analysisId={analysisId || currentAnalysis?.analysisId} 
          fileHash={currentAnalysis?.fileHash}
        />
      ) : (
        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-gray-500 mb-4">
            No analysis data available. Please upload a DNA file first.
          </p>
          <Link 
            to="/upload" 
            className="inline-flex items-center text-blue-600 hover:text-blue-800"
          >
            <FaArrowLeft className="mr-2" />
            Go to Upload Page
          </Link>
        </div>
      )}
    </div>
  );
};

export default AnalysisPage;