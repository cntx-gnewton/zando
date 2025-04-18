import os
import uuid
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.models.report import Report
from app.schemas.report import ReportMetadata
from app.core.config import settings
from app.services.dna_service import DNAService

logger = logging.getLogger(__name__)

class ReportService:
    """
    Service for managing report generation and storage.
    """
    
    @staticmethod
    def get_cached_report(report_data: Dict[str, Any], report_type: str = "markdown") -> Optional[bytes]:
        """
        Check if a report with the same data exists in cache.
        
        Args:
            report_data: The analysis data to create a report from
            report_type: Type of report ("markdown" or "standard")
            
        Returns:
            Cached report binary data if exists, None otherwise
        """
        # Create a hash of the report data and type for cache lookup
        import hashlib
        import json
        
        # Create a deterministic representation of the report data
        data_str = json.dumps(report_data, sort_keys=True)
        hash_key = f"{report_type}_{hashlib.sha256(data_str.encode()).hexdigest()}"
        
        # Check cache for this report
        return DNAService.load_from_cache(hash_key, format_type='pdf')
    
    @staticmethod
    def cache_report(report_data: Dict[str, Any], pdf_data: bytes, report_type: str = "markdown") -> None:
        """
        Cache a generated report for future use.
        
        Args:
            report_data: The analysis data used to create the report
            pdf_data: The binary PDF data
            report_type: Type of report ("markdown" or "standard")
        """
        import hashlib
        import json
        
        # Create a deterministic representation of the report data
        data_str = json.dumps(report_data, sort_keys=True)
        hash_key = f"{report_type}_{hashlib.sha256(data_str.encode()).hexdigest()}"
        
        # Save to cache
        DNAService.save_to_cache(pdf_data, hash_key, format_type='pdf')
    
    @staticmethod
    async def record_report_generation(
        db: AsyncSession, 
        report_id: str, 
        report_type: str,
        report_path: str,
        file_hash: Optional[str] = None,
        analysis_id: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> Report:
        """
        Record report generation in the database.
        
        Args:
            db: Database session
            report_id: Unique ID for the report
            report_type: Type of report ("markdown" or "standard")
            report_path: Path to the generated report file
            file_hash: Hash of the DNA file (optional)
            analysis_id: ID of the analysis used (optional)
            user_id: ID of the user (optional)
            
        Returns:
            The created Report record
        """
        try:
            # Get analysis ID from database if provided
            analysis_db_id = None
            if analysis_id:
                try:
                    result = await db.execute(
                        text("SELECT id FROM analyses WHERE analysis_id = :analysis_id"),
                        {"analysis_id": analysis_id}
                    )
                    record = result.first()
                    if record:
                        # Handle both attribute and index-based access
                        if hasattr(record, 'id'):
                            analysis_db_id = record.id
                        else:
                            analysis_db_id = record[0]
                        logger.info(f"Found analysis database ID: {analysis_db_id} for analysis_id: {analysis_id}")
                except Exception as e:
                    logger.warning(f"Could not find analysis by ID {analysis_id}: {e}")
                    
            # Use direct SQL insertion to avoid ORM persistence issues
            logger.info(f"Recording report generation: {report_id}, analysis_db_id: {analysis_db_id}")
            
            query = """
            INSERT INTO reports (report_id, user_id, analysis_id, file_hash, report_type, report_path, created_at, is_cached)
            VALUES (:report_id, :user_id, :analysis_id, :file_hash, :report_type, :report_path, NOW(), FALSE)
            RETURNING id
            """
            
            params = {
                "report_id": report_id,
                "user_id": user_id,
                "analysis_id": analysis_db_id,
                "file_hash": file_hash,
                "report_type": report_type,
                "report_path": report_path
            }
            
            # Execute the insert directly
            result = await db.execute(text(query), params)
            await db.commit()
            
            # Retrieve the newly created report
            get_query = "SELECT * FROM reports WHERE report_id = :report_id"
            result = await db.execute(text(get_query), {"report_id": report_id})
            report_row = result.first()
            
            # Create a Report instance from the row data
            if report_row:
                if hasattr(report_row, '_mapping'):
                    # SQLAlchemy 1.4+ result
                    report_dict = dict(report_row._mapping)
                    report = Report(**report_dict)
                else:
                    # Handle tuple-like result
                    report = Report(
                        id=report_row[0],
                        report_id=report_row[1],
                        user_id=report_row[2],
                        analysis_id=report_row[3],
                        file_hash=report_row[4],
                        report_type=report_row[5],
                        report_path=report_row[6],
                        is_cached=report_row[7],
                        created_at=report_row[8]
                    )
                
                logger.info(f"Successfully created report record with ID: {report.id}")
                return report
            else:
                logger.error("Failed to retrieve newly created report record")
                raise Exception("Failed to retrieve report record after insertion")
                
        except Exception as e:
            logger.error(f"Error recording report generation: {str(e)}")
            # Try to rollback the transaction
            try:
                await db.rollback()
            except:
                pass
            raise e
    
    @staticmethod
    async def get_report_by_id(report_id: str, db: AsyncSession) -> Optional[Report]:
        """
        Get a report by its ID.
        
        Args:
            report_id: ID of the report
            db: Database session
            
        Returns:
            Report object if found, None otherwise
        """
        result = await db.execute(
            text("SELECT * FROM reports WHERE report_id = :report_id"),
            {"report_id": report_id}
        )
        return result.first()
    
    @staticmethod
    async def get_user_reports(user_id: int, db: AsyncSession) -> List[ReportMetadata]:
        """
        Get all reports for a user.
        
        Args:
            user_id: ID of the user
            db: Database session
            
        Returns:
            List of report metadata
        """
        result = await db.execute(
            text("SELECT * FROM reports WHERE user_id = :user_id ORDER BY created_at DESC"),
            {"user_id": user_id}
        )
        reports = result.fetchall()
        
        # Convert to ReportMetadata objects
        return [
            ReportMetadata(
                report_id=report.report_id,
                created_at=report.created_at,
                report_type=report.report_type,
                file_hash=report.file_hash,
                analysis_id=str(report.analysis_id) if report.analysis_id else None,
                download_url=f"/api/v1/reports/{report.report_id}/download"
            )
            for report in reports
        ]