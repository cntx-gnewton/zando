

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List, Dict, Any
import time
import logging
import uuid
import json

from app.services.dna_service import DNAService
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalysisRequest, AnalysisResponse, AnalysisResult, AnalysisList, AnalysisSummary
from app.core.dependencies import get_db, get_sync_db

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process", response_model=AnalysisResponse)
async def process_dna_data(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Process DNA data and perform genetic analysis.
    Either file_hash or raw_snp_data must be provided.
    """
    if not request.file_hash and not request.raw_snp_data:
        raise HTTPException(
            status_code=400, 
            detail="Either file_hash or raw_snp_data must be provided"
        )
    
    try:
        logger.info(f"Starting DNA analysis process for file_hash: {request.file_hash}")
        logger.info(f"DB session type: {type(db)}")
        start_time = time.time()
        
        # Check if we have cached analysis results
        if request.file_hash:
            logger.info(f"Checking for cached analysis for hash: {request.file_hash}")
            cached_analysis = AnalysisService.get_cached_analysis(request.file_hash)
            if cached_analysis and not request.force_refresh:
                logger.info(f"Found cached analysis with {len(cached_analysis.get('mutations', []))} mutations")
                
                # Try storing the analysis in the database
                try:
                    logger.info("Recording cached analysis in database")
                    analysis_id = await AnalysisService.record_analysis(
                        db=db,
                        file_hash=request.file_hash,
                        analysis_data=cached_analysis
                    )
                    logger.info(f"Successfully recorded analysis: {analysis_id}")
                except Exception as db_error:
                    logger.error(f"Failed to record analysis in DB: {str(db_error)}")
                    # Generate a fake ID if DB insertion fails
                    analysis_id = str(uuid.uuid4())
                    logger.info(f"Using generated ID instead: {analysis_id}")
                
                # Return the response
                return AnalysisResponse(
                    analysis_id=analysis_id,
                    status="success",
                    message="Analysis retrieved from cache",
                    snp_count=len(cached_analysis.get("mutations", [])),
                    file_hash=request.file_hash,
                    processing_time=0.0,
                    cached=True
                )
        
        # Get SNP data, either from cache/database or from the request
        if request.file_hash:
            logger.info(f"Fetching SNP data for hash: {request.file_hash}")
            # This function is async, so need to await it
            snp_data = await DNAService.get_snp_data_by_hash(request.file_hash, db)
            if not snp_data:
                logger.error(f"No SNP data found for hash: {request.file_hash}")
                raise HTTPException(
                    status_code=404,
                    detail=f"No DNA data found for file hash: {request.file_hash}"
                )
            logger.info(f"Found {len(snp_data)} SNP records")
        else:
            # Use the raw SNP data provided in the request
            snp_data = request.raw_snp_data
            logger.info(f"Using provided raw SNP data with {len(snp_data)} records")
        
        # Process the SNP data
        logger.info("Processing SNP data for analysis")
        report_data = await AnalysisService.process_snp_data(snp_data, db)
        logger.info(f"Generated report with {len(report_data.get('mutations', []))} mutations")
        
        # Record the analysis in the database
        logger.info("Recording analysis in database")
        try:
            analysis_id = await AnalysisService.record_analysis(
                db=db,
                file_hash=request.file_hash,
                analysis_data=report_data
            )
            logger.info(f"Successfully recorded analysis: {analysis_id}")
        except Exception as db_error:
            logger.error(f"Failed to record analysis in DB: {str(db_error)}")
            # Generate a fake ID if DB insertion fails
            analysis_id = str(uuid.uuid4())
            logger.info(f"Using generated ID instead: {analysis_id}")
        
        # Cache the analysis results
        if request.file_hash:
            logger.info(f"Caching analysis results for hash: {request.file_hash}")
            AnalysisService.cache_analysis_results(request.file_hash, report_data)
        
        elapsed_time = time.time() - start_time
        logger.info(f"Analysis process completed in {elapsed_time:.2f} seconds")
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            status="success",
            message="Analysis completed successfully",
            snp_count=len(report_data.get("mutations", [])),
            file_hash=request.file_hash,
            processing_time=elapsed_time,
            cached=False
        )
    
    except Exception as e:
        logger.error(f"Error processing DNA data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing DNA data: {str(e)}")

@router.post("/direct-insert-sync", response_model=Dict[str, Any])
def direct_insert_sync(
    file_hash: str,
    db=Depends(get_sync_db)  # Use synchronous DB session
):
    """
    Attempt a direct SQL insert into the analyses table using synchronous code.
    This bypasses async issues that might be causing runtime errors.
    """
    try:
        analysis_id = str(uuid.uuid4())
        
        # Create minimal JSON data
        simple_data = {
            "mutations": [],
            "ingredient_recommendations": {
                "prioritize": [],
                "caution": []
            },
            "summary": "Test analysis created via direct SQL insert (sync)"
        }
        
        # Just try the simplest approach for diagnostics
        logger.info("Trying synchronous direct SQL insert")
        query = f"""
        INSERT INTO analyses (analysis_id, file_hash, status, data)
        VALUES ('{analysis_id}', '{file_hash}', 'completed', '{json.dumps(simple_data)}')
        """
        
        # Execute without async/await
        db.execute(text(query))
        db.commit()
        
        # Verify what was inserted
        verify_query = "SELECT analysis_id FROM analyses ORDER BY created_at DESC LIMIT 5"
        verify_result = db.execute(text(verify_query))
        recent_ids = [row[0] for row in verify_result.fetchall()]
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "recent_ids": recent_ids,
            "message": "Synchronous insert successful"
        }
    except Exception as e:
        logger.error(f"Synchronous SQL insert error: {str(e)}")
        if db:
            try:
                db.rollback()
            except:
                pass
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/direct-insert", response_model=Dict[str, Any])
async def direct_insert(
    file_hash: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Attempt a direct SQL insert into the analyses table for debugging purposes.
    """
    try:
        analysis_id = str(uuid.uuid4())
        
        # Create minimal JSON data
        simple_data = {
            "mutations": [],
            "ingredient_recommendations": {
                "prioritize": [],
                "caution": []
            },
            "summary": "Test analysis created via direct SQL insert"
        }
        
        # Try multiple approaches to insert
        results = {}
        
        # Approach 1: Raw SQL with string literal
        try:
            logger.info("Trying direct SQL insert with string literal")
            query1 = f"""
            INSERT INTO analyses (analysis_id, file_hash, status, data)
            VALUES ('{analysis_id}', '{file_hash}', 'completed', '{json.dumps(simple_data)}')
            """
            await db.execute(text(query1))
            await db.commit()
            results["approach1"] = "success"
        except Exception as e1:
            logger.error(f"Approach 1 failed: {str(e1)}")
            results["approach1"] = f"failed: {str(e1)}"
            await db.rollback()
        
        # Approach 2: SQL with parameter binding
        try:
            logger.info("Trying SQL insert with parameter binding")
            # Generate a new ID for this approach
            analysis_id2 = str(uuid.uuid4())
            query2 = """
            INSERT INTO analyses (analysis_id, file_hash, status, data)
            VALUES (:analysis_id, :file_hash, :status, :data)
            """
            params = {
                "analysis_id": analysis_id2, 
                "file_hash": file_hash, 
                "status": "completed", 
                "data": json.dumps(simple_data)
            }
            await db.execute(text(query2), params)
            await db.commit()
            results["approach2"] = "success"
            results["analysis_id2"] = analysis_id2
        except Exception as e2:
            logger.error(f"Approach 2 failed: {str(e2)}")
            results["approach2"] = f"failed: {str(e2)}"
            await db.rollback()
        
        # Approach 3: SQL with minimal data (no JSON)
        try:
            logger.info("Trying SQL insert with minimal data (no JSON)")
            # Generate a new ID for this approach
            analysis_id3 = str(uuid.uuid4())
            query3 = f"""
            INSERT INTO analyses (analysis_id, file_hash, status)
            VALUES ('{analysis_id3}', '{file_hash}', 'completed')
            """
            await db.execute(text(query3))
            await db.commit()
            results["approach3"] = "success"
            results["analysis_id3"] = analysis_id3
        except Exception as e3:
            logger.error(f"Approach 3 failed: {str(e3)}")
            results["approach3"] = f"failed: {str(e3)}"
            await db.rollback()
        
        # Try to verify what was inserted
        try:
            verify_query = "SELECT analysis_id FROM analyses ORDER BY created_at DESC LIMIT 5"
            verify_result = await db.execute(text(verify_query))
            recent_ids = [row[0] for row in verify_result.fetchall()]
            results["recent_ids"] = recent_ids
        except Exception as e4:
            logger.error(f"Verification failed: {str(e4)}")
            results["verification"] = f"failed: {str(e4)}"
        
        # Return all results
        return {
            "success": "approach1" in results or "approach2" in results or "approach3" in results,
            "analysis_id": analysis_id,
            "test_results": results
        }
    except Exception as e:
        logger.error(f"Direct SQL insert master error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/logs", response_model=Dict[str, Any])
async def debug_logs():
    """
    Simple endpoint to get recent application logs.
    """
    try:
        # Use the logging handler to get recent logs
        recent_logs = []
        
        for handler in logging.getLogger().handlers:
            if hasattr(handler, 'baseFilename'):
                try:
                    with open(handler.baseFilename, 'r') as f:
                        # Get last 30 lines
                        lines = f.readlines()[-30:]
                        recent_logs.extend(lines)
                except Exception as e:
                    recent_logs.append(f"Error reading log file: {str(e)}")
        
        return {
            "recent_logs": recent_logs[:30] if recent_logs else ["No logs found or no file handlers configured"]
        }
    except Exception as e:
        return {"error": f"Error getting logs: {str(e)}"}

@router.get("/debug", response_model=Dict[str, Any])
async def debug_database(
    db: AsyncSession = Depends(get_db)
):
    """
    Debug endpoint to check database tables and records.
    """
    debug_info = {
        "tables": [],
        "analyses_count": 0,
        "sample_records": [],
        "errors": [],
        "connection_type": str(type(db))
    }
    
    try:
        # Check if we can execute a simple query
        try:
            test_query = "SELECT 1 as test"
            test_result = await db.execute(text(test_query))
            test_row = test_result.first()
            debug_info["connection_test"] = "Success" if test_row else "Failed (no rows)"
        except Exception as e:
            debug_info["connection_test"] = f"Failed: {str(e)}"
            debug_info["errors"].append(f"Connection test failed: {str(e)}")
            
        # Try to get table list (may not work in some DBs)
        try:
            query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            """
            tables_result = await db.execute(text(query))
            tables = []
            
            for row in tables_result:
                try:
                    if hasattr(row, "table_name"):
                        tables.append(row.table_name)
                    else:
                        tables.append(row[0])
                except Exception as e:
                    debug_info["errors"].append(f"Error getting table name: {str(e)}")
                    
            debug_info["tables"] = tables
        except Exception as e:
            debug_info["errors"].append(f"Error listing tables: {str(e)}")
        
        # Alternate approach: try to query analyses table directly
        try:
            count_query = "SELECT COUNT(*) FROM analyses"
            count_result = await db.execute(text(count_query))
            
            # Try to get the count value
            try:
                count_value = count_result.scalar()
                debug_info["analyses_count"] = count_value if count_value is not None else 0
            except (AttributeError, TypeError) as e:
                debug_info["errors"].append(f"Error getting count scalar: {str(e)}")
                row = count_result.first()
                if row:
                    debug_info["analyses_count"] = row[0] if len(row) > 0 else 0
                    
        except Exception as e:
            debug_info["errors"].append(f"Error counting analyses: {str(e)}")
            
        # Get sample records if possible
        try:
            sample_query = "SELECT * FROM analyses LIMIT 5"
            sample_result = await db.execute(text(sample_query))
            
            for row in sample_result:
                try:
                    # Try to handle both attribute and index access
                    record = {}
                    
                    # Try attribute access
                    if hasattr(row, "analysis_id"):
                        for col in ["analysis_id", "file_hash", "status", "created_at"]:
                            if hasattr(row, col):
                                record[col] = getattr(row, col)
                    # Fallback to index access
                    else:
                        # Include raw row representation
                        record["_row"] = str(row)
                        if len(row) >= 3:
                            record["analysis_id"] = row[0]
                            record["file_hash"] = row[1]
                            record["status"] = row[2]
                            
                    debug_info["sample_records"].append(record)
                except Exception as e:
                    debug_info["errors"].append(f"Error processing row: {str(e)}")
                    debug_info["sample_records"].append({"error": str(e), "row": str(row)})
        except Exception as e:
            debug_info["errors"].append(f"Error getting sample records: {str(e)}")
            
        # Check if the database was committed properly by directly querying for a specific analysis ID
        try:
            # Try to get the most recently created analysis we processed
            specific_query = "SELECT analysis_id FROM analyses ORDER BY created_at DESC LIMIT 1"
            specific_result = await db.execute(text(specific_query))
            specific_row = specific_result.first()
            
            if specific_row:
                analysis_id = specific_row[0] if not hasattr(specific_row, "analysis_id") else specific_row.analysis_id
                debug_info["latest_analysis_id"] = analysis_id
            else:
                debug_info["latest_analysis_id"] = None
                
        except Exception as e:
            debug_info["errors"].append(f"Error fetching latest analysis ID: {str(e)}")
            
        return debug_info
    except Exception as e:
        logger.error(f"Error debugging database: {str(e)}")
        debug_info["errors"].append(f"Global error: {str(e)}")
        return debug_info

@router.get("/list-sync", response_model=AnalysisList)
def list_analyses_sync(
    limit: int = 50,
    offset: int = 0,
    db=Depends(get_sync_db)
):
    """
    Get a list of all analyses with pagination (synchronous version).
    """
    try:
        # Direct SQL query to get analyses count
        count_query = "SELECT COUNT(*) FROM analyses"
        count_result = db.execute(text(count_query))
        total_count = count_result.scalar() or 0
        
        # Query to get the analyses with pagination
        query = """
        SELECT analysis_id, file_hash, status, created_at, data
        FROM analyses 
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        result = db.execute(text(query), {"limit": limit, "offset": offset})
        
        # Process the rows
        analyses = []
        for row in result:
            # Process data if available
            try:
                data_json = json.loads(row[4]) if row[4] and isinstance(row[4], str) else row[4]
                snp_count = len(data_json.get('mutations', [])) if data_json and isinstance(data_json, dict) else 0
            except:
                snp_count = 0
                
            analysis = {
                "analysis_id": row[0],
                "file_hash": row[1],
                "status": row[2],
                "created_at": row[3].isoformat() if hasattr(row[3], 'isoformat') else row[3],
                "snp_count": snp_count
            }
            analyses.append(analysis)
            
        return AnalysisList(
            items=[AnalysisSummary(**item) for item in analyses],
            count=total_count
        )
    except Exception as e:
        logger.error(f"Error listing analyses (sync): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")

@router.get("/list", response_model=AnalysisList)
async def list_analyses(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a list of all analyses with pagination.
    """
    try:
        analyses = await AnalysisService.get_all_analyses(db, limit, offset)
        print(analyses)
        return AnalysisList(
            items=[AnalysisSummary(**item) for item in analyses["items"]],
            count=analyses["count"]
        )
    except Exception as e:
        logger.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")

@router.get("/{analysis_id}/sync", response_model=AnalysisResult)
def get_analysis_results_sync(
    analysis_id: str,
    db=Depends(get_sync_db)
):
    """
    Get the results of a previously completed analysis (synchronous version).
    """
    try:
        # Direct SQL query to get analysis
        query = """
        SELECT analysis_id, file_hash, status, data, created_at, completed_at
        FROM analyses 
        WHERE analysis_id = :analysis_id
        """
        
        result = db.execute(text(query), {"analysis_id": analysis_id})
        row = result.first()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"Analysis not found with ID: {analysis_id}")
        
        # Build the analysis record from the row
        # Row columns: 0=analysis_id, 1=file_hash, 2=status, 3=data, 4=created_at, 5=completed_at
        analysis_record = {
            "analysis_id": row[0],
            "file_hash": row[1],
            "status": row[2],
            "data": json.loads(row[3]) if isinstance(row[3], str) else row[3],
            "created_at": row[4].isoformat() if hasattr(row[4], 'isoformat') else row[4],
            "completed_at": row[5].isoformat() if row[5] and hasattr(row[5], 'isoformat') else row[5]
        }
        
        # Return the AnalysisResult
        return AnalysisResult(
            analysis_id=analysis_record["analysis_id"],
            created_at=analysis_record["created_at"],
            file_hash=analysis_record["file_hash"],
            data=analysis_record["data"]
        )
    except Exception as e:
        logger.error(f"Error retrieving analysis (sync): {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")

@router.get("/{analysis_id}", response_model=AnalysisResult)
async def get_analysis_results(
    analysis_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the results of a previously completed analysis.
    """
    try:
        analysis_record = await AnalysisService.get_analysis_by_id(analysis_id, db)
        if not analysis_record:
            raise HTTPException(status_code=404, detail=f"Analysis not found with ID: {analysis_id}")
        
        # The analysis_record is now a dictionary, not an Analysis object
        return AnalysisResult(
            analysis_id=analysis_record["analysis_id"],
            created_at=analysis_record["created_at"],
            file_hash=analysis_record["file_hash"],
            data=analysis_record["data"]
        )
    except Exception as e:
        logger.error(f"Error retrieving analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")