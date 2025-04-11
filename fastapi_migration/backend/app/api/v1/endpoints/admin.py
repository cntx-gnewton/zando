from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Dict, Any
import logging
import time

from app.services.analysis_service import AnalysisService
from app.core.dependencies import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/cache/status", summary="Check all reference data cache status")
async def check_cache_status():
    """
    Check the status of all reference data caches, including when they were last updated
    and how many records they contain.
    """
    current_time = time.time()
    
    # Calculate age for each cache
    snp_cache_age = current_time - AnalysisService._snp_cache_timestamp if AnalysisService._snp_cache_timestamp else 0
    char_cache_age = current_time - AnalysisService._characteristics_cache_timestamp if AnalysisService._characteristics_cache_timestamp else 0
    ingr_cache_age = current_time - AnalysisService._ingredients_cache_timestamp if AnalysisService._ingredients_cache_timestamp else 0
    
    # Calculate total memory usage (rough estimate)
    total_memory_mb = 0
    if AnalysisService._snp_cache:
        total_memory_mb += len(str(AnalysisService._snp_cache)) / (1024 * 1024)
    if AnalysisService._characteristics_cache:
        total_memory_mb += len(str(AnalysisService._characteristics_cache)) / (1024 * 1024)
    if AnalysisService._ingredients_cache:
        total_memory_mb += len(str(AnalysisService._ingredients_cache)) / (1024 * 1024)
    
    return {
        "summary": {
            "all_caches_valid": all([
                bool(AnalysisService._snp_cache) and snp_cache_age < AnalysisService._CACHE_DURATION,
                bool(AnalysisService._characteristics_cache) and char_cache_age < AnalysisService._CACHE_DURATION,
                bool(AnalysisService._ingredients_cache) and ingr_cache_age < AnalysisService._CACHE_DURATION
            ]),
            "cache_expiry_hours": AnalysisService._CACHE_DURATION / 3600,
            "estimated_memory_usage_mb": round(total_memory_mb, 2),
            "last_updated": time.strftime(
                '%Y-%m-%d %H:%M:%S', 
                time.localtime(min(filter(None, [
                    AnalysisService._snp_cache_timestamp, 
                    AnalysisService._characteristics_cache_timestamp,
                    AnalysisService._ingredients_cache_timestamp
                ])) if any([AnalysisService._snp_cache_timestamp, 
                          AnalysisService._characteristics_cache_timestamp,
                          AnalysisService._ingredients_cache_timestamp]) else current_time))
        },
        "caches": {
            "snp": {
                "exists": bool(AnalysisService._snp_cache),
                "records_count": len(AnalysisService._snp_cache) if AnalysisService._snp_cache else 0,
                "age_hours": round(snp_cache_age / 3600, 2),
                "is_expired": snp_cache_age > AnalysisService._CACHE_DURATION if AnalysisService._snp_cache_timestamp else True,
                "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(AnalysisService._snp_cache_timestamp)) if AnalysisService._snp_cache_timestamp else None
            },
            "characteristics": {
                "exists": bool(AnalysisService._characteristics_cache),
                "records_count": len(AnalysisService._characteristics_cache) if AnalysisService._characteristics_cache else 0,
                "age_hours": round(char_cache_age / 3600, 2),
                "is_expired": char_cache_age > AnalysisService._CACHE_DURATION if AnalysisService._characteristics_cache_timestamp else True,
                "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(AnalysisService._characteristics_cache_timestamp)) if AnalysisService._characteristics_cache_timestamp else None
            },
            "ingredients": {
                "exists": bool(AnalysisService._ingredients_cache),
                "records_count": len(AnalysisService._ingredients_cache) if AnalysisService._ingredients_cache else 0,
                "age_hours": round(ingr_cache_age / 3600, 2),
                "is_expired": ingr_cache_age > AnalysisService._CACHE_DURATION if AnalysisService._ingredients_cache_timestamp else True,
                "last_updated": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(AnalysisService._ingredients_cache_timestamp)) if AnalysisService._ingredients_cache_timestamp else None
            }
        }
    }

