# Zando Genomic Analysis: FastAPI + React Migration Plan

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

### API Structure

```
/api
  /v1
    /auth
      - POST /login               # User authentication
      - POST /register            # User registration
    /dna
      - POST /upload              # Upload DNA file
      - POST /validate            # Validate DNA file 
      - GET /formats              # Get supported DNA file formats
    /analysis
      - POST /process             # Process DNA and store results
      - GET /{analysis_id}        # Get analysis results by ID
    /reports
      - POST /generate            # Generate report from analysis
      - GET /{report_id}          # Get report metadata
      - GET /{report_id}/download # Download report as PDF
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

#### Extracted Business Logic

1. **DNAService**
   - File validation and parsing
   - SNP extraction
   - File format detection
   - Cached file processing

2. **AnalysisService**
   - SNP batch database lookup
   - Genetic trait matching
   - Characteristic analysis
   - Ingredient recommendations

3. **ReportService**
   - Report data assembly
   - Summary generation
   - Personalization

4. **PDFService**
   - PDF document generation
   - Styling and formatting
   - Image embedding

5. **Database Models**
   - User: Authentication and user data
   - DNAFile: Uploaded file metadata and status
   - Analysis: Processed genetic analysis results
   - Report: Generated report metadata
   - Genetics: SNPs, characteristics, and ingredients

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

## 4. Data Flow Mapping

### Key User Flows

1. **DNA Upload & Analysis**
   - Frontend: `FileUpload` component sends file to `/api/v1/dna/upload`
   - Backend: `DNAService` validates and processes file
   - Backend: `AnalysisService` extracts SNPs and matches with database
   - Frontend: `AnalysisResults` displays processed data

2. **Report Generation**
   - Frontend: `ReportViewer` requests report from `/api/v1/reports/generate`
   - Backend: `ReportService` assembles report data
   - Backend: `PDFService` creates PDF document
   - Frontend: `ReportDownload` provides download link

3. **Recommendations View**
   - Frontend: Dashboard displays personalized recommendations
   - Backend: Recommendations pulled from analysis results

## 5. Development Phases

### Phase 1: Backend Core (Weeks 1-2)
- Set up FastAPI project structure
- Implement database models and connections
- Extract and refactor core DNA processing logic
- Create basic endpoints for DNA upload and validation

### Phase 2: Backend Services (Weeks 3-4)
- Implement analysis service with database integration
- Create report generation service
- Develop PDF creation service
- Add authentication and user management

### Phase 3: Frontend Foundation (Weeks 5-6)
- Set up React project with TypeScript
- Create API integration layer
- Implement authentication flows
- Build basic navigation and layout

### Phase 4: Frontend Features (Weeks 7-8)
- Build file upload and validation UI
- Create analysis visualization components
- Implement report viewer and download
- Develop dashboard and user profile

### Phase 5: Integration & Testing (Weeks 9-10)
- End-to-end testing of key workflows
- Performance optimization
- Security auditing
- Bug fixing and refinement

## 6. Deployment Strategy

### Backend Deployment
- Google Cloud Run for API services
- Google Cloud SQL for PostgreSQL database
- Cloud Storage for file storage and caching

### Frontend Deployment
- Google Cloud Storage for static hosting
- Cloud CDN for content delivery
- Firebase hosting as an alternative

### DevOps
- CI/CD pipeline with GitHub Actions
- Automated testing before deployment
- Staging and production environments
- Monitoring with Google Cloud Operations

## 7. Key Technical Considerations

### Authentication & Security
- JWT-based authentication
- HTTPS for all communications
- API rate limiting
- Input validation and sanitization

### Performance Optimization
- Efficient database queries with proper indexing
- Caching strategy for DNA analysis results
- Background task processing for long-running operations
- Lazy loading of frontend components

### Scalability
- Stateless API design for horizontal scaling
- Database connection pooling
- Efficient file storage with content-addressable caching
- Proper separation of compute-intensive operations

## 8. Migration Execution Plan

1. **Setup Development Environment**
   - Create new repository structure with frontend and backend folders
   - Set up local development environment with Docker

2. **Extract Core Business Logic**
   - Extract DNA processing from current codebase
   - Refactor database access patterns
   - Create Pydantic models for data validation

3. **Develop FastAPI Endpoints**
   - Implement API routes following RESTful principles
   - Add documentation with Swagger/OpenAPI
   - Set up authentication middleware

4. **Create React Frontend**
   - Set up React application with TypeScript
   - Create API service layer
   - Implement core UI components

5. **Integration & Testing**
   - Connect frontend and backend
   - Test critical user flows
   - Optimize performance bottlenecks

6. **Deploy & Monitor**
   - Set up cloud infrastructure
   - Configure CI/CD pipeline
   - Implement monitoring and alerting