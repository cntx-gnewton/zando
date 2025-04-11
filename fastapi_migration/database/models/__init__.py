# Import all models here to ensure they are registered with SQLAlchemy
from .snp import SNP, SNPCharacteristicLink, SNPIngredientLink, SNPIngredientCautionLink
from .characteristic import SkinCharacteristic
from .condition import SkinCondition, CharacteristicConditionLink, ConditionIngredientLink
from .ingredient import Ingredient, IngredientCaution

# When integrating with the FastAPI backend, we'll also need to import the existing models:
# from app.db.models.user import User
# from app.db.models.dna_file import DNAFile
# from app.db.models.analysis import Analysis
# from app.db.models.report import Report