from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Import Base from the existing session.py once integrated
# For now we'll define it here for reference
Base = declarative_base()

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
    
    # Relationships - these will be defined once all models exist
    # snps = relationship("SNPCharacteristicLink", back_populates="characteristic")
    # conditions = relationship("CharacteristicConditionLink", back_populates="characteristic")

    def __repr__(self):
        return f"<SkinCharacteristic(name='{self.name}')>"