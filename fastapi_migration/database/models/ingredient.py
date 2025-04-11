from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Import Base from the existing session.py once integrated
# For now we'll define it here for reference
Base = declarative_base()

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
    
    # Relationships - these will be defined once all models exist
    # snps = relationship("SNPIngredientLink", back_populates="ingredient")
    # conditions = relationship("ConditionIngredientLink", back_populates="ingredient")

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
    
    # Relationships - these will be defined once all models exist
    # snps = relationship("SNPIngredientCautionLink", back_populates="caution")

    def __repr__(self):
        return f"<IngredientCaution(ingredient_name='{self.ingredient_name}', category='{self.category}')>"