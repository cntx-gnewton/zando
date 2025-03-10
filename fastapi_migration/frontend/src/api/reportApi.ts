import axios from 'axios';
import { API_URL } from '../config';
import { ReportRequest, ReportResponse, ReportMetadata } from '../types/report';

/**
 * API client for report generation and management
 */
export const reportApi = {
  /**
   * Generate a report from DNA analysis
   * 
   * @param request - Report request with analysis ID or file hash
   * @returns Report response with status and download link
   */
  generateReport: async (request: ReportRequest): Promise<ReportResponse> => {
    const response = await axios.post(`${API_URL}/reports/generate`, request);
    return response.data;
  },
  
  /**
   * Get metadata about a previously generated report
   * 
   * @param reportId - The ID of the report
   * @returns Report metadata including creation time and type
   */
  getReportMetadata: async (reportId: string): Promise<ReportMetadata> => {
    const response = await axios.get(`${API_URL}/reports/${reportId}`);
    return response.data;
  },
  
  /**
   * Get the download URL for a report
   * 
   * @param reportId - The ID of the report
   * @returns URL to download the report
   */
  getReportDownloadUrl: (reportId: string): string => {
    return `${API_URL}/reports/${reportId}/download`;
  },
  
  /**
   * Download a report directly in the browser
   * 
   * @param reportId - The ID of the report
   */
  downloadReport: (reportId: string): void => {
    window.open(`${API_URL}/reports/${reportId}/download`, '_blank');
  },
  
  /**
   * Get a list of reports for the current user
   * 
   * @returns List of report metadata
   */
  getUserReports: async (): Promise<ReportMetadata[]> => {
    const response = await axios.get(`${API_URL}/reports/user`);
    return response.data;
  }
};

export default reportApi;