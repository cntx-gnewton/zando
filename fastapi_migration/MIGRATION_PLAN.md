# Zando Genomic Analysis: FastAPI + React Migration Plan

## 0. Migration Progress Update

### Completed Backend Components
- ✅ FastAPI project structure and core setup
- ✅ Database models and connection management with SQLAlchemy
- ✅ Robust connection handling for Google Cloud SQL
- ✅ DNA file upload, validation, and processing services
- ✅ Analysis service with full database integration
- ✅ Report generation and PDF creation services
- ✅ Comprehensive caching system for reference data and analysis results
- ✅ File storage with proper organization and hash-based addressing
- ✅ Dockerization with proper health checks and environment config

### Next Steps
- 🔄 Frontend React application development
- 🔄 API integration with frontend components
- 🔄 Authentication system implementation
- 🔄 Deploy to Google Cloud environment

## 1. Project Architecture

### Current Architecture
```
[Client Browser] → [Dash/Flask UI] → [Python Business Logic] → [PostgreSQL]
```

### Target Architecture
```
[React Frontend] → [FastAPI Backend] → [PostgreSQL]
                     ↑ Deployed on Google Cloud Functions/Run
```

## 2. Backend Migration (FastAPI)

### Implemented API Structure

The following endpoints have been implemented and are ready for frontend integration:

```
/api
  /v1
    /dna
      - POST /upload              # Upload DNA file
      - GET /uploads              # List uploaded DNA files with pagination
      - GET /formats              # Get supported DNA file formats
    
    /analysis
      - POST /process             # Process DNA file and store results
      - GET /{analysis_id}        # Get analysis results by ID
      - GET /{analysis_id}/sync   # Get analysis results by ID (sync version)
      - GET /list                 # List all analyses with pagination
      - GET /list-sync            # List all analyses (sync version)
      - GET /debug                # Get database debug information
      - GET /logs                 # Get recent application logs
    
    /reports
      - POST /generate            # Generate report from analysis
      - GET /{report_id}          # Get report metadata
      - GET /{report_id}/download # Download report as PDF
    
    /cache
      - GET /                     # Get cache overview and statistics
      - GET /files                # List all cache files with optional filtering
      - GET /file/{file_hash}     # Get detailed cache info for a file hash
      - DELETE /file/{file_hash}  # Delete cache for a specific file
      - DELETE /expired           # Remove expired cache files
      - DELETE /all               # Clean entire cache
      - GET /sync                 # Get cache stats (sync version)
    
    /admin
      - GET /cache/status         # Check all reference data cache status
      - POST /cache/refresh       # Refresh all reference data caches
      - POST /cache/refresh/snp   # Refresh only SNP cache
      - POST /cache/refresh/characteristics # Refresh characteristics cache
      - POST /cache/refresh/ingredients    # Refresh ingredients cache
      - DELETE /cache             # Clear all reference data caches
      - GET /database/stats       # Get database statistics
```

Pending implementation:

```
/api
  /v1
    /auth
      - POST /login               # User authentication
      - POST /register            # User registration
    
    /genetics
      - GET /traits               # Get genetic traits catalog
      - GET /ingredients          # Get ingredient recommendations
```

### Core Components

#### FastAPI Project Structure
```
/backend
  /app
    /api
      /v1
        /endpoints
          auth.py
          dna.py
          analysis.py
          reports.py
          genetics.py
        api.py         # API router aggregation
    /core
      config.py        # Application configuration
      security.py      # Authentication/authorization
    /db
      /models          # SQLAlchemy models
        user.py
        dna_file.py
        analysis.py
        report.py
        genetics.py
      session.py       # Database session management
    /schemas           # Pydantic models
      user.py
      dna.py
      analysis.py
      report.py
      genetics.py
    /services          # Business logic
      dna_service.py   # DNA file processing
      analysis_service.py  # Genetic analysis 
      report_service.py    # Report generation
      pdf_service.py       # PDF creation
    /utils
      caching.py       # Caching utilities
      file_ops.py      # File operations
      pdf.py           # PDF generation helpers
    main.py            # Application entry point
```

