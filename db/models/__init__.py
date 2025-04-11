"""
SQLAlchemy models for the Zando database.

This module imports all models to ensure they're registered with SQLAlchemy.
"""

from sqlalchemy.ext.declarative import declarative_base

# Base class for all models
Base = declarative_base()

# Import all models so they're registered with SQLAlchemy
from .snp import SNP, SNPCharacteristicLink, SNPIngredientLink, SNPIngredientCautionLink
from .characteristic import SkinCharacteristic
from .condition import SkinCondition, CharacteristicConditionLink, ConditionIngredientLink
from .ingredient import Ingredient, IngredientCaution

# Make all models available at the module level
__all__ = [
    'Base',
    'SNP',
    'SNPCharacteristicLink',
    'SNPIngredientLink',
    'SNPIngredientCautionLink',
    'SkinCharacteristic',
    'SkinCondition',
    'CharacteristicConditionLink',
    'ConditionIngredientLink',
    'Ingredient',
    'IngredientCaution',
]