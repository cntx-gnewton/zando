import axios from 'axios';
import { API_URL } from '../config';
import { AnalysisRequest, AnalysisResponse, AnalysisResult } from '../types/analysis';

// Mock data for development
const MOCK_MUTATIONS = [
  {
    rsid: 'rs1805007',
    gene_name: 'MC1R',
    allele: 'T',
    effect: 'Increased sensitivity to UV radiation',
    evidence_level: 'Strong',
    category: 'Sun Sensitivity'
  },
  {
    rsid: 'rs2228570',
    gene_name: 'VDR',
    allele: 'A',
    effect: 'Reduced vitamin D receptor function',
    evidence_level: 'Moderate',
    category: 'Vitamin Metabolism'
  },
  {
    rsid: 'rs4516035',
    gene_name: 'VDR',
    allele: 'T',
    effect: 'Altered vitamin D metabolism',
    evidence_level: 'Moderate',
    category: 'Vitamin Metabolism'
  },
  {
    rsid: 'rs1800896',
    gene_name: 'IL10',
    allele: 'G',
    effect: 'Reduced inflammatory response',
    evidence_level: 'Moderate',
    category: 'Inflammation'
  },
  {
    rsid: 'rs2187668',
    gene_name: 'HLA-DQA1',
    allele: 'T',
    effect: 'Increased risk of celiac disease',
    evidence_level: 'Strong',
    category: 'Autoimmune'
  },
  {
    rsid: 'rs1544410',
    gene_name: 'VDR',
    allele: 'A',
    effect: 'Altered calcium absorption',
    evidence_level: 'Moderate',
    category: 'Vitamin Metabolism'
  }
];

const MOCK_INGREDIENTS = {
  beneficial: [
    {
      name: 'Vitamin C',
      benefit: 'Antioxidant protection',
      genes: ['MC1R'],
      evidence_level: 'Strong'
    },
    {
      name: 'Niacinamide',
      benefit: 'Reduces inflammation and redness',
      genes: ['IL10'],
      evidence_level: 'Moderate'
    },
    {
      name: 'Ceramides',
      benefit: 'Supports skin barrier function',
      genes: ['FLG'],
      evidence_level: 'Moderate'
    }
  ],
  cautionary: [
    {
      name: 'Retinol',
      caution: 'May cause increased sensitivity',
      genes: ['MC1R'],
      evidence_level: 'Moderate'
    },
    {
      name: 'Benzoyl Peroxide',
      caution: 'May cause excessive drying',
      genes: ['VDR'],
      evidence_level: 'Limited'
    }
  ]
};

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
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          resolve({
            analysis_id: `mock-analysis-${request.file_hash || Date.now()}`,
            status: 'completed',
            message: 'Analysis completed successfully',
            snp_count: 24601,
            file_hash: request.file_hash || `mock-file-hash-${Date.now()}`,
            processing_time: 2.5,
            cached: false
          });
        }, 1500);
      });
    }
    
    // Real implementation
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
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          resolve({
            analysis_id: analysisId,
            created_at: new Date().toISOString(),
            file_hash: analysisId.replace('mock-analysis-', ''),
            data: {
              mutations: MOCK_MUTATIONS,
              ingredient_recommendations: MOCK_INGREDIENTS,
              summary: "Based on your genetic profile, your skin has an increased sensitivity to UV radiation and may experience more inflammation than average. You would likely benefit from products containing vitamin C and niacinamide, while being cautious with retinol-based products."
            }
          });
        }, 1000);
      });
    }
    
    // Real implementation
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
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          // In development, pretend all uploaded files have analysis available
          resolve(true);
        }, 500);
      });
    }
    
    // Real implementation
    try {
      const response = await axios.get(`${API_URL}/analysis/exists/${fileHash}`);
      return response.data.exists;
    } catch (error) {
      return false;
    }
  }
};

export default analysisApi;