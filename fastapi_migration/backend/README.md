# Zando Genomic Analysis - FastAPI Backend

This is the FastAPI backend for the Zando Genomic Analysis platform, providing a modern API for DNA processing, genetic analysis, and report generation.

## Features

- DNA file upload and validation
- Genetic analysis with trait identification
- PDF report generation
- Caching system for improved performance
- User authentication and data management

## Technical Overview

- Built with FastAPI and Python 3.9+
- SQLAlchemy ORM for database operations
- PostgreSQL database for data storage
- Modern async/await patterns for better performance
- Comprehensive type hints and validation with Pydantic

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Docker (optional)

### Installation

1. Clone the repository
2. Set up a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/zando
   SECRET_KEY=your_secret_key
   CACHE_DIR=./cache
   REPORTS_DIR=./reports
   ```
4. Run database migrations:
   ```
   alembic upgrade head
   ```
5. Start the development server:
   ```
   uvicorn app.main:app --reload
   ```

## Project Structure

The project follows a modular organization:

```
/app
  /api
    /v1
      /endpoints        # API route handlers
      api.py            # API router aggregation
  /core
    config.py           # Application configuration
    security.py         # Authentication utilities
    dependencies.py     # FastAPI dependencies
  /db
    /models             # SQLAlchemy models
    session.py          # Database session management
  /schemas              # Pydantic models
  /services             # Business logic
  /utils                # Utility functions
  main.py               # Application entry point
```

## API Documentation

The API is documented using OpenAPI and can be accessed at `/docs` when the server is running. Key endpoints include:

### DNA Endpoints

- `POST /api/v1/dna/upload` - Upload DNA file
- `POST /api/v1/dna/validate` - Validate DNA file
- `GET /api/v1/dna/formats` - Get supported DNA formats

### Analysis Endpoints

- `POST /api/v1/analysis/process` - Process DNA for analysis
- `GET /api/v1/analysis/{analysis_id}` - Get analysis results

### Report Endpoints

- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/{report_id}` - Get report metadata
- `GET /api/v1/reports/{report_id}/download` - Download report PDF

## Database Schema

The application uses the following core database models:

- `User` - User authentication and information
- `DNAFile` - Uploaded DNA file metadata
- `Analysis` - Genetic analysis results
- `Report` - Generated report metadata
- `SNP`/`SkinCharacteristic`/`Ingredient` - Genetic reference data

## Services

The application is organized around these key services:

### DNAService

Handles DNA file operations, including:
- Validating DNA file formats
- Parsing raw DNA data
- Extracting SNP information
- Caching processed data

### AnalysisService

Performs genetic analysis, including:
- Matching user SNPs with reference database
- Identifying genetic traits and characteristics
- Generating ingredient recommendations
- Creating summary descriptions

### ReportService

Manages report generation, including:
- Creating PDF reports with personalized information
- Formatting reports with different styles
- Caching generated reports
- Tracking report history

## Deployment

### Docker

Build and run with Docker:

```bash
docker build -t zando-backend .
docker run -p 8000:8000 --env-file .env zando-backend
```

### Google Cloud

For deployment to Google Cloud Run:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/zando-backend
gcloud run deploy --image gcr.io/PROJECT_ID/zando-backend --platform managed
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Run linting
flake8 app

# Run type checking
mypy app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests where appropriate
5. Submit a pull request

## License

This project is licensed under the MIT License.