/**
 * Global configuration variables for the application
 */

// API base URL
export const API_URL = process.env.REACT_APP_API_URL || 'https://zando-272043323727.us-central1.run.app';

// Flag to control mock data usage (default to false to use the real API)
export const USE_MOCK_DATA = process.env.REACT_APP_USE_MOCK_DATA === 'true';

// Maximum file upload size in bytes (20MB)
export const MAX_FILE_SIZE = 20 * 1024 * 1024;

// Supported file types
export const SUPPORTED_FILE_TYPES = ['text/plain'];

// Cache expiration time in milliseconds (7 days)
export const CACHE_EXPIRATION = 7 * 24 * 60 * 60 * 1000;

// Feature flags
export const FEATURES = {
  USER_AUTHENTICATION: true, // Enabled with Google Authentication
  REPORT_CUSTOMIZATION: true,
  DATA_EXPORT: false,
  DETAILED_ANALYSIS: true
};