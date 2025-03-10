import React, { useState, useEffect } from 'react';
import { FaSpinner, FaExclamationTriangle, FaDna, FaLeaf } from 'react-icons/fa';
import { useAnalysis } from '../../hooks/useAnalysis';
import { analysisApi } from '../../api/analysisApi';
import { AnalysisResult } from '../../types/analysis';
import GeneCard from './GeneCard';
import IngredientRecommendations from './IngredientRecommendations';

type AnalysisResultsProps = {
  analysisId?: string;
  fileHash?: string;
};

const AnalysisResults: React.FC<AnalysisResultsProps> = ({ analysisId, fileHash }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResult | null>(null);
  
  const { currentAnalysis, setCurrentAnalysis } = useAnalysis();
  
  useEffect(() => {
    const fetchAnalysisResults = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let analysisResult;
        
        // If we have an analysis ID, use that
        if (analysisId) {
          analysisResult = await analysisApi.getAnalysisResults(analysisId);
        }
        // Otherwise, if we have a file hash, process the analysis
        else if (fileHash) {
          const processResponse = await analysisApi.processAnalysis({
            file_hash: fileHash,
            force_refresh: false
          });
          
          // Update the analysis context with the new ID
          setCurrentAnalysis({
            ...currentAnalysis,
            analysisId: processResponse.analysis_id,
            status: 'analyzed'
          });
          
          // Fetch the results
          analysisResult = await analysisApi.getAnalysisResults(processResponse.analysis_id);
        } else {
          throw new Error('Either analysisId or fileHash must be provided');
        }
        
        setResults(analysisResult);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalysisResults();
  }, [analysisId, fileHash, currentAnalysis, setCurrentAnalysis]);
  
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <FaSpinner className="animate-spin text-4xl text-blue-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-700">Analyzing your genetic data...</h2>
        <p className="text-gray-500 mt-2">This may take a moment as we process your DNA information.</p>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FaExclamationTriangle className="text-4xl text-amber-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-700">Unable to load analysis results</h2>
        <p className="text-gray-500 mt-2 max-w-md">{error}</p>
        <button 
          className="mt-6 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
          onClick={() => window.location.reload()}
        >
          Try Again
        </button>
      </div>
    );
  }
  
  if (!results || !results.data) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <FaExclamationTriangle className="text-4xl text-amber-500 mb-4" />
        <h2 className="text-xl font-semibold text-gray-700">No genetic findings</h2>
        <p className="text-gray-500 mt-2">We couldn't find any relevant genetic markers in your DNA data.</p>
      </div>
    );
  }
  
  const { mutations, ingredient_recommendations, summary } = results.data;
  
  return (
    <div className="space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">Your Genetic Skin Profile</h2>
        
        {summary && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <p className="text-gray-700 leading-relaxed">{summary}</p>
          </div>
        )}
        
        <div className="flex items-center text-gray-700 mb-2">
          <FaDna className="mr-2 text-blue-500" />
          <h3 className="text-lg font-semibold">Genetic Findings</h3>
        </div>
        
        {mutations.length === 0 ? (
          <p className="text-gray-500 italic">No genetic variants of interest were found.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
            {mutations.map((mutation, index) => (
              <GeneCard key={index} gene={mutation} />
            ))}
          </div>
        )}
      </div>
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center text-gray-700 mb-4">
          <FaLeaf className="mr-2 text-green-500" />
          <h3 className="text-lg font-semibold">Ingredient Recommendations</h3>
        </div>
        
        <IngredientRecommendations recommendations={ingredient_recommendations} />
      </div>
    </div>
  );
};

export default AnalysisResults;