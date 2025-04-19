from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
import time
import hashlib
import os
from tempfile import NamedTemporaryFile
import logging
from datetime import datetime
from pathlib import Path

from app.core.dependencies import get_db
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_dna_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Dict[str, Any] = Depends(get_db)
):
    """
    Upload a DNA file (23andMe or Ancestry format).
    The file will be saved to both the uploads directory for permanent storage
    and the cache/uploads directory for quick access.
    """
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="File must be a .txt file")
    
    # Create a temporary file to store the uploaded content
    with NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
        # Write the uploaded file content to the temporary file
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        # Calculate a file hash for identification
        hash_obj = hashlib.sha256(content)
        file_hash = hash_obj.hexdigest()
        
        # Create safe filename with hash prefix to avoid collisions
        safe_filename = f"{file_hash[:8]}_{file.filename}"
        
        # Save to the uploads directory (permanent storage)
        uploads_path = Path(settings.UPLOADS_DIR) / safe_filename
        with open(uploads_path, "wb") as f:
            # Reset file pointer to beginning
            with open(temp_file_path, "rb") as temp:
                f.write(temp.read())
                
        logger.info(f"File saved to uploads directory: {uploads_path}")
                
        # Also save to the cache/uploads directory for quick access
        cache_path = Path(settings.UPLOADS_CACHE_DIR) / safe_filename
        with open(cache_path, "wb") as f:
            # Reset file pointer to beginning
            with open(temp_file_path, "rb") as temp:
                f.write(temp.read())
                
        logger.info(f"File saved to cache directory: {cache_path}")
        
        # Get file size for reporting
        file_size = os.path.getsize(uploads_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        
        # Here you would typically do more processing, like:
        # - Validating the DNA file format
        # - Counting SNPs
        # - Adding to database
        # For now we'll return basic info
        return {
            "filename": file.filename,
            "safe_filename": safe_filename,
            "file_hash": file_hash,
            "status": "success",
            "size": file_size,
            "size_mb": file_size_mb,
            "uploads_path": str(uploads_path),
            "cache_path": str(cache_path),
            "message": "File uploaded and cached successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error processing DNA file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing DNA file: {str(e)}")
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@router.get("/formats")
async def get_supported_formats():
    """
    Return information about the supported DNA file formats
    """
    return {
        "formats": [
            {
                "name": "23andMe",
                "description": "Raw DNA data from 23andMe",
                "columns": ["rsid", "chromosome", "position", "genotype"],
                "example": "rs4477212\t1\t82154\tAA"
            },
            {
                "name": "Ancestry DNA",
                "description": "Raw DNA data from Ancestry DNA",
                "columns": ["rsid", "chromosome", "position", "allele1", "allele2"],
                "example": "rs4477212\t1\t82154\tA\tA"
            }
        ]
    }

@router.get("/uploads", summary="List uploaded DNA files")
async def list_uploaded_files(
    limit: int = Query(50, description="Maximum number of files to return"),
    offset: int = Query(0, description="Number of files to skip")
):
    """
    List all DNA files in the uploads directory with detailed information.
    """
    try:
        uploads_dir = Path(settings.UPLOADS_DIR)
        
        # Check if the uploads directory exists
        if not uploads_dir.exists():
            return {
                "files": [],
                "count": 0,
                "message": "Uploads directory does not exist"
            }
            
        # Get all files in the uploads directory
        all_files = []
        for file_path in uploads_dir.glob("*.*"):
            # Skip directories
            if file_path.is_dir():
                continue
                
            # Get file stats
            stats = file_path.stat()
            
            # Calculate a simple hash from filename for demo purposes
            # In production, you'd use the actual file hash stored in your database
            simple_hash = hashlib.md5(file_path.name.encode()).hexdigest()
            
            file_info = {
                "filename": file_path.name,
                "path": str(file_path),
                "size": stats.st_size,
                "size_mb": round(stats.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "file_hash": simple_hash,
                "extension": file_path.suffix.lstrip('.')
            }
            all_files.append(file_info)
            
        # Sort files by modification time (newest first)
        all_files.sort(key=lambda x: x["modified_at"], reverse=True)
        
        # Apply pagination
        total_count = len(all_files)
        paginated_files = all_files[offset:offset+limit]
        
        return {
            "files": paginated_files,
            "count": total_count,
            "limit": limit,
            "offset": offset,
            "uploads_directory": str(uploads_dir)
        }
    except Exception as e:
        logger.error(f"Error listing uploaded files: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error listing uploaded files: {str(e)}"
        )