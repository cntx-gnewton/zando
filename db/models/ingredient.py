"""
SQLAlchemy models for ingredients and ingredient cautions.
"""

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from . import Base

class Ingredient(Base):
    """
    Ingredient database model.
    
    Represents skincare ingredients with their mechanisms of action and evidence levels.
    These are beneficial ingredients that may be recommended based on genetic profile.
    """
    __tablename__ = "ingredient"
    
    ingredient_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    mechanism = Column(Text)
    evidence_level = Column(String)
    contraindications = Column(Text)
    
    # Relationships
    snps = relationship("SNPIngredientLink", back_populates="ingredient", cascade="all, delete-orphan")
    conditions = relationship("ConditionIngredientLink", back_populates="ingredient", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ingredient(name='{self.name}')>"


class IngredientCaution(Base):
    """
    IngredientCaution database model.
    
    Represents ingredients that should be avoided or used with caution
    for specific genetic profiles.
    """
    __tablename__ = "ingredientcaution"
    
    caution_id = Column(Integer, primary_key=True)
    ingredient_name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # "Avoid" or "Use with Caution"
    risk_mechanism = Column(Text)
    affected_characteristic = Column(String)
    alternative_ingredients = Column(Text)
    
    # Relationships
    snps = relationship("SNPIngredientCautionLink", back_populates="caution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<IngredientCaution(ingredient_name='{self.ingredient_name}', category='{self.category}')>"