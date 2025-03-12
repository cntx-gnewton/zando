/**
 * Types related to DNA data and processing
 */

export interface SNPID {
  rsid: string;
}

export interface SNP extends SNPID {
  chromosome: string;
  position: string;
  allele1: string;
  allele2: string;
}

export interface DNAFileUploadResponse {
  file_name: string;
  file_hash: string;
  file_size: number;
  upload_date: string;
  status: string;
  snp_count?: number;
  processing_time?: number;
  message?: string;
  cached: boolean;
  format?: string;
}

export interface ValidationStatistics {
  alleles?: Record<string, number>;
  rsid_patterns?: Record<string, number>;
}

export interface ValidationResult {
  valid: boolean;
  format?: string;
  snp_count: number;
  chromosomes: Record<string, number>;
  statistics: ValidationStatistics;
  errors: string[];
}

export interface DNAFile {
  id?: number;
  file_hash: string;
  filename: string;
  file_format?: string;
  snp_count?: number;
  status: string;
  created_at?: string;
}

export interface ValidatedFile extends DNAFile {
  validation: ValidationResult;
}

export interface DNAUploadProgress {
  uploaded: boolean;
  progress: number;
  validated: boolean;
  processed: boolean;
  error?: string;
}

export interface FileFormat {
  name: string;
  description: string;
  columns?: string[];
  example?: string;
  example_line?: string;
  file_pattern?: string;
  support_level: 'full' | 'partial' | 'experimental';
}