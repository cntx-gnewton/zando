import logging
import os
import contextlib
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from typing import AsyncGenerator

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import init_db

# Configure logging with file name, line number, and function name
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s",
)
logger = logging.getLogger(__name__)

# Define lifespan context manager (modern way to handle startup/shutdown)
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup logic
    logger.info("Starting up Zando Genomic Analysis API")
    logger.info(f"Environment: {'Development' if os.getenv('DEBUG') else 'Production'}")
    
    # Initialize database
    try:
        success = await init_db()
        if success:
            logger.info("Database initialized successfully")
        else:
            logger.warning("Database initialization returned False")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Ensure required directories exist
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)
    os.makedirs(settings.UPLOADS_DIR, exist_ok=True)
    
    # Yield control back to FastAPI
    yield
    
    # Shutdown logic (if any)
    logger.info("Shutting down Zando Genomic Analysis API")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API for genetic analysis and report generation",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files directory for reports and uploads
app.mount("/reports", StaticFiles(directory=settings.REPORTS_DIR), name="reports")

# Global exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "api_version": "1.0.0"}

# Root endpoint redirects to docs
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API. See /docs for documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)