import axios from 'axios';
import { API_URL } from '../config';

/**
 * API client for DNA-related operations
 */
export const dnaApi = {
  /**
   * Upload a DNA file for processing
   * 
   * @param file - The DNA file to upload
   * @returns Response with file information and status
   */
  uploadFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(
      `${API_URL}/dna/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  },
  
  /**
   * Validate a DNA file to check format and quality
   * 
   * @param file - The DNA file to validate
   * @returns Validation results with statistics
   */
  validateFile: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(
      `${API_URL}/dna/validate`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    return response.data;
  },
  
  /**
   * Get information about supported DNA file formats
   * 
   * @returns Information about supported formats
   */
  getSupportedFormats: async () => {
    const response = await axios.get(`${API_URL}/dna/formats`);
    return response.data;
  },
  
  /**
   * Get SNP data by file hash, if available in the system
   * 
   * @param fileHash - The hash of the previously uploaded file
   * @returns SNP data if found
   */
  getSnpDataByHash: async (fileHash: string) => {
    const response = await axios.get(`${API_URL}/dna/data/${fileHash}`);
    return response.data;
  }
};

export default dnaApi;