#### Implemented Services and Business Logic

1. **DNAService** (`app/services/dna_service.py`)
   - File upload and storage with hash-based addressing
   - File validation and parsing with format detection
   - SNP extraction and processing
   - Comprehensive caching system for DNA files and results
   - File hash computation and management
   - Database integration for file metadata

2. **AnalysisService** (`app/services/analysis_service.py`)
   - Reference data caching (SNPs, characteristics, ingredients)
   - Optimized batch database lookups
   - SNP matching and filtering against reference database
   - Genetic trait matching and evidence scoring
   - Ingredient recommendations (beneficial and cautionary)
   - Dynamic summary generation
   - Analysis result storage and retrieval

3. **ReportService** (`app/services/report_service.py`)
   - Report data assembly from analysis results
   - Report metadata management
   - Cache-aware report generation
   - Database integration for report storage

4. **PDFService** (`app/services/pdf_service.py`)
   - PDF report generation with ReportLab
   - Markdown-to-PDF conversion
   - Report styling and formatting
   - Multi-format report support

5. **CacheService** (`app/services/cache_service.py`)
   - Comprehensive file caching system
   - Cache statistics and monitoring
   - Expiration and cleanup management
   - Multi-format cache support (JSON, PDF, other binary)

6. **Database Models**
   - **DNAFile** (`app/db/models/dna_file.py`): Stores uploaded file metadata
   - **Analysis** (`app/db/models/analysis.py`): Stores analysis results and metadata
   - **Report** (`app/db/models/report.py`): Tracks generated reports with references to analyses
   - **User** (`app/db/models/user.py`): User account information (partially implemented)
   
7. **Data Schemas** (`app/schemas/`)
   - **Analysis**: Request/response models for analysis operations
   - **DNA**: DNA file and upload related schemas
   - **Report**: Report generation and metadata schemas
   - **User**: User account schemas (pending full implementation)

## 3. Frontend Migration (React)

### React Project Structure
```
/frontend
  /public
    index.html
    assets/
  /src
    /api
      authApi.ts       # Authentication API calls
      dnaApi.ts        # DNA file API calls
      analysisApi.ts   # Analysis API calls
      reportApi.ts     # Report API calls
      geneticsApi.ts   # Genetics data API calls
    /components
      /auth
        Login.tsx
        Register.tsx
      /dna
        FileUpload.tsx
        ValidationResults.tsx
      /analysis
        AnalysisProgress.tsx
        AnalysisResults.tsx
      /reports
        ReportViewer.tsx
        ReportDownload.tsx
      /shared
        Header.tsx
        Footer.tsx
        Navigation.tsx
        LoadingIndicator.tsx
        ErrorBoundary.tsx
    /contexts
      AuthContext.tsx  # Authentication state
      UserContext.tsx  # User data
    /hooks
      useAuth.ts       # Authentication hooks
      useAnalysis.ts   # Analysis hooks
      useReports.ts    # Report hooks
    /pages
      Home.tsx
      Dashboard.tsx
      Upload.tsx
      Analysis.tsx
      Reports.tsx
      Account.tsx
    /types
      auth.ts
      dna.ts
      analysis.ts
      report.ts
      genetics.ts
    /utils
      formatting.ts    # Data formatting utilities
      validation.ts    # Form validation
      storage.ts       # Local storage
    App.tsx
    index.tsx
    routes.tsx
  package.json
  tsconfig.json
```

### Core Components

1. **Authentication & User Management**
   - User registration and login
   - Profile management
   - Access control

2. **DNA File Handling**
   - File upload with drag-and-drop
   - Progress indicators
   - Format validation

3. **Analysis Visualization**
   - Analysis progress tracking
   - Results visualization
   - Genetic trait explanation

