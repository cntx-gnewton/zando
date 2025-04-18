from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Report request schemas
class ReportRequest(BaseModel):
    file_hash: Optional[str] = None
    analysis_id: Optional[str] = None
    report_type: str = "markdown"  # markdown or standard
    include_raw_data: bool = False

# Report response schemas
class ReportResponse(BaseModel):
    report_id: str
    status: str
    message: str
    processing_time: Optional[float] = None
    download_url: str
    cached: bool = False

class ReportMetadata(BaseModel):
    report_id: str
    created_at: datetime
    report_type: str
    file_hash: Optional[str] = None
    analysis_id: Optional[str] = None
    download_url: str
    
    class Config:
        from_attributes = True

# Report listing schemas
class ReportSummary(BaseModel):
    report_id: str
    created_at: datetime
    report_type: str
    download_url: str

class UserReportsList(BaseModel):
    reports: List[ReportSummary] = []