# Database Architecture Analysis: Zando Genomic Analysis Project

## Overview

This document provides a comprehensive analysis of the PostgreSQL database architecture powering the Zando Genomic Analysis platform. It details the database schema, critical functions, optimization opportunities, and dependencies between the database and application components.

## Table of Contents

1. [Database Schema Overview](#database-schema-overview)
2. [Key Tables Analysis](#key-tables-analysis)
3. [Critical SQL Functions](#critical-sql-functions)
4. [Frontend & Backend Dependencies](#frontend--backend-dependencies)
5. [Performance Analysis](#performance-analysis)
6. [Optimization Opportunities](#optimization-opportunities)
7. [Migration Considerations](#migration-considerations)
8. [Recommended Changes](#recommended-changes)

## Database Schema Overview

The database consists of three main categories of tables:

1. **Core Genetic Data**
   - `snp`: Central table containing genetic variants (SNPs)
   - `skincharacteristic`: Skin traits affected by genetic variants
   - `skincondition`: Skin conditions related to characteristics

2. **Ingredient Data**
   - `ingredient`: Beneficial skincare ingredients
   - `ingredientcaution`: Ingredients that may be problematic for certain genetic profiles

3. **Relationship Tables**
   - `snp_characteristic_link`: Links SNPs to affected skin characteristics
   - `characteristic_condition_link`: Links characteristics to conditions
   - `snp_ingredient_link`: Links SNPs to beneficial ingredients
   - `snp_ingredientcaution_link`: Links SNPs to cautionary ingredients
   - `condition_ingredient_link`: Links conditions to recommended ingredients

Additionally, the database defines custom types and views:
- `genetic_finding`: Composite type for report generation
- `pdf_style`: Type for report formatting
- `routine_step_type`: Enum for skincare routine steps
- `snp_beneficial_ingredients`: View joining SNPs and their beneficial ingredients

## Key Tables Analysis

### SNP Table

```sql
CREATE TABLE SNP (
    snp_id SERIAL PRIMARY KEY,
    rsid VARCHAR NOT NULL UNIQUE,
    gene VARCHAR NOT NULL,
    risk_allele VARCHAR NOT NULL,
    effect TEXT,
    evidence_strength VARCHAR CHECK (evidence_strength IN ('Strong', 'Moderate', 'Weak')),
    category VARCHAR NOT NULL
);
```

**Purpose**: Stores genetic variants (Single Nucleotide Polymorphisms) with their associated genes, risk alleles, and effects.

**Critical Fields**:
- `rsid`: Unique identifier for each SNP (e.g., "rs1805007")
- `gene`: Gene symbol the SNP is associated with (e.g., "MC1R")
- `evidence_strength`: Importance/reliability of the genetic association

**Dependencies**:
- Both FastAPI and original application rely on this as the central lookup table
- The `rsid` field is used to match user DNA file data
- The `category` field enables grouping of related genetic findings in reports

### SkinCharacteristic Table

```sql
CREATE TABLE SkinCharacteristic (
    characteristic_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    measurement_method TEXT
);
```

**Purpose**: Defines skin traits that can be affected by genetic variations.

**Dependencies**:
- Used by report generation to create the "Skin Characteristics Affected" section
- Accessed by the frontend to display characteristic descriptions

### Ingredient Tables

```sql
CREATE TABLE Ingredient (
    ingredient_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL UNIQUE,
    mechanism TEXT,
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    contraindications TEXT
);

CREATE TABLE IngredientCaution (
    caution_id SERIAL PRIMARY KEY,
    ingredient_name VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    risk_mechanism TEXT,
    affected_characteristic VARCHAR,
    alternative_ingredients TEXT
);
```

**Purpose**: Store beneficial ingredients and cautionary ingredients respectively.

**Dependencies**:
- Frontend displays these as "Prioritize These" and "Approach With Caution" sections
- Used for batch ingredient recommendation processing in both applications

### Relationship Tables

```sql
CREATE TABLE SNP_Characteristic_Link (
    snp_id INTEGER REFERENCES snp(snp_id),
    characteristic_id INTEGER REFERENCES SkinCharacteristic(characteristic_id),
    effect_direction VARCHAR CHECK (effect_direction IN ('Increases', 'Decreases', 'Modulates')),
    evidence_strength VARCHAR,
    PRIMARY KEY (snp_id, characteristic_id)
);

CREATE TABLE SNP_Ingredient_Link (
    snp_id INTEGER REFERENCES snp(snp_id),
    ingredient_id INTEGER REFERENCES Ingredient(ingredient_id),
    benefit_mechanism TEXT,
    recommendation_strength VARCHAR CHECK (recommendation_strength IN ('First-line', 'Second-line', 'Supportive')),
    evidence_level VARCHAR CHECK (evidence_level IN ('Strong', 'Moderate', 'Weak')),
    PRIMARY KEY (snp_id, ingredient_id)
);
```

**Purpose**: Create many-to-many relationships between entities.

**Dependencies**:
- `SNP_Ingredient_Link.benefit_mechanism` provides the text explaining why an ingredient is recommended
- The FastAPI backend relies on these tables for batch query optimization

## Critical SQL Functions

### 1. `generate_genetic_analysis_section(text[])`

**Purpose**: Creates the detailed genetic analysis section of the report.

**Dependencies**:
- Called by both the legacy app and FastAPI backend's `process_dna.py` and `analysis_service.py`
- Returns the `genetic_finding[]` array used for subsequent report generation

```sql
CREATE OR REPLACE FUNCTION generate_genetic_analysis_section(user_variants text[])
  RETURNS TABLE(report_text text, findings genetic_finding[])
  LANGUAGE plpgsql
AS $function$
-- Function implementation
$function$;
```

### 2. `generate_summary_section(text[], genetic_finding[])`

**Purpose**: Creates the summary section of the genetic report.

**Dependencies**:
- Called as the first step in report generation by both applications
- Relies on the output of `generate_genetic_analysis_section()`

```sql
CREATE OR REPLACE FUNCTION generate_summary_section(
    user_variants text[],
    genetic_data genetic_finding[] DEFAULT NULL::genetic_finding[]
)
RETURNS text
LANGUAGE plpgsql
AS $function$
-- Function implementation
$function$;
```

### 3. `get_genetic_findings(text)`

**Purpose**: Retrieves all genetic findings associated with a specific rsID.

**Dependencies**:
- Used by `format_genetic_analysis()` to build comprehensive reports
- Returns the `genetic_finding` composite type used throughout the system

## Frontend & Backend Dependencies

### FastAPI Backend Dependencies

1. **Analysis Service**
   - Directly queries `snp`, `snp_beneficial_ingredients`, and `SNP_IngredientCaution_Link` tables
   - Uses optimized batch queries for performance
   - Depends on the database structure for caching and reporting

2. **Report Generation**
   - Uses the `generate_genetic_analysis_section` and `generate_summary_section` SQL functions
   - Depends on the structure of the `genetic_finding` type for report assembly

3. **Data Models**
   - `Analysis` model in `app/db/models/analysis.py` stores analysis results in a JSON column
   - Database structure influences what gets stored in the analysis data

### React Frontend Dependencies

1. **Ingredient Recommendations Component**
   - Displays data based on the structure of `snp_beneficial_ingredients` view
   - Expects `benefit_mechanism` to be present for explanation text

2. **Genetic Analysis Visualization**
   - Displays data based on the joined structure of `snp` and `snp_characteristic_link` tables

3. **Report Generation**
   - Depends on JSON structure from backend response, which mirrors database relationships

## Performance Analysis

### Current Database Performance Issues

1. **Multiple Independent Queries**
   - Many single-row lookups rather than batch operations
   - Separate queries for SNPs, characteristics, and ingredients

2. **Missing Indexes**
   - The `rsid` field is frequently used in joins but lacks optimal indexing
   - Missing composite indexes on frequently joined columns

3. **Heavy In-Memory Processing**
   - Most aggregation and formatting happens in application code rather than database

4. **Inefficient Joins**
   - Some queries join multiple tables sequentially rather than using optimized join patterns
   - No use of Common Table Expressions (CTEs) for complex queries

5. **No Query Caching**
   - Repeated identical queries without server-side statement caching

## Optimization Opportunities

### 1. Improved Indexing

```sql
-- Add composite indexes for frequently joined columns
CREATE INDEX idx_snp_characteristic_link_composite ON snp_characteristic_link(snp_id, characteristic_id);
CREATE INDEX idx_snp_ingredient_link_composite ON snp_ingredient_link(snp_id, ingredient_id);

-- Add indexes for frequent lookup fields
CREATE INDEX idx_ingredient_name ON ingredient(name);
CREATE INDEX idx_characteristic_name ON skincharacteristic(name);
```

### 2. Query Optimization

```sql
-- Replace multiple small queries with a single optimized query
WITH relevant_snps AS (
    SELECT snp_id, rsid, gene, risk_allele, effect, evidence_strength, category
    FROM snp
    WHERE rsid = ANY($1)  -- Use array parameter for batch lookup
),
snp_chars AS (
    SELECT 
        s.snp_id,
        json_agg(json_build_object(
            'name', sc.name,
            'description', sc.description,
            'effect_direction', scl.effect_direction
        )) as characteristics
    FROM relevant_snps s
    JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    GROUP BY s.snp_id
)
-- Complete query with ingredients...
```

### 3. Database Partitioning

For larger deployments with millions of SNPs, consider partitioning the SNP table by category or chromosome.

```sql
CREATE TABLE snp (
    snp_id SERIAL,
    rsid VARCHAR NOT NULL,
    gene VARCHAR NOT NULL,
    category VARCHAR NOT NULL,
    -- other columns
    PRIMARY KEY (snp_id, category)
) PARTITION BY LIST (category);

CREATE TABLE snp_pigmentation PARTITION OF snp FOR VALUES IN ('Pigmentation');
CREATE TABLE snp_inflammation PARTITION OF snp FOR VALUES IN ('Inflammation');
-- Additional partitions
```

### 4. Materialized Views

Create materialized views for complex, frequently-accessed joined data.

```sql
CREATE MATERIALIZED VIEW mv_snp_complete_data AS
SELECT 
    s.snp_id, s.rsid, s.gene, s.category,
    json_agg(DISTINCT jsonb_build_object(
        'name', sc.name,
        'effect_direction', scl.effect_direction
    )) as characteristics,
    -- Include ingredients
FROM snp s
LEFT JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
-- Additional joins
GROUP BY s.snp_id, s.rsid, s.gene, s.category;

-- Add refresh policy
CREATE OR REPLACE FUNCTION refresh_mv_snp_complete_data()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_snp_complete_data;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 5. Connection Pooling Optimization

The FastAPI backend already implements connection pooling, but the pool parameters can be optimized based on load testing:

```python
_engine = sqlalchemy.create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    # Optimized pool settings
    pool_size=10,            # Increased from 5
    max_overflow=15,         # Increased from 10
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)
```

## Migration Considerations

When migrating or updating the database, consider these dependencies:

1. **View Dependencies**
   - The `snp_beneficial_ingredients` view is used by both FastAPI and legacy code
   - API response structures mirror this view's output format
   
2. **Type Dependencies**
   - The `genetic_finding` composite type is used throughout the codebase
   - Any schema changes require updating both database and application code
   
3. **Function Dependencies**
   - Functions like `generate_genetic_analysis_section` and `generate_summary_section` are critical
   - Both applications call these functions directly

## Recommended Changes

### 1. Convert Report Generation Functions to PLpgSQL

Replace the complex, inefficient PL/pgSQL functions with optimized versions that use modern PostgreSQL features:

```sql
CREATE OR REPLACE FUNCTION generate_genetic_analysis_section_v2(user_variants text[])
  RETURNS TABLE(report_text text, findings json)
  LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    WITH variant_data AS (
        -- Optimized variant lookup with single scan
        SELECT 
            s.snp_id, s.rsid, s.gene, s.risk_allele, 
            s.effect, s.evidence_strength, s.category,
            -- Use JSON aggregation for nested data
            COALESCE(
                (SELECT json_agg(jsonb_build_object(
                    'name', sc.name,
                    'description', sc.description,
                    'effect_direction', scl.effect_direction
                ))
                FROM snp_characteristic_link scl
                JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
                WHERE scl.snp_id = s.snp_id),
                '[]'::json
            ) as characteristics,
            -- Include beneficial ingredients
            -- Include cautionary ingredients
        FROM snp s
        WHERE s.rsid = ANY(user_variants)
    )
    SELECT 
        -- Format report text
        -- Return JSON-formatted findings
    FROM variant_data;
END;
$function$;
```

### 2. Implement Database Migration Scripts

Create Alembic migration scripts for the FastAPI application:

```python
# migrations/versions/xxxx_add_indexes.py
def upgrade():
    op.create_index('idx_snp_rsid', 'snp', ['rsid'])
    op.create_index('idx_snp_gene', 'snp', ['gene'])
    op.create_index('idx_snp_characteristic_link_composite', 
                   'snp_characteristic_link', 
                   ['snp_id', 'characteristic_id'])
    # Additional indexes

def downgrade():
    op.drop_index('idx_snp_rsid')
    op.drop_index('idx_snp_gene')
    op.drop_index('idx_snp_characteristic_link_composite')
    # Additional index removals
```

### 3. Add Narrative Field to Ingredient Links

To better support personalized reports, add a narrative field to the ingredient link tables:

```sql
-- Add narrative field to SNP_Ingredient_Link
ALTER TABLE SNP_Ingredient_Link ADD COLUMN narrative TEXT;

-- Add narrative field to SNP_IngredientCaution_Link
ALTER TABLE SNP_IngredientCaution_Link ADD COLUMN narrative TEXT;

-- Update the view to include the new field
CREATE OR REPLACE VIEW snp_beneficial_ingredients AS
SELECT 
    s.rsid,
    s.gene,
    s.category as genetic_category,
    i.name as ingredient_name,
    i.mechanism as ingredient_mechanism,
    sil.benefit_mechanism,
    sil.recommendation_strength,
    sil.evidence_level,
    sil.narrative
FROM SNP_Ingredient_Link sil
JOIN snp s ON s.snp_id = sil.snp_id
JOIN Ingredient i ON i.ingredient_id = sil.ingredient_id
ORDER BY sil.evidence_level DESC, sil.recommendation_strength;
```

### 4. Create Database Statistics Collection Function

```sql
CREATE OR REPLACE FUNCTION get_database_statistics()
RETURNS json
LANGUAGE plpgsql
AS $$
DECLARE
    stats json;
BEGIN
    WITH table_stats AS (
        SELECT
            tables.table_schema,
            tables.table_name,
            (SELECT COUNT(*) FROM information_schema.columns 
             WHERE table_schema = tables.table_schema AND table_name = tables.table_name) AS column_count,
            pg_total_relation_size(tables.table_schema || '.' || tables.table_name) AS total_bytes,
            (SELECT COUNT(*) FROM (SELECT 1 FROM pg_namespace n
                              JOIN pg_class c ON n.oid = c.relnamespace
                              JOIN pg_index i ON c.oid = i.indrelid
                              WHERE n.nspname = tables.table_schema AND c.relname = tables.table_name) s) AS index_count,
            pg_size_pretty(pg_relation_size(tables.table_schema || '.' || tables.table_name)) AS table_size,
            pg_size_pretty(pg_total_relation_size(tables.table_schema || '.' || tables.table_name)) AS total_size
        FROM information_schema.tables
        WHERE tables.table_schema = 'public' AND tables.table_type = 'BASE TABLE'
    ),
    function_stats AS (
        SELECT count(*) as function_count FROM pg_proc WHERE pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
    ),
    record_counts AS (
        SELECT
            'snp' as table_name, (SELECT COUNT(*) FROM snp) as record_count UNION ALL
            SELECT 'skincharacteristic', (SELECT COUNT(*) FROM skincharacteristic) UNION ALL
            SELECT 'ingredient', (SELECT COUNT(*) FROM ingredient) UNION ALL
            SELECT 'snp_characteristic_link', (SELECT COUNT(*) FROM snp_characteristic_link) UNION ALL
            SELECT 'snp_ingredient_link', (SELECT COUNT(*) FROM snp_ingredient_link)
    )
    SELECT json_build_object(
        'database_size', (SELECT pg_size_pretty(pg_database_size(current_database()))),
        'table_count', (SELECT COUNT(*) FROM table_stats),
        'function_count', (SELECT function_count FROM function_stats),
        'tables', (SELECT json_agg(row_to_json(table_stats)) FROM table_stats),
        'record_counts', (SELECT json_object_agg(table_name, record_count) FROM record_counts)
    ) INTO stats;
    
    RETURN stats;
END;
$$;
```

These recommended changes will significantly improve database performance, maintainability, and support the evolving needs of both the FastAPI backend and React frontend applications.

## Conclusion

The Zando Genomic Analysis database provides a solid foundation for genetic analysis and personalized recommendations. With the optimizations suggested in this document, the system will be able to handle larger datasets, provide faster query responses, and maintain better compatibility with the evolving application architecture.

The most critical dependencies for both applications are:
1. The structure of the `snp` table and its relationships
2. The SQL functions for report generation
3. The `genetic_finding` composite type
4. The `snp_beneficial_ingredients` view for recommendation processing

Any modifications to these elements should be carefully coordinated with updates to both the FastAPI backend and the React frontend to ensure continued functionality.