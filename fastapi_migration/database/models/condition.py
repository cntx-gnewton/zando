from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Import Base from the existing session.py once integrated
# For now we'll define it here for reference
Base = declarative_base()

class SkinCondition(Base):
    """
    SkinCondition database model.
    
    Represents various skin conditions that may be related to genetic characteristics,
    such as eczema, acne, hyperpigmentation, etc.
    """
    __tablename__ = "skincondition"
    
    condition_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    severity_scale = Column(Text)
    
    # Relationships - these will be defined once all models exist
    # characteristics = relationship("CharacteristicConditionLink", back_populates="condition")
    # ingredients = relationship("ConditionIngredientLink", back_populates="condition")

    def __repr__(self):
        return f"<SkinCondition(name='{self.name}')>"
        
        
class CharacteristicConditionLink(Base):
    """
    Association table linking skin characteristics to skin conditions.
    
    Describes how different skin characteristics relate to specific skin conditions.
    """
    __tablename__ = "characteristic_condition_link"
    
    characteristic_id = Column(Integer, ForeignKey("skincharacteristic.characteristic_id"), primary_key=True)
    condition_id = Column(Integer, ForeignKey("skincondition.condition_id"), primary_key=True)
    relationship_type = Column(String)
    
    # Relationships - will be properly set up when related models exist
    # characteristic = relationship("SkinCharacteristic", back_populates="conditions")
    # condition = relationship("SkinCondition", back_populates="characteristics")

    def __repr__(self):
        return f"<CharacteristicConditionLink(characteristic_id={self.characteristic_id}, condition_id={self.condition_id})>"


class ConditionIngredientLink(Base):
    """
    Association table linking skin conditions to recommended ingredients.
    
    Describes which ingredients are beneficial for specific skin conditions.
    """
    __tablename__ = "condition_ingredient_link"
    
    condition_id = Column(Integer, ForeignKey("skincondition.condition_id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredient.ingredient_id"), primary_key=True)
    recommendation_strength = Column(String)
    guidance_notes = Column(Text)
    
    # Relationships - will be properly set up when related models exist
    # condition = relationship("SkinCondition", back_populates="ingredients")
    # ingredient = relationship("Ingredient", back_populates="conditions")

    def __repr__(self):
        return f"<ConditionIngredientLink(condition_id={self.condition_id}, ingredient_id={self.ingredient_id})>"