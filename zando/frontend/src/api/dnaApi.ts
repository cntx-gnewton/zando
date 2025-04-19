import axios from 'axios';
import { API_URL } from '../config';
import { DNAFileUploadResponse } from '../types/dna';

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
  uploadFile: async (file: File): Promise<DNAFileUploadResponse> => {
    // Create form data for the upload
    const formData = new FormData();
    formData.append('file', file);
    
    // Log the API URL to help debug
    console.log('Uploading file to:', `${API_URL}/dna/upload`);
    
    // Real implementation
    const response = await axios.post(
      `${API_URL}/dna/upload`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    
    // Log the response for debugging
    console.log('Upload API response:', response.data);
    
    return response.data;
  },
  
  /**
   * Get a list of uploaded DNA files
   * 
   * @param limit - Maximum number of files to return
   * @param offset - Number of files to skip for pagination
   * @returns List of DNA files with pagination metadata
   */
  getUploadedFiles: async (limit = 50, offset = 0): Promise<{ files: DNAFileUploadResponse[], total: number }> => {
    // Log for debugging
    console.log('Getting uploaded files from:', `${API_URL}/dna/uploads`);
    
    // Real implementation
    const response = await axios.get(`${API_URL}/dna/uploads`, {
      params: {
        limit,
        offset
      }
    });
    
    console.log('Files API response:', response.data);
    return response.data;
  },
  
  /**
   * Validate a DNA file to check format and quality
   * 
   * @param file - The DNA file to validate
   * @returns Validation results with statistics
   */
  validateFile: async (file: File) => {
    console.log('Validating file at:', `${API_URL}/dna/validate`);
    
    // Real implementation
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
    
    console.log('Validation API response:', response.data);
    return response.data;
  },
  
  /**
   * Get information about supported DNA file formats
   * 
   * @returns Information about supported formats
   */
  getSupportedFormats: async () => {
    console.log('Getting supported formats from:', `${API_URL}/dna/formats`);
    
    // Real implementation
    const response = await axios.get(`${API_URL}/dna/formats`);
    console.log('Formats API response:', response.data);
    return response.data;
  },
  
  /**
   * Get SNP data by file hash, if available in the system
   * 
   * @param fileHash - The hash of the previously uploaded file
   * @returns SNP data if found
   */
  getSnpDataByHash: async (fileHash: string) => {
    console.log('Getting SNP data from:', `${API_URL}/dna/data/${fileHash}`);
    
    // Real implementation
    const response = await axios.get(`${API_URL}/dna/data/${fileHash}`);
    console.log('SNP data API response:', response.data);
    return response.data;
  }
};

export default dnaApi;