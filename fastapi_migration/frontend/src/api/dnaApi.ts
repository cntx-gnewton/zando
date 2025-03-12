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
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          resolve({
            file_hash: 'mock-file-hash-' + Date.now(),
            file_name: file.name,
            file_size: file.size,
            upload_date: new Date().toISOString(),
            status: 'uploaded',
            snp_count: Math.floor(Math.random() * 100000) + 500000, // Random count for mock
            format: file.name.toLowerCase().includes('ancestry') ? 'ancestry' : '23andme',
            cached: false
          });
        }, 2000);
      });
    }
    
    // Real implementation
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
   * Get a list of uploaded DNA files
   * 
   * @param limit - Maximum number of files to return
   * @param offset - Number of files to skip for pagination
   * @returns List of DNA files with pagination metadata
   */
  getUploadedFiles: async (limit = 50, offset = 0): Promise<{ files: DNAFileUploadResponse[], total: number }> => {
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          const mockFiles: DNAFileUploadResponse[] = [
            {
              file_hash: 'mock-file-hash-1',
              file_name: '23andMe_raw_data.txt',
              file_size: 4500000,
              upload_date: new Date().toISOString(),
              status: 'processed',
              snp_count: 640000,
              format: '23andme',
              cached: true
            },
            {
              file_hash: 'mock-file-hash-2',
              file_name: 'ancestry_dna_export.txt',
              file_size: 5200000,
              upload_date: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
              status: 'processed',
              snp_count: 710000,
              format: 'ancestry',
              cached: true
            },
            {
              file_hash: 'mock-file-hash-3',
              file_name: 'myheritage_dna_data.txt',
              file_size: 4800000,
              upload_date: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
              status: 'processed',
              snp_count: 680000,
              format: 'myheritage',
              cached: true
            }
          ];
          
          resolve({
            files: mockFiles.slice(offset, offset + limit),
            total: mockFiles.length
          });
        }, 1000);
      });
    }
    
    // Real implementation
    const response = await axios.get(`${API_URL}/dna/uploads`, {
      params: {
        limit,
        offset
      }
    });
    
    return response.data;
  },
  
  /**
   * Validate a DNA file to check format and quality
   * 
   * @param file - The DNA file to validate
   * @returns Validation results with statistics
   */
  validateFile: async (file: File) => {
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          resolve({
            valid: true,
            format: file.name.toLowerCase().includes('ancestry') ? 'ancestry' : '23andme',
            stats: {
              line_count: Math.floor(Math.random() * 100000) + 500000,
              valid_snps: Math.floor(Math.random() * 100000) + 500000,
              invalid_lines: Math.floor(Math.random() * 1000),
              chromosomes: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X', 'Y', 'MT']
            }
          });
        }, 1500);
      });
    }
    
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
    
    return response.data;
  },
  
  /**
   * Get information about supported DNA file formats
   * 
   * @returns Information about supported formats
   */
  getSupportedFormats: async () => {
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          resolve({
            formats: ['23andme', 'ancestry', 'myheritage'],
            details: {
              '23andme': {
                name: '23andMe',
                description: 'Raw data export from 23andMe',
                file_pattern: '*.txt',
                example_line: 'rs548049170 1 69869 TT',
                support_level: 'full'
              },
              'ancestry': {
                name: 'AncestryDNA',
                description: 'Raw data export from Ancestry DNA',
                file_pattern: '*.txt',
                example_line: 'rs548049170,1,69869,T,T',
                support_level: 'full'
              },
              'myheritage': {
                name: 'MyHeritage',
                description: 'Raw data export from MyHeritage DNA',
                file_pattern: '*.csv',
                example_line: 'rs548049170,1,69869,T,T',
                support_level: 'partial'
              }
            }
          });
        }, 1000);
      });
    }
    
    // Real implementation
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
    // For development purposes, use a mock implementation
    if (process.env.NODE_ENV === 'development' && !process.env.REACT_APP_USE_REAL_API) {
      return new Promise(resolve => {
        // Simulate network latency
        setTimeout(() => {
          resolve({
            file_hash: fileHash,
            snp_count: 640000,
            chromosomes: {
              '1': 51234,
              '2': 48765,
              '3': 42198,
              // ... other chromosomes
            },
            sample: [
              { rsid: 'rs548049170', chromosome: '1', position: 69869, genotype: 'TT' },
              { rsid: 'rs13302982', chromosome: '1', position: 877831, genotype: 'GG' },
              { rsid: 'rs1234567', chromosome: '2', position: 1234567, genotype: 'AC' }
            ]
          });
        }, 1500);
      });
    }
    
    // Real implementation
    const response = await axios.get(`${API_URL}/dna/data/${fileHash}`);
    return response.data;
  }
};

export default dnaApi;