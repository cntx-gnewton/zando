from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any, Optional
import logging

from app.services.cache_service import CacheService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", summary="Get cache overview")
def get_cache_stats():
    """
    Get overall statistics about the cache including total files, sizes, and formats.
    """
    try:
        stats = CacheService.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")

@router.get("/files", summary="List cache files")
def list_cache_files(format_type: Optional[str] = Query(None, description="Filter by file format (e.g., json, pdf, md)")):
    """
    List all files in the cache with detailed metadata.
    Optionally filter by file format.
    """
    try:
        files = CacheService.list_cache_files(format_type)
        return {
            "files": files,
            "count": len(files),
            "format_filter": format_type
        }
    except Exception as e:
        logger.error(f"Error listing cache files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing cache files: {str(e)}")

@router.get("/file/{file_hash}", summary="Get cache for specific file")
def get_cache_for_file(file_hash: str = Path(..., description="Hash of the file to look up")):
    """
    Get details about all cached files associated with a specific file hash.
    """
    try:
        cache_info = CacheService.get_cache_for_file(file_hash)
        if cache_info['total_files'] == 0:
            return {
                "message": f"No cache files found for hash: {file_hash}",
                "file_hash": file_hash,
                "cache_files": []
            }
        return cache_info
    except Exception as e:
        logger.error(f"Error getting cache for file {file_hash}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache for file: {str(e)}")

@router.delete("/file/{file_hash}", summary="Delete cache for specific file")
def delete_cache_for_file(file_hash: str = Path(..., description="Hash of the file to delete from cache")):
    """
    Delete all cached files associated with a specific file hash.
    """
    try:
        result = CacheService.delete_cache_for_file(file_hash)
        if result['files_removed'] == 0:
            return {
                "message": f"No cache files found for hash: {file_hash}",
                "file_hash": file_hash,
                "files_removed": 0
            }
        return {
            "message": f"Successfully removed {result['files_removed']} cache files for {file_hash}",
            **result
        }
    except Exception as e:
        logger.error(f"Error deleting cache for file {file_hash}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting cache for file: {str(e)}")

@router.delete("/expired", summary="Clear expired cache files")
def clean_expired_cache():
    """
    Remove all expired cache files based on the configured expiry time.
    """
    try:
        result = CacheService.clean_expired_cache()
        if result['files_removed'] == 0:
            return {
                "message": "No expired cache files found",
                "files_removed": 0
            }
        return {
            "message": f"Successfully removed {result['files_removed']} expired cache files ({result['mb_freed']:.2f} MB)",
            **result
        }
    except Exception as e:
        logger.error(f"Error cleaning expired cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cleaning expired cache: {str(e)}")

@router.delete("/all", summary="Clear entire cache")
def clean_all_cache():
    """
    Remove all files from the cache.
    WARNING: This will delete all cached data and may impact performance for subsequent requests.
    """
    try:
        result = CacheService.clean_all_cache()
        return {
            "message": f"Successfully removed {result['files_removed']} cache files ({result['mb_freed']:.2f} MB)",
            **result
        }
    except Exception as e:
        logger.error(f"Error cleaning all cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error cleaning all cache: {str(e)}")

# Synchronous endpoints (for environments with async issues)
@router.get("/sync", summary="Get cache overview (sync)")
def get_cache_stats_sync():
    """
    Synchronous version of the cache stats endpoint.
    """
    try:
        stats = CacheService.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")