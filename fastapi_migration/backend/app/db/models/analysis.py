from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base

class Analysis(Base):
    """
    Analysis model for storing genetic analysis results.
    """
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional user association
    dna_file_id = Column(Integer, ForeignKey("dna_files.id"), nullable=True)  # Optional file association
    file_hash = Column(String, index=True, nullable=True)  # For lookup without DB join
    status = Column(String, nullable=False, default="pending")  # pending, completed, error
    data = Column(JSON, nullable=True)  # Complete analysis results
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    dna_file = relationship("DNAFile", back_populates="analyses")
    reports = relationship("Report", back_populates="analysis", cascade="all, delete-orphan")

# Add back-reference to User model
from app.db.models.user import User
User.analyses = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")