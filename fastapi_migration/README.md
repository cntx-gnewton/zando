# Zando Genomic Analysis - FastAPI/React Migration

This project is a migration of the Zando Genomic Analysis platform from a Dash/Flask application to a modern architecture using FastAPI for the backend and React for the frontend.

## Project Structure

```
/fastapi_migration
  /backend                # FastAPI backend application
    /app
      /api                # API endpoints
      /core               # Core functionality
      /db                 # Database models and session management
      /schemas            # Pydantic models
      /services           # Business logic
      /utils              # Utility functions
    requirements.txt      # Python dependencies
    Dockerfile            # Backend Docker configuration
  
  /frontend               # React frontend application
    /public               # Static assets
    /src
      /api                # API client code
      /components         # React components
      /contexts           # React context providers
      /hooks              # Custom React hooks
      /pages              # Page components
      /types              # TypeScript type definitions
      /utils              # Utility functions
    package.json          # JavaScript dependencies
    Dockerfile            # Frontend Docker configuration
  
  /docs                   # Documentation
  docker-compose.yml      # Docker Compose configuration
  MIGRATION_PLAN.md       # Detailed migration plan
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 13+
- Docker and Docker Compose (optional)

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and install dependencies:
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

4. Run the FastAPI server:
   ```
   uvicorn app.main:app --reload
   ```

The API will be available at http://localhost:8000 with interactive documentation at http://localhost:8000/docs.

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file with the following variables:
   ```
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

4. Start the development server:
   ```
   npm start
   ```

The frontend will be available at http://localhost:3000.

## Docker Setup

To run the entire application using Docker:

1. Make sure Docker and Docker Compose are installed
2. Run the following command from the root directory:
   ```
   docker-compose up -d
   ```

This will start both the backend and frontend services, with the frontend available at http://localhost:3000 and the backend at http://localhost:8000.

## Documentation

For detailed information about the migration plan and architecture, see [MIGRATION_PLAN.md](MIGRATION_PLAN.md).

## License

This project is licensed under the MIT License.