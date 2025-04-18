from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

# DNA file schemas
class DNAFileBase(BaseModel):
    filename: str
    file_hash: str

class DNAFileCreate(DNAFileBase):
    file_path: Optional[str] = None
    user_id: Optional[int] = None
    file_format: Optional[str] = None
    snp_count: Optional[int] = None

class DNAFileUpdate(BaseModel):
    file_path: Optional[str] = None
    file_format: Optional[str] = None
    snp_count: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None

class DNAFileInDBBase(DNAFileBase):
    id: int
    status: str
    created_at: datetime
    file_format: Optional[str] = None
    snp_count: Optional[int] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True

class DNAFile(DNAFileInDBBase):
    """DNA file model returned to client"""
    pass

# API response schemas
class DNAFileResponse(BaseModel):
    filename: str
    file_hash: str
    status: str
    snp_count: Optional[int] = None
    processing_time: Optional[float] = None
    message: Optional[str] = None
    cached: bool = False

class SNPDataResponse(BaseModel):
    filename: str
    valid: bool
    format: Optional[str] = None
    snp_count: int = 0
    chromosomes: Dict[str, int] = {}
    statistics: Dict[str, Any] = {}
    errors: List[str] = []

# SNP-related schemas
class SNP(BaseModel):
    rsid: str
    chromosome: str
    position: str
    allele1: str
    allele2: str

class SNPBatch(BaseModel):
    snps: List[SNP] = []