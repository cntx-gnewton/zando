from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.session import Base

class DNAFile(Base):
    """
    DNA file model for tracking uploaded DNA files.
    """
    __tablename__ = "dna_files"
    
    id = Column(Integer, primary_key=True, index=True)
    file_hash = Column(String, unique=True, index=True, nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=True)  # Path to saved file if stored
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional user association
    file_format = Column(String, nullable=True)  # 23andMe, AncestryDNA, etc.
    snp_count = Column(Integer, nullable=True)
    status = Column(String, nullable=False, default="uploaded")  # uploaded, processed, error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="dna_files")
    analyses = relationship("Analysis", back_populates="dna_file", cascade="all, delete-orphan")

# Add back-reference to User model
from app.db.models.user import User
User.dna_files = relationship("DNAFile", back_populates="user", cascade="all, delete-orphan")