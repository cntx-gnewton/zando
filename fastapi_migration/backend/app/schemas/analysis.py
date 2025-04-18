from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

# Analysis request schemas
class AnalysisRequest(BaseModel):
    file_hash: Optional[str] = None
    analysis_id: Optional[str] = None
    raw_snp_data: Optional[List[Dict[str, Any]]] = None
    force_refresh: bool = False

# Analysis response schemas
class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    message: str
    snp_count: int = 0
    file_hash: Optional[str] = None
    processing_time: Optional[float] = None
    cached: bool = False

class AnalysisResult(BaseModel):
    analysis_id: str
    created_at: Union[datetime, str]
    file_hash: Optional[str] = None
    data: Dict[str, Any]
    
    class Config:
        from_attributes = True

class AnalysisSummary(BaseModel):
    analysis_id: str
    file_hash: Optional[str] = None
    created_at: Union[datetime, str]
    status: str
    snp_count: int = 0
    
    class Config:
        from_attributes = True
        
class AnalysisList(BaseModel):
    items: List[AnalysisSummary]
    count: int

# Genetic structure schemas
class GeneticCharacteristic(BaseModel):
    name: str
    description: str
    effect_direction: Optional[str] = None
    evidence_strength: Optional[str] = None

class BeneficialIngredient(BaseModel):
    ingredient_name: str
    ingredient_mechanism: Optional[str] = None
    benefit_mechanism: str
    recommendation_strength: Optional[str] = None
    evidence_level: Optional[str] = None

class IngredientCaution(BaseModel):
    ingredient_name: str
    risk_mechanism: str
    alternative_ingredients: Optional[str] = None

class IngredientRecommendations(BaseModel):
    prioritize: List[BeneficialIngredient] = []
    caution: List[IngredientCaution] = []

class GeneticMutation(BaseModel):
    gene: str
    rsid: str
    allele1: str
    allele2: str
    risk_allele: str
    effect: str
    evidence_strength: Optional[str] = None
    category: Optional[str] = None
    characteristics: List[GeneticCharacteristic] = []

class AnalysisData(BaseModel):
    mutations: List[GeneticMutation] = []
    ingredient_recommendations: IngredientRecommendations
    summary: Optional[str] = None