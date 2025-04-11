# CLAUDE.md - Guide for Zando Genomic Analysis Project

This document serves as a comprehensive guide to the Zando Genomic Analysis project, including both the original implementation and the new FastAPI+React architecture.

## Current Project Architecture

Zando has been migrated from a monolithic Flask/Dash application to a modern microservices architecture with a FastAPI backend and React frontend.

### Architecture Overview

**Original Architecture:**
```
[Client Browser] → [Dash/Flask UI] → [Python Business Logic] → [PostgreSQL]
```

**Current Architecture:**
```
[React Frontend] → [FastAPI Backend] → [PostgreSQL]
                    ↑ Deployed on Google Cloud Run
```

## Backend (FastAPI)

### Core Components

1. **DNA Processing Service**
   - File validation and parsing
   - SNP extraction and normalization
   - Format detection for 23andMe/Ancestry data
   - Content-based file hashing for caching
   - Optimized for large genomic files

2. **Analysis Service**
   - Batch database operations for efficient SNP lookup
   - Genetic trait matching with weighted evidence scoring
   - Characteristic analysis for skin conditions
   - Comprehensive ingredient recommendations
   - Reference data caching for performance

3. **Report Generation**
   - Markdown-based PDF generation with ReportLab
   - Dynamic summary creation based on genetic findings
   - Ingredient recommendations with scientific evidence
   - Organized sections for traits, characteristics, and recommendations
   - Content-addressable caching system

4. **API Endpoints**

The backend exposes RESTful endpoints for all functionality:

```
/api/v1
  /auth
    - POST /login               # User authentication
    - POST /register            # User registration
    - GET /me                   # Get user profile
  /dna
    - POST /upload              # Upload DNA file
    - GET /uploads              # List uploads with pagination
    - GET /formats              # Get supported formats
  /analysis
    - POST /process             # Process DNA and get results
    - GET /{analysis_id}        # Get analysis results
    - GET /list                 # List analyses with pagination
  /reports
    - POST /generate            # Generate PDF report
    - GET /{report_id}          # Get report metadata
    - GET /{report_id}/download # Download report PDF
  /cache
    - Various endpoints for cache management
  /admin
    - Various endpoints for system administration
```

### Database Schema

- **snp**: Genetic variants with rsID, gene, allele, effect details
- **skincharacteristic**: Skin traits affected by genetic variations
- **ingredientcaution/ingredient**: Beneficial and cautionary ingredients
- **Association tables**: Link SNPs to characteristics and ingredients
- **Efficient indexes**: Optimized for rapid genetic lookups

### Performance Optimizations

- **Connection Pooling**: Persistent database connections
- **Batch Operations**: Combined queries for SNP data and characteristics
- **Data Caching**: Multiple caching layers for each processing stage
- **Content-addressable Storage**: Hash-based file management
- **Asynchronous Processing**: Non-blocking database operations

## Frontend (React)

### Core Components

1. **File Upload System**
   - Drag-and-drop interface with progress indication
   - File validation and format checking
   - Error handling with user feedback
   - Integration with backend upload API

2. **Analysis Visualization**
   - Interactive display of genetic findings
   - Organized presentation of SNP impacts
   - Clear visualization of characteristic effects
   - Mobile-responsive design

3. **Ingredient Recommendations**
   - Tabbed display of beneficial and cautionary ingredients
   - Gene-based grouping of recommendations
   - Evidence-weighted presentation
   - Clear scientific explanations

4. **Report Management**
   - One-click report generation
   - PDF download functionality
   - Report history and management
   - Shareable report links

### Frontend Structure

```
/frontend
  /src
    /api         # API service clients
    /components  # React components
    /contexts    # State management
    /hooks       # Custom React hooks
    /pages       # Page components
    /types       # TypeScript definitions
    /utils       # Utility functions
```

### Authentication

The system includes JWT-based authentication with the following features:
- Secure password hashing with bcrypt
- Token-based authentication
- Protected routes
- User profile management
- Frontend context for auth state

## Development Environment

### Backend Setup

```bash
# Set up backend
cd fastapi_migration/backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run backend server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# Set up frontend
cd fastapi_migration/frontend
npm install

# Run development server
npm start
```

### Environment Variables

Backend (.env):
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=zando
SECRET_KEY=yoursecretkey
```

Frontend (.env):
```
REACT_APP_API_URL=http://localhost:8000/api/v1
```

## Deployment

The application is designed for deployment on Google Cloud:

- **Backend**: Google Cloud Run
- **Frontend**: Google Cloud Storage with Cloud CDN
- **Database**: Google Cloud SQL (PostgreSQL)
- **File Storage**: Google Cloud Storage

## Code Style Guidelines

- **Backend**:
  - Use snake_case for Python (variables, functions, files)
  - Add type hints to function signatures
  - Document with docstrings
  - Follow PEP 8 standards

- **Frontend**:
  - Use camelCase for JavaScript/TypeScript
  - Component-focused architecture
  - Strong TypeScript typing
  - Consistent Tailwind CSS styling

## Legacy System Reference

For reference to the original system:

- **Main Files**:
  - `ALGORYTHM/src/app.py`: Original Dash application
  - `ALGORYTHM/src/process_dna.py`: Core DNA processing
  - `ALGORYTHM/database/`: Database schema and initialization

- **Run Commands** (Legacy):
  - Install: `pip install -r ALGORYTHM/requirements.txt`
  - Run web app: `python ALGORYTHM/src/app.py`
  - Process file: `python ALGORYTHM/src/process_dna.py <input> <output>`