4. **Report Management**
   - Report generation interface
   - PDF preview capability
   - Download functionality

5. **Dashboard**
   - Summary of analyses and reports
   - Quick actions
   - Status updates

## 4. API Endpoints Detail for Frontend Integration

### DNA File Handling Endpoints

1. **`POST /api/v1/dna/upload`**
   - **Purpose**: Upload a DNA file for analysis
   - **Request**: Multipart form with file
   - **Response**: File metadata including file_hash for later reference
   - **Frontend Integration**: Use in file upload component with progress indicator
   - **Notes**: File is saved to both regular uploads directory and cache

2. **`GET /api/v1/dna/uploads`**
   - **Purpose**: Get a paginated list of uploaded DNA files
   - **Parameters**: `limit` (default 50), `offset` (default 0)
   - **Response**: List of file metadata including timestamps and sizes
   - **Frontend Integration**: Use in file browser/history component

3. **`GET /api/v1/dna/formats`**
   - **Purpose**: Get information about supported DNA file formats
   - **Response**: Detailed format specifications and examples
   - **Frontend Integration**: Use in upload help/instructions component

### Analysis Endpoints

1. **`POST /api/v1/analysis/process`**
   - **Purpose**: Process a DNA file to perform genetic analysis
   - **Request Body**:
     ```json
     {
       "file_hash": "string",  // Required if not providing raw SNP data
       "raw_snp_data": [],     // Optional array of SNP objects
       "force_refresh": false  // If true, ignores cache
     }
     ```
   - **Response**: Analysis metadata with `analysis_id` for retrieval
   - **Frontend Integration**: Trigger after successful file upload, show progress indicator

2. **`GET /api/v1/analysis/{analysis_id}`**
   - **Purpose**: Get detailed results of a completed analysis
   - **Path Parameter**: `analysis_id` from process response
   - **Response**: Complete analysis data with mutations and recommendations
   - **Frontend Integration**: Use in results visualization components

3. **`GET /api/v1/analysis/list`**
   - **Purpose**: Get paginated list of all analyses
   - **Parameters**: `limit` (default 50), `offset` (default 0)
   - **Response**: List of analysis metadata
   - **Frontend Integration**: Use in analysis history/browser component

### Report Endpoints

1. **`POST /api/v1/reports/generate`**
   - **Purpose**: Generate a PDF report from analysis results
   - **Request Body**:
     ```json
     {
       "file_hash": "string",  // Optional - source DNA file hash
       "analysis_id": "string", // Optional - specific analysis to use
       "report_type": "markdown" // Report format (markdown or standard)
     }
     ```
   - **Response**: Report metadata with download URL
   - **Frontend Integration**: Trigger from analysis results page with report options

2. **`GET /api/v1/reports/{report_id}`**
   - **Purpose**: Get metadata about a generated report
   - **Path Parameter**: `report_id` from generate response
   - **Response**: Report metadata including creation time and download link
   - **Frontend Integration**: Use to check report status

3. **`GET /api/v1/reports/{report_id}/download`**
   - **Purpose**: Download the actual PDF report
   - **Path Parameter**: `report_id` from generate response
   - **Response**: PDF file stream
   - **Frontend Integration**: Create download button that links directly to this endpoint

### Cache Management Endpoints

1. **`GET /api/v1/cache/`**
   - **Purpose**: Get overall cache statistics
   - **Response**: Cache size, file counts, formats
   - **Frontend Integration**: Admin dashboard component

2. **`DELETE /api/v1/cache/all`**
   - **Purpose**: Clear entire application cache
   - **Response**: Summary of cleared files and space freed
   - **Frontend Integration**: Admin tools/maintenance component

### Admin Endpoints

1. **`GET /api/v1/admin/cache/status`**
   - **Purpose**: Get status of reference data caches
   - **Response**: Detailed cache information with expiration status
   - **Frontend Integration**: Admin monitoring dashboard

