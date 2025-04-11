# Database Script Analysis for Zando Genomic Analysis Project

## Overview of Key Database Files

The Zando genomic analysis project uses PostgreSQL for data storage with several key SQL scripts managing the schema, data loading, and functionality.

### 1. initialize.sql
- **Primary Schema Definition**: Creates core tables, views, types, and functions
- **Size**: Several thousand lines of SQL definitions
- **Key Components**:
  - Database types (genetic_finding, pdf_style, etc.)
  - Core table definitions (SNP, Ingredient, SkinCharacteristic, etc.)
  - Linking/junction tables for relationships
  - View definitions for simplified data access
  - Database functions for analysis and processing

### 2. populate.sql
- **Reference Data**: Contains INSERT statements for core database tables
- **Purpose**: Loads initial reference data for genetic variants, ingredients, etc.
- **Pattern**: Uses TRUNCATE then INSERT for idempotent loading

### 3. complete_backup.sql
- **Full Database Dump**: Contains complete schema and data
- **Usage**: Reference for port to migration system

### 4. test.sql
- **Testing Queries**: Used for verifying database functionality
- **Purpose**: Developer tool for debugging and testing

## Core Database Tables

1. **SNP**: Genetic variants with rsID, gene, risk allele, etc.
   - Primary fields: snp_id, rsid, gene, risk_allele, effect, evidence_strength, category

2. **SkinCharacteristic**: Different skin traits/qualities
   - Primary fields: characteristic_id, name, description, measurement_method

3. **Ingredient**: Skincare ingredients with benefits
   - Primary fields: ingredient_id, name, mechanism, evidence_level, contraindications

4. **IngredientCaution**: Potentially problematic ingredients
   - Primary fields: caution_id, ingredient_name, category, risk_mechanism, affected_characteristic, alternative_ingredients

5. **SkinCondition**: Different skin conditions/issues
   - Primary fields: condition_id, name, description, severity_scale

## Relationship Tables

1. **SNP_Characteristic_Link**: Connects SNPs to skin characteristics
   - Fields: snp_id, characteristic_id, effect_direction, evidence_strength

2. **SNP_Ingredient_Link**: Links SNPs to beneficial ingredients
   - Fields: snp_id, ingredient_id, benefit_mechanism, recommendation_strength, evidence_level

3. **SNP_IngredientCaution_Link**: Links SNPs to cautionary ingredients
   - Fields: snp_id, caution_id, relationship_notes, evidence_level

4. **Characteristic_Condition_Link**: Connects skin traits to conditions
   - Fields: characteristic_id, condition_id, relationship_type

5. **Condition_Ingredient_Link**: Links conditions to recommended ingredients
   - Fields: condition_id, ingredient_id, recommendation_strength, guidance_notes

## Key Views

1. **snp_beneficial_ingredients**: Critical view for ingredient recommendations
   ```sql
   CREATE VIEW public.snp_beneficial_ingredients AS
   SELECT 
       s.rsid,
       s.gene,
       s.category AS genetic_category,
       i.name AS ingredient_name,
       i.mechanism AS ingredient_mechanism,
       sil.benefit_mechanism,
       sil.recommendation_strength,
       sil.evidence_level
   FROM public.snp_ingredient_link sil
   JOIN public.snp s ON s.snp_id = sil.snp_id
   JOIN public.ingredient i ON i.ingredient_id = sil.ingredient_id
   ORDER BY sil.evidence_level DESC, sil.recommendation_strength;
   ```

2. **snp_ingredient_cautions**: View for ingredients to avoid
3. **comprehensive_recommendations**: Combined recommendation view
4. **product_recommendations**: Product-specific recommendations

## Database Functions

The database includes numerous functions for:
1. Data analysis (analyze_genetic_risks, calculate_ingredient_score)
2. Report generation (generate_skincare_report, format_genetic_summary)
3. Recommendations (get_recommended_ingredients, get_ingredients_to_avoid)
4. Data processing (get_genetic_findings, process_dna_file)

## Migration Strategy

When implementing the `snp_beneficial_ingredients` view:
1. Create a new migration (0005_add_beneficial_ingredients_table)
2. Implement the view definition matching the original
3. Add supporting index for performance
4. Provide rollback capability (down.sql)
5. Ensure integration with the existing migration framework