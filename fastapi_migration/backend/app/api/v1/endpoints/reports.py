from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Path
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os
import uuid
import time
import logging

from app.services.dna_service import DNAService
from app.services.analysis_service import AnalysisService
from app.services.report_service import ReportService
from app.services.pdf_service import PDFService
from app.schemas.report import ReportRequest, ReportResponse, ReportMetadata
from app.core.dependencies import get_db
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

# Create reports directory if it doesn't exist
os.makedirs(settings.REPORTS_DIR, exist_ok=True)

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a report from DNA analysis results.
    If file_hash is provided, the system will look for cached DNA data.
    If analysis_id is provided, the system will use existing analysis results.
    At least one of these parameters must be provided.
    """
    if not request.file_hash and not request.analysis_id:
        raise HTTPException(
            status_code=400, 
            detail="Either file_hash or analysis_id must be provided"
        )
    
    try:
        start_time = time.time()
        
        # Generate a unique report ID
        report_id = str(uuid.uuid4())
        
        # Determine the file path for the report
        report_filename = f"report_{report_id}.pdf"
        report_path = os.path.join(settings.REPORTS_DIR, report_filename)
        report_data = None
        if request.file_hash:
            # Check for cached analysis data
            cached_analysis = AnalysisService.get_cached_analysis(request.file_hash)
            
            if cached_analysis:
                # Use cached analysis data
                report_data = cached_analysis
                logger.info(f"Using cached analysis data for file hash: {request.file_hash}")
            else:
                # Retrieve DNA data from cache or database
                snp_data = await DNAService.get_snp_data_by_hash(request.file_hash, db)
                if not snp_data:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No DNA data found for file hash: {request.file_hash}"
                    )
                
                # Perform analysis
                report_data = await AnalysisService.process_snp_data(snp_data, db)
                
                # Cache the analysis results
                AnalysisService.cache_analysis_results(request.file_hash, report_data)
        
        elif request.analysis_id:
            # Retrieve existing analysis results
            analysis_record = await AnalysisService.get_analysis_by_id(request.analysis_id, db)
            if not analysis_record:
                raise HTTPException(
                    status_code=404,
                    detail=f"Analysis not found with ID: {request.analysis_id}"
                )
            
            report_data = analysis_record['data']
        
        # Check if we have a cached report PDF
        cached_pdf = ReportService.get_cached_report(report_data, report_type=request.report_type)
        
        if cached_pdf:
            # Use cached PDF
            with open(report_path, 'wb') as f:
                f.write(cached_pdf)
            cached = True
        else:
            # Generate a new report based on the specified type
            if request.report_type == "markdown":
                await PDFService.generate_markdown_report(report_data, report_path, db)
            else:
                await PDFService.generate_pdf_report(report_data, report_path, db)
            
            # Cache the generated PDF
            with open(report_path, 'rb') as f:
                ReportService.cache_report(report_data, f.read(), report_type=request.report_type)
            
            cached = False
        
        # Record the report generation in the database
        report_record = await ReportService.record_report_generation(
            db=db,
            report_id=report_id,
            report_type=request.report_type,
            file_hash=request.file_hash,
            analysis_id=request.analysis_id,
            report_path=report_path
        )
        
        elapsed_time = time.time() - start_time
        
        return ReportResponse(
            report_id=report_id,
            status="success",
            message="Report generated successfully",
            processing_time=elapsed_time,
            download_url=f"/api/v1/reports/{report_id}/download",
            cached=cached
        )
    
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

@router.get("/{report_id}", response_model=ReportMetadata)
async def get_report_metadata(
    report_id: str = Path(..., description="The ID of the report"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get metadata about a generated report.
    """
    report_record = await ReportService.get_report_by_id(report_id, db)
    if not report_record:
        raise HTTPException(status_code=404, detail=f"Report not found with ID: {report_id}")
    
    return ReportMetadata(
        report_id=report_record.report_id,
        created_at=report_record.created_at,
        report_type=report_record.report_type,
        file_hash=report_record.file_hash,
        analysis_id=report_record.analysis_id,
        download_url=f"/api/v1/reports/{report_id}/download"
    )

@router.get("/{report_id}/download")
async def download_report(
    report_id: str = Path(..., description="The ID of the report"),
    db: AsyncSession = Depends(get_db)
):
    """
    Download a generated report as a PDF.
    """
    report_record = await ReportService.get_report_by_id(report_id, db)
    if not report_record:
        raise HTTPException(status_code=404, detail=f"Report not found with ID: {report_id}")
    
    # Verify the file exists
    if not os.path.exists(report_record.report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Return the file as a download
    return FileResponse(
        path=report_record.report_path,
        filename=f"genomic_report_{report_id}.pdf",
        media_type="application/pdf"
    )