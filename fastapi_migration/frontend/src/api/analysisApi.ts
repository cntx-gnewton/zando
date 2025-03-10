import axios from 'axios';
import { API_URL } from '../config';
import { AnalysisRequest, AnalysisResponse, AnalysisResult } from '../types/analysis';

/**
 * API client for genetic analysis operations
 */
export const analysisApi = {
  /**
   * Process DNA data and perform genetic analysis
   * 
   * @param request - Analysis request containing file hash or raw SNP data
   * @returns Analysis response with processing status and analysis ID
   */
  processAnalysis: async (request: AnalysisRequest): Promise<AnalysisResponse> => {
    const response = await axios.post(`${API_URL}/analysis/process`, request);
    return response.data;
  },
  
  /**
   * Get the results of a previously completed analysis
   * 
   * @param analysisId - The ID of the analysis to retrieve
   * @returns Analysis results including genetic findings and recommendations
   */
  getAnalysisResults: async (analysisId: string): Promise<AnalysisResult> => {
    const response = await axios.get(`${API_URL}/analysis/${analysisId}`);
    return response.data;
  },
  
  /**
   * Check if analysis exists for a specific file hash
   * 
   * @param fileHash - The hash of the DNA file
   * @returns Boolean indicating if analysis exists
   */
  checkAnalysisExists: async (fileHash: string): Promise<boolean> => {
    try {
      const response = await axios.get(`${API_URL}/analysis/exists/${fileHash}`);
      return response.data.exists;
    } catch (error) {
      return false;
    }
  }
};

export default analysisApi;