@router.post("/cache/refresh", summary="Refresh all reference data caches")
async def refresh_all_caches(db: AsyncSession = Depends(get_db)):
    """
    Force a refresh of all reference data caches.
    """
    try:
        start_time = time.time()
        
        # Get database connection from session
        conn = await db.connection()
        
        # Clear all caches
        AnalysisService._snp_cache = {}
        AnalysisService._snp_cache_timestamp = None
        AnalysisService._characteristics_cache = {}
        AnalysisService._characteristics_cache_timestamp = None
        AnalysisService._ingredients_cache = {}
        AnalysisService._ingredients_cache_timestamp = None
        
        # Force a full refresh of all caches in parallel
        results = {}
        
        # Refresh SNP cache
        snps = await AnalysisService.get_all_snps_cached(conn)
        results['snp'] = {
            "records_cached": len(snps),
            "cache_size_mb": round(len(str(snps)) / (1024 * 1024), 2)
        }
        
        # Refresh characteristics cache
        chars = await AnalysisService.get_all_characteristics_cached(conn)
        results['characteristics'] = {
            "records_cached": len(chars),
            "cache_size_mb": round(len(str(chars)) / (1024 * 1024), 2)
        }
        
        # Refresh ingredients cache
        ingrs = await AnalysisService.get_all_ingredients_cached(conn)
        results['ingredients'] = {
            "records_cached": len(ingrs),
            "cache_size_mb": round(len(str(ingrs)) / (1024 * 1024), 2)
        }
        
        elapsed_time = time.time() - start_time
        
        return {
            "success": True, 
            "processing_time_seconds": round(elapsed_time, 2),
            "total_memory_mb": round(sum(r["cache_size_mb"] for r in results.values()), 2),
            "caches": results,
            "message": f"All reference data caches refreshed in {round(elapsed_time, 2)} seconds"
        }
    except Exception as e:
        logger.error(f"Error refreshing caches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing caches: {str(e)}")

@router.post("/cache/refresh/snp", summary="Refresh SNP cache only")
async def refresh_snp_cache(db: AsyncSession = Depends(get_db)):
    """
    Force a refresh of only the SNP table cache.
    """
    try:
        start_time = time.time()
        
        # Get database connection from session
        conn = await db.connection()
        
        # Force a refresh of the cache by calling the get_all_snps_cached method
        # but first clear the existing cache
        AnalysisService._snp_cache = {}
        AnalysisService._snp_cache_timestamp = None
        
        # This will force a full refresh
        snps = await AnalysisService.get_all_snps_cached(conn)
        
        elapsed_time = time.time() - start_time
        
        return {
            "success": True, 
            "records_cached": len(snps),
            "processing_time_seconds": round(elapsed_time, 2),
            "cache_size_mb": round(len(str(snps)) / (1024 * 1024), 2),  # Rough estimate of memory usage
            "message": f"SNP cache refreshed with {len(snps)} records in {round(elapsed_time, 2)} seconds"
        }
    except Exception as e:
        logger.error(f"Error refreshing SNP cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing SNP cache: {str(e)}")

@router.post("/cache/refresh/characteristics", summary="Refresh characteristics cache only")
async def refresh_characteristics_cache(db: AsyncSession = Depends(get_db)):
    """
    Force a refresh of only the characteristics cache.
    """
    try:
        start_time = time.time()
        
        # Get database connection from session
        conn = await db.connection()
        
        # Force a refresh of the cache
        AnalysisService._characteristics_cache = {}
        AnalysisService._characteristics_cache_timestamp = None
        
        # This will force a full refresh
        chars = await AnalysisService.get_all_characteristics_cached(conn)
        
        elapsed_time = time.time() - start_time
        
        total_chars = sum(len(v) for v in chars.values())
        
        return {
            "success": True, 
            "snps_with_characteristics": len(chars),
            "total_characteristics": total_chars,
            "processing_time_seconds": round(elapsed_time, 2),
            "cache_size_mb": round(len(str(chars)) / (1024 * 1024), 2),
            "message": f"Characteristics cache refreshed with {total_chars} records for {len(chars)} SNPs in {round(elapsed_time, 2)} seconds"
        }
    except Exception as e:
        logger.error(f"Error refreshing characteristics cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing characteristics cache: {str(e)}")