2. **`POST /api/v1/admin/cache/refresh`**
   - **Purpose**: Force refresh of reference data caches
   - **Response**: Summary of cache refresh operation
   - **Frontend Integration**: Admin tools component

3. **`GET /api/v1/admin/database/stats`**
   - **Purpose**: Get database statistics
   - **Response**: Table sizes, row counts, total database size
   - **Frontend Integration**: Admin dashboard/monitoring component

## 5. Key User Flows

1. **DNA Upload & Analysis Flow**
   - Frontend: `FileUpload` component sends file to `/api/v1/dna/upload`
   - Backend: `DNAService` validates, stores, and creates hash for the file
   - Frontend: Request analysis via `/api/v1/analysis/process` with file_hash
   - Backend: `AnalysisService` extracts SNPs, queries database, builds analysis
   - Frontend: Poll or await completion, then retrieve results with `/api/v1/analysis/{analysis_id}`
   - Frontend: Display results using `AnalysisResults` component with mutations and recommendations

2. **Report Generation Flow**
   - Frontend: User selects analysis and requests report
   - Frontend: `ReportGenerator` component calls `/api/v1/reports/generate` with analysis_id
   - Backend: `ReportService` assembles report data, `PDFService` creates PDF document
   - Frontend: Redirect to or open `/api/v1/reports/{report_id}/download` for PDF download
   - Frontend: Update report history in user dashboard

3. **Admin Dashboard Flow**
   - Frontend: Admin views cache status via `/api/v1/admin/cache/status`
   - Frontend: Admin can refresh reference data via `/api/v1/admin/cache/refresh`
   - Frontend: System statistics available via `/api/v1/admin/database/stats`
   - Frontend: Cache cleanup available via `/api/v1/cache/expired` or `/api/v1/cache/all`

## 6. Frontend Development Plan

### Phase 1: Frontend Foundation (Week 1)
- ✅ Set up React project with TypeScript
- ✅ Configure build system and development environment
- ✅ Implement basic routing with React Router
- ✅ Create API service layer for backend communication
- ✅ Develop responsive layout with common components

### Phase 2: Core Features (Week 2)
- 🔄 Implement DNA file upload functionality
  - Drag-and-drop interface
  - Progress indicators
  - File validation
  - Success/error handling
- 🔄 Create file browser component for uploaded files
  - Pagination support
  - Sorting and filtering
  - File details view

### Phase 3: Analysis Features (Week 3)
- 🔄 Build analysis request and progress tracking
  - Analysis submission form
  - Progress indicator and status tracking 
  - Error handling and recovery options
- 🔄 Develop analysis results visualization
  - SNP mutations display
  - Genetic trait visualization
  - Ingredient recommendations with filtering

### Phase 4: Report Generation (Week 4)
- 🔄 Implement report generation interface
  - Report options selection
  - Generation progress tracking
- 🔄 Create report viewer and download components
  - Report preview
  - PDF download functionality
  - Report history and management

### Phase 5: Admin Features & Refinement (Week 5)
- 🔄 Develop admin dashboard
  - Cache management interface
  - Database statistics visualization
  - System health monitoring
- 🔄 Final UI polish and optimization
  - Performance optimization
  - Responsive design refinement
  - Accessibility improvements

## 7. Frontend-Backend Integration

### API Service Layer
The React frontend will communicate with the backend through a dedicated API service layer. Here's the recommended structure:

```typescript
// api/apiClient.ts
import axios from 'axios';

// Create an Axios instance with common configuration
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for handling auth tokens
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for handling errors
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Handle authentication errors
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Service Modules

Recommended API service modules that align with the backend endpoints:

```typescript
// api/dnaService.ts
import apiClient from './apiClient';

export const uploadDNAFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiClient.post('/dna/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: progressEvent => {
      // Calculate and report progress
      const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      // Call progress callback or update state
    }
  });
};

export const getUploadedFiles = async (limit = 50, offset = 0) => {
  return apiClient.get(`/dna/uploads?limit=${limit}&offset=${offset}`);
};

