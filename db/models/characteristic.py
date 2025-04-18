"""
SQLAlchemy model for skin characteristics.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base

class SkinCharacteristic(Base):
    """
    SkinCharacteristic database model.
    
    Represents various skin characteristics that can be influenced by genetic factors,
    such as barrier function, melanin production, inflammatory response, etc.
    """
    __tablename__ = "skincharacteristic"
    
    characteristic_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    measurement_method = Column(Text)
    
    # Relationships
    snps = relationship("SNPCharacteristicLink", back_populates="characteristic", cascade="all, delete-orphan")
    conditions = relationship("CharacteristicConditionLink", back_populates="characteristic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SkinCharacteristic(name='{self.name}')>"