/**
 * Types related to genetic reports
 */

// Report generation request
export interface ReportRequest {
  file_hash?: string;
  analysis_id?: string;
  report_type: string;
  include_raw_data?: boolean;
}

// Report generation response
export interface ReportResponse {
  report_id: string;
  status: string;
  message: string;
  processing_time?: number;
  download_url: string;
  cached: boolean;
}

// Report metadata
export interface ReportMetadata {
  report_id: string;
  created_at: string;
  report_type: string;
  file_hash?: string;
  analysis_id?: string;
  download_url: string;
}

// Report summary for listings
export interface ReportSummary {
  report_id: string;
  created_at: string;
  report_type: string;
  download_url: string;
}

// User reports listing
export interface UserReportsList {
  reports: ReportSummary[];
}

// Report type options
export enum ReportType {
  STANDARD = "standard",
  MARKDOWN = "markdown"
}

// Report state for the application
export interface ReportState {
  generating: boolean;
  reportId?: string;
  reportType: ReportType;
  downloadUrl?: string;
  error?: string;
  recentReports: ReportSummary[];
}