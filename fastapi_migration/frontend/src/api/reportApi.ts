import axios from 'axios';
import { API_URL } from '../config';
import { ReportRequest, ReportResponse, ReportMetadata } from '../types/report';

// Mock data should be controlled by the UI debug mode toggle
// Default to false - real API calls will be used unless UI debug mode is enabled
const USE_MOCK_REPORT = false;

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
  generateReport: async (request: ReportRequest, debugMode: boolean = false): Promise<ReportResponse> => {
    // Log request for debugging
    console.log('Report generation request:', request);
    
    // Use mock data for debugging if enabled via debugMode or global setting
    if (debugMode || USE_MOCK_REPORT) {
      console.log('Using mock report data');
      return new Promise(resolve => {
        // Simulate network delay
        setTimeout(() => {
          const mockReportId = `mock-report-${Date.now()}`;
          resolve({
            report_id: mockReportId,
            status: 'completed',
            message: 'Report generated successfully (MOCK)',
            download_url: `/mock-reports/${mockReportId}.pdf`,
            cached: false
          });
        }, 1500);
      });
    }
    
    // Real API call with more detailed error handling
    try {
      console.log('Calling report API at:', `${API_URL}/reports/generate`);
      const response = await axios.post(`${API_URL}/reports/generate`, request);
      console.log('Report API response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      if (axios.isAxiosError(error)) {
        console.error('API Error Response:', error.response?.data);
        console.error('API Error Status:', error.response?.status);
        console.error('Request data:', request);
      }
      throw error;
    }
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
  downloadReport: (reportId: string, debugMode: boolean = false): void => {
    // Check if we're using mock mode and if the reportId begins with "mock-"
    if (debugMode || USE_MOCK_REPORT || reportId.startsWith('mock-')) {
      console.log('Using mock download for report:', reportId);
      
      // Create a sample PDF with HTML content
      const htmlContent = `
        <html>
          <head>
            <title>Mock Genetic Report</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 40px; }
              h1 { color: #2563eb; }
              h2 { color: #1e40af; margin-top: 30px; }
              .section { margin: 20px 0; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }
              .gene { background: #f3f4f6; padding: 10px; margin: 10px 0; border-radius: 4px; }
              .effect-high { color: #b91c1c; }
              .effect-medium { color: #b45309; }
              .effect-low { color: #047857; }
              .recommendation { background: #ecfdf5; padding: 15px; margin: 15px 0; border-radius: 4px; }
            </style>
          </head>
          <body>
            <h1>Zando Genetic Analysis Report</h1>
            <p>This is a mock report for demonstration purposes.</p>
            <p>Report ID: ${reportId}</p>
            <p>Generated on: ${new Date().toLocaleString()}</p>
            
            <div class="section">
              <h2>Genetic Profile Summary</h2>
              <p>Based on your genetic profile, your skin has an increased sensitivity to UV radiation and may experience more inflammation than average. You would likely benefit from products containing vitamin C and niacinamide, while being cautious with retinol-based products.</p>
            </div>
            
            <div class="section">
              <h2>Key Genetic Findings</h2>
              <div class="gene">
                <h3>MC1R Gene (rs1805007)</h3>
                <p>Variant: T allele</p>
                <p class="effect-high">Effect: Increased sensitivity to UV radiation</p>
                <p>Evidence: Strong</p>
              </div>
              
              <div class="gene">
                <h3>VDR Gene (rs2228570)</h3>
                <p>Variant: A allele</p>
                <p class="effect-medium">Effect: Reduced vitamin D receptor function</p>
                <p>Evidence: Moderate</p>
              </div>
              
              <div class="gene">
                <h3>IL10 Gene (rs1800896)</h3>
                <p>Variant: G allele</p>
                <p class="effect-medium">Effect: Reduced inflammatory response</p>
                <p>Evidence: Moderate</p>
              </div>
            </div>
            
            <div class="section">
              <h2>Personalized Recommendations</h2>
              <div class="recommendation">
                <h3>Beneficial Ingredients</h3>
                <ul>
                  <li><strong>Vitamin C</strong> - Antioxidant protection, helps prevent UV damage</li>
                  <li><strong>Niacinamide</strong> - Reduces inflammation and redness</li>
                  <li><strong>Ceramides</strong> - Supports skin barrier function</li>
                </ul>
              </div>
              
              <div class="recommendation">
                <h3>Ingredients to Use with Caution</h3>
                <ul>
                  <li><strong>Retinol</strong> - May cause increased sensitivity with your MC1R variant</li>
                  <li><strong>Benzoyl Peroxide</strong> - May cause excessive drying with your VDR variant</li>
                </ul>
              </div>
            </div>
            
            <footer style="margin-top: 50px; font-size: 12px; color: gray; text-align: center;">
              <p>This is a mock report generated for demonstration purposes only.</p>
              <p>Zando Genomics &copy; ${new Date().getFullYear()}</p>
            </footer>
          </body>
        </html>
      `;
      
      // Create a Blob with the HTML content
      const blob = new Blob([htmlContent], { type: 'text/html' });
      const url = URL.createObjectURL(blob);
      
      // Open the blob URL in a new tab
      window.open(url, '_blank');
    } else {
      // Real implementation
      window.open(`${API_URL}/reports/${reportId}/download`, '_blank');
    }
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