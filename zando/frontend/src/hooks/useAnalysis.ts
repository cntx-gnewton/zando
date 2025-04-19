import { useContext } from 'react';
import { AnalysisContext } from '../contexts/AnalysisContext';
import { AnalysisState, AnalysisData } from '../types';

/**
 * Hook for accessing and updating analysis state.
 */
export const useAnalysis = () => {
  const context = useContext(AnalysisContext);
  
  if (!context) {
    throw new Error('useAnalysis must be used within an AnalysisProvider');
  }
  
  const { currentAnalysis, setCurrentAnalysis } = context;
  
  /**
   * Reset analysis state
   */
  const resetAnalysis = () => {
    setCurrentAnalysis({
      status: 'idle'
    });
  };
  
  /**
   * Set analysis to uploading state
   */
  const setUploading = (fileName: string) => {
    setCurrentAnalysis({
      fileName,
      status: 'uploaded'
    });
  };
  
  /**
   * Set analysis to analyzing state
   */
  const setAnalyzing = (fileHash: string) => {
    setCurrentAnalysis((prev) => ({
      ...prev,
      fileHash,
      status: 'analyzing'
    }));
  };
  
  /**
   * Set analysis to analyzed state with data
   */
  const setAnalyzed = (analysisId: string, data: AnalysisData) => {
    setCurrentAnalysis((prev) => ({
      ...prev,
      analysisId,
      status: 'analyzed',
      data
    }));
  };
  
  /**
   * Set analysis to error state
   */
  const setError = (error: string) => {
    setCurrentAnalysis((prev) => ({
      ...prev,
      status: 'error',
      error
    }));
  };
  
  return {
    currentAnalysis,
    setCurrentAnalysis,
    resetAnalysis,
    setUploading,
    setAnalyzing,
    setAnalyzed,
    setError
  };
};

export default useAnalysis;