/**
 * Types related to genetic analysis
 */

// Genetic traits and characteristics
export interface GeneticCharacteristic {
  name: string;
  description: string;
  effect_direction?: string;
  evidence_strength?: string;
}

// Mutation for the GeneCard component
export interface Mutation {
  rsid: string;
  gene_name: string;
  allele: string;
  effect: string;
  evidence_level: string;
  category?: string;
}

export interface GeneticMutation {
  gene: string;
  rsid: string;
  allele1: string;
  allele2: string;
  risk_allele: string;
  effect: string;
  evidence_strength?: string;
  category?: string;
  characteristics: GeneticCharacteristic[];
}

// Ingredient recommendations
export interface IngredientRecommendation {
  name: string;
  benefit?: string;
  caution?: string;
  genes?: string[];
  evidence_level?: string;
}

export interface BeneficialIngredient {
  ingredient_name: string;
  ingredient_mechanism?: string;
  benefit_mechanism: string;
  recommendation_strength?: string;
  evidence_level?: string;
}

export interface IngredientCaution {
  ingredient_name: string;
  risk_mechanism: string;
  alternative_ingredients?: string;
}

// Analysis data structure
export interface AnalysisData {
  mutations: Mutation[];
  ingredient_recommendations: {
    beneficial: IngredientRecommendation[];
    cautionary: IngredientRecommendation[];
  };
  summary?: string;
}

// API Request and Response types
export interface AnalysisRequest {
  file_hash?: string;
  analysis_id?: string;
  raw_snp_data?: any[];
  force_refresh?: boolean;
}

export interface AnalysisResponse {
  analysis_id: string;
  status: string;
  message: string;
  snp_count: number;
  file_hash?: string;
  processing_time?: number;
  cached: boolean;
}

export interface AnalysisResult {
  analysis_id: string;
  created_at: string;
  file_hash?: string;
  data: AnalysisData;
}

// Analysis state for the application
export interface AnalysisState {
  fileHash?: string;
  fileName?: string;
  analysisId?: string;
  snpCount?: number;
  status: 'idle' | 'uploaded' | 'analyzing' | 'analyzed' | 'error';
  error?: string;
  data?: AnalysisData;
}