@router.post("/cache/refresh/ingredients", summary="Refresh ingredients cache only")
async def refresh_ingredients_cache(db: AsyncSession = Depends(get_db)):
    """
    Force a refresh of only the ingredients cache.
    """
    try:
        start_time = time.time()
        
        # Get database connection from session
        conn = await db.connection()
        
        # Force a refresh of the cache
        AnalysisService._ingredients_cache = {}
        AnalysisService._ingredients_cache_timestamp = None
        
        # This will force a full refresh
        ingrs = await AnalysisService.get_all_ingredients_cached(conn)
        
        elapsed_time = time.time() - start_time
        
        # Count beneficial and cautionary ingredients
        total_beneficial = sum(len(b) for b, _ in ingrs.values())
        total_cautions = sum(len(c) for _, c in ingrs.values())
        active_snps = sum(1 for _, (b, c) in ingrs.items() if b or c)
        
        return {
            "success": True, 
            "snps_with_ingredients": active_snps,
            "beneficial_ingredients": total_beneficial,
            "cautionary_ingredients": total_cautions,
            "processing_time_seconds": round(elapsed_time, 2),
            "cache_size_mb": round(len(str(ingrs)) / (1024 * 1024), 2),
            "message": f"Ingredients cache refreshed with {total_beneficial + total_cautions} records for {active_snps} SNPs in {round(elapsed_time, 2)} seconds"
        }
    except Exception as e:
        logger.error(f"Error refreshing ingredients cache: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error refreshing ingredients cache: {str(e)}")

@router.delete("/cache", summary="Clear all reference data caches") 
async def clear_all_caches():
    """
    Clear all reference data caches completely.
    """
    try:
        # Get sizes before clearing
        snp_size = len(AnalysisService._snp_cache) if AnalysisService._snp_cache else 0
        char_size = len(AnalysisService._characteristics_cache) if AnalysisService._characteristics_cache else 0
        ingr_size = len(AnalysisService._ingredients_cache) if AnalysisService._ingredients_cache else 0
        
        # Clear all caches
        AnalysisService._snp_cache = {}
        AnalysisService._snp_cache_timestamp = None
        AnalysisService._characteristics_cache = {}
        AnalysisService._characteristics_cache_timestamp = None
        AnalysisService._ingredients_cache = {}
        AnalysisService._ingredients_cache_timestamp = None
        
        total_cleared = snp_size + char_size + ingr_size
        
        return {
            "success": True,
            "total_records_cleared": total_cleared,
            "caches_cleared": {
                "snp": snp_size,
                "characteristics": char_size,
                "ingredients": ingr_size
            },
            "message": f"All reference data caches cleared ({total_cleared} total records removed)"
        }
    except Exception as e:
        logger.error(f"Error clearing caches: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error clearing caches: {str(e)}")

@router.get("/database/stats", summary="Get database statistics")
async def get_database_stats(db: AsyncSession = Depends(get_db)):
    """
    Get statistics about the database tables.
    """
    try:
        conn = await db.connection()
        
        # Get table sizes and row counts 
        query = """
        SELECT 
            table_name,
            pg_total_relation_size(quote_ident(table_name)) AS size_bytes,
            (SELECT reltuples FROM pg_class WHERE relname = table_name) AS row_count
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY size_bytes DESC;
        """
        
        results = await conn.execute(text(query))
        tables = []
        
        for row in results:
            try:
                # Try attribute access
                table = {
                    "name": row.table_name,
                    "size_bytes": row.size_bytes,
                    "size_mb": round(row.size_bytes / (1024 * 1024), 2),
                    "row_count": int(row.row_count)
                }
            except (AttributeError, TypeError):
                # Fall back to index-based access
                table = {
                    "name": row[0],
                    "size_bytes": row[1],
                    "size_mb": round(row[1] / (1024 * 1024), 2),
                    "row_count": int(row[2])
                } 
            
            tables.append(table)
        
        # Get total database size
        size_query = "SELECT pg_database_size(current_database());"
        size_result = await conn.execute(text(size_query))
        
        try:
            # Try scalar
            total_size = size_result.scalar()
        except (AttributeError, TypeError):
            # Fall back
            row = size_result.fetchone()
            total_size = row[0] if row else 0
        
        return {
            "tables": tables,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size else 0,
            "total_tables": len(tables)
        }
        
    except Exception as e:
        logger.error(f"Error getting database stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting database stats: {str(e)}")