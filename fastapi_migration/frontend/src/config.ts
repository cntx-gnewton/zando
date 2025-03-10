/**
 * Global configuration variables for the application
 */

// API base URL
export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Maximum file upload size in bytes (20MB)
export const MAX_FILE_SIZE = 20 * 1024 * 1024;

// Supported file types
export const SUPPORTED_FILE_TYPES = ['text/plain'];

// Cache expiration time in milliseconds (7 days)
export const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000;

// Feature flags
export const FEATURES = {
  USER_AUTHENTICATION: false, // Disable authentication for initial version
  REPORT_CUSTOMIZATION: true,
  DATA_EXPORT: false,
  DETAILED_ANALYSIS: true
};