export const getSupportedFormats = async () => {
  return apiClient.get('/dna/formats');
};
```

```typescript
// api/analysisService.ts
import apiClient from './apiClient';

export const processAnalysis = async (fileHash, forceRefresh = false) => {
  return apiClient.post('/analysis/process', {
    file_hash: fileHash,
    force_refresh: forceRefresh
  });
};

export const getAnalysisById = async (analysisId) => {
  return apiClient.get(`/analysis/${analysisId}`);
};

export const listAnalyses = async (limit = 50, offset = 0) => {
  return apiClient.get(`/analysis/list?limit=${limit}&offset=${offset}`);
};
```

```typescript
// api/reportService.ts
import apiClient from './apiClient';

export const generateReport = async (analysisId, reportType = 'markdown') => {
  return apiClient.post('/reports/generate', {
    analysis_id: analysisId,
    report_type: reportType
  });
};

export const getReportMetadata = async (reportId) => {
  return apiClient.get(`/reports/${reportId}`);
};

export const getReportDownloadUrl = (reportId) => {
  return `${apiClient.defaults.baseURL}/reports/${reportId}/download`;
};
```

### React Hooks for API Integration

Create custom hooks to easily use these services in React components:

```typescript
// hooks/useDNA.ts
import { useState } from 'react';
import * as dnaService from '../api/dnaService';

export const useFileUpload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  const uploadFile = async (file) => {
    setIsUploading(true);
    setProgress(0);
    setError(null);
    
    try {
      const result = await dnaService.uploadDNAFile(file, setProgress);
      setUploadResult(result.data);
      return result.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
      throw err;
    } finally {
      setIsUploading(false);
    }
  };

  return { uploadFile, isUploading, progress, error, uploadResult };
};

export const useUploadedFiles = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({ limit: 50, offset: 0, count: 0 });

  const fetchFiles = async (limit = 50, offset = 0) => {
    setLoading(true);
    try {
      const response = await dnaService.getUploadedFiles(limit, offset);
      setFiles(response.data.files);
      setPagination({ 
        limit, 
        offset, 
        count: response.data.count 
      });
      return response.data;
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch files');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { files, loading, error, pagination, fetchFiles };
};
```

## 8. Key Technical Considerations

### Authentication & Security
- JWT-based authentication (pending implementation)
- HTTPS for all communications
- Input validation with Pydantic schemas
- File hash verification for uploads

### Performance Optimization
- Efficient database queries with proper indexing
- Comprehensive caching strategy for:
  - Reference data (SNPs, characteristics, ingredients)
  - DNA file processing results
  - Analysis results
  - Generated reports
- Parallel data loading in React components
- Pagination for large data sets
- Lazy loading of frontend components

### Scalability
- Stateless API design for horizontal scaling
- Database connection pooling with configurable parameters
- Content-addressable file storage with double caching
- Clear separation of compute-intensive operations

### Monitoring & Management
- Admin endpoints for system monitoring
- Cache management interface
- Database statistics tracking
- Reference data refresh controls

## 9. Frontend Development Guidelines

1. **State Management**
   - Use React Context for global state (authentication, user preferences)
   - Use local component state for UI-specific state
   - Consider React Query for server state management and caching

2. **Component Structure**
   - Create reusable, atomic components in `/components`
   - Compose page components from smaller components
   - Use TypeScript interfaces for prop type definitions

3. **API Integration**
   - Use the services defined in the API layer
   - Wrap API calls in try/catch blocks with proper error handling
   - Implement loading states and error handling UI
   - Use React Query for data fetching, caching, and synchronization

4. **Styling**
   - Use CSS modules or styled-components for component styling
   - Implement a responsive design that works on all devices
   - Follow accessibility guidelines (WCAG 2.1)

5. **Testing**
   - Write unit tests for key components and utilities
   - Add integration tests for critical user flows
   - Test error handling and edge cases