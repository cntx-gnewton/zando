from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base

class Report(Base):
    """
    Report model for tracking generated reports.
    """
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional user association
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=True)  # Optional analysis association
    file_hash = Column(String, index=True, nullable=True)  # For lookup without DB join
    report_type = Column(String, nullable=False, default="standard")  # standard, markdown, etc.
    report_path = Column(String, nullable=True)  # Path to the generated report file
    is_cached = Column(Boolean, default=False)  # Whether this was served from cache
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reports")
    analysis = relationship("Analysis", back_populates="reports")

# Add back-reference to User model
from app.db.models.user import User
User.reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")