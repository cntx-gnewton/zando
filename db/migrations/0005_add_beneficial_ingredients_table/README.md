# Migration 0005: Add Beneficial Ingredients Views

This migration adds two critical views that were present in the original monolithic schema but needed to be ported to the new migration system:

1. `snp_beneficial_ingredients` - Provides a simplified view of beneficial ingredients based on genetic variants
2. `snp_ingredient_cautions` - Provides a simplified view of ingredients to avoid based on genetic variants

## Details

### SNP Beneficial Ingredients View

This view joins the SNP, ingredient, and SNP-ingredient link tables to provide a simplified query interface for recommended ingredients based on genetic variants. It includes:

- rsid (SNP identifier)
- gene
- genetic category
- ingredient name
- ingredient mechanism
- benefit mechanism
- recommendation strength
- evidence level

### SNP Ingredient Cautions View

This view joins the SNP, ingredient caution, and SNP-ingredient caution link tables to provide a simplified query interface for ingredients to avoid based on genetic variants. It includes:

- rsid (SNP identifier) 
- gene
- genetic category
- ingredient name
- caution category
- risk mechanism
- relationship notes
- evidence level

## Performance Optimizations

The migration also adds two indexes to improve query performance:

1. `idx_snp_ingredient_multi` - Multi-column index on SNP-ingredient relationships
2. `idx_snp_caution_multi` - Multi-column index on SNP-caution relationships

## Usage

These views are used by the application to generate ingredient recommendations and cautions based on a user's genetic profile. They simplify complex joins that would otherwise need to be repeated throughout the codebase.

## Migration Commands

To apply this migration:
```bash
python scripts/migrate.py --env cloud
```

To roll back this migration:
```bash
# Not yet implemented in the migration system
```