"""
SQLAlchemy models for SNP and related association tables.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from . import Base

class SNP(Base):
    """
    SNP (Single Nucleotide Polymorphism) database model.
    
    Represents genetic variants with their associated genes,
    risk alleles, and effects.
    """
    __tablename__ = "snp"
    
    snp_id = Column(Integer, primary_key=True)
    rsid = Column(String, nullable=False, index=True)
    gene = Column(String, nullable=False)
    risk_allele = Column(String, nullable=False)
    effect = Column(Text)
    evidence_strength = Column(String)
    category = Column(String, nullable=False)
    
    # Relationships
    characteristics = relationship("SNPCharacteristicLink", back_populates="snp", cascade="all, delete-orphan")
    ingredients = relationship("SNPIngredientLink", back_populates="snp", cascade="all, delete-orphan")
    cautions = relationship("SNPIngredientCautionLink", back_populates="snp", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SNP(rsid='{self.rsid}', gene='{self.gene}')>"


class SNPCharacteristicLink(Base):
    """
    Association table linking SNPs to skin characteristics.
    
    Describes the relationship between genetic variants and 
    their effects on skin characteristics.
    """
    __tablename__ = "snp_characteristic_link"
    
    snp_id = Column(Integer, ForeignKey("snp.snp_id"), primary_key=True)
    characteristic_id = Column(Integer, ForeignKey("skincharacteristic.characteristic_id"), primary_key=True)
    effect_direction = Column(String)
    evidence_strength = Column(String)
    
    # Relationships
    snp = relationship("SNP", back_populates="characteristics")
    characteristic = relationship("SkinCharacteristic", back_populates="snps")

    def __repr__(self):
        return f"<SNPCharacteristicLink(snp_id={self.snp_id}, characteristic_id={self.characteristic_id})>"


class SNPIngredientLink(Base):
    """
    Association table linking SNPs to beneficial ingredients.
    
    Describes which ingredients are beneficial for specific genetic variants.
    """
    __tablename__ = "snp_ingredient_link"
    
    snp_id = Column(Integer, ForeignKey("snp.snp_id"), primary_key=True)
    ingredient_id = Column(Integer, ForeignKey("ingredient.ingredient_id"), primary_key=True)
    benefit_mechanism = Column(Text)
    recommendation_strength = Column(String)
    evidence_level = Column(String)
    
    # Relationships
    snp = relationship("SNP", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="snps")

    def __repr__(self):
        return f"<SNPIngredientLink(snp_id={self.snp_id}, ingredient_id={self.ingredient_id})>"


class SNPIngredientCautionLink(Base):
    """
    Association table linking SNPs to ingredients that should be avoided.
    
    Describes which ingredients may be problematic for specific genetic variants.
    """
    __tablename__ = "snp_ingredientcaution_link"
    
    snp_id = Column(Integer, ForeignKey("snp.snp_id"), primary_key=True)
    caution_id = Column(Integer, ForeignKey("ingredientcaution.caution_id"), primary_key=True)
    evidence_level = Column(String)
    notes = Column(Text)
    
    # Relationships
    snp = relationship("SNP", back_populates="cautions")
    caution = relationship("IngredientCaution", back_populates="snps")

    def __repr__(self):
        return f"<SNPIngredientCautionLink(snp_id={self.snp_id}, caution_id={self.caution_id})>"