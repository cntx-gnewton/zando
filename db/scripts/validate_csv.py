#!/usr/bin/env python3
import csv
import re
import argparse
import os
import sys

# Schema definitions for different table CSVs
SCHEMAS = {
    'snps': {
        'rsid': {
            'required': True,
            'pattern': r'^rs\d+$',
            'description': 'Reference SNP ID'
        },
        'gene': {
            'required': True,
            'description': 'Gene symbol'
        },
        'risk_allele': {
            'required': True,
            'pattern': r'^[ATGC]$',
            'description': 'Risk allele (A, T, G, C)'
        },
        'effect': {
            'required': True,
            'description': 'Description of effect'
        },
        'evidence_strength': {
            'required': True,
            'type': 'enum',
            'allowed': ['Strong', 'Moderate', 'Weak'],
            'description': 'Evidence strength'
        },
        'category': {
            'required': True,
            'description': 'Functional category'
        }
    },
    'characteristics': {
        'name': {
            'required': True,
            'description': 'Characteristic name'
        },
        'description': {
            'required': True,
            'description': 'Detailed description'
        },
        'measurement_method': {
            'required': False,
            'description': 'How this characteristic is measured'
        }
    },
    'ingredients': {
        'name': {
            'required': True,
            'description': 'Ingredient name'
        },
        'mechanism': {
            'required': True,
            'description': 'Mechanism of action'
        },
        'evidence_level': {
            'required': True,
            'type': 'enum',
            'allowed': ['Strong', 'Moderate', 'Weak'],
            'description': 'Evidence level'
        },
        'contraindications': {
            'required': False,
            'description': 'Contraindications'
        }
    },
    'ingredient_cautions': {
        'ingredient_name': {
            'required': True,
            'description': 'Ingredient name'
        },
        'category': {
            'required': True,
            'description': 'Caution category'
        },
        'risk_mechanism': {
            'required': True,
            'description': 'Risk mechanism'
        },
        'affected_characteristic': {
            'required': False,
            'description': 'Affected characteristic'
        },
        'alternative_ingredients': {
            'required': False,
            'description': 'Alternative ingredients'
        }
    },
    'skin_conditions': {
        'name': {
            'required': True,
            'description': 'Condition name'
        },
        'description': {
            'required': True,
            'description': 'Condition description'
        },
        'severity_scale': {
            'required': True,
            'description': 'Severity scale'
        }
    },
    'snp_characteristic': {
        'rsid': {
            'required': True,
            'pattern': r'^rs\d+$',
            'description': 'Reference SNP ID'
        },
        'characteristic_name': {
            'required': True,
            'description': 'Characteristic name'
        },
        'effect_direction': {
            'required': True,
            'type': 'enum',
            'allowed': ['Increases', 'Decreases', 'Modulates'],
            'description': 'Effect direction'
        },
        'evidence_strength': {
            'required': True,
            'type': 'enum',
            'allowed': ['Strong', 'Moderate', 'Weak'],
            'description': 'Evidence strength'
        }
    },
    'snp_ingredient': {
        'rsid': {
            'required': True,
            'pattern': r'^rs\d+$',
            'description': 'Reference SNP ID'
        },
        'ingredient_name': {
            'required': True,
            'description': 'Ingredient name'
        },
        'benefit_mechanism': {
            'required': True,
            'description': 'Benefit mechanism'
        },
        'recommendation_strength': {
            'required': True,
            'type': 'enum',
            'allowed': ['First-line', 'Second-line', 'Supportive', 'Adjuvant'],
            'description': 'Recommendation strength'
        },
        'evidence_level': {
            'required': True,
            'type': 'enum',
            'allowed': ['Strong', 'Moderate', 'Weak'],
            'description': 'Evidence level'
        }
    },
    'snp_ingredientcaution': {
        'rsid': {
            'required': True,
            'pattern': r'^rs\d+$',
            'description': 'Reference SNP ID'
        },
        'ingredient_name': {
            'required': True,
            'description': 'Ingredient name'
        },
        'relationship_notes': {
            'required': True,
            'description': 'Relationship notes'
        },
        'evidence_level': {
            'required': True,
            'type': 'enum',
            'allowed': ['Strong', 'Moderate', 'Weak'],
            'description': 'Evidence level'
        }
    },
    'characteristic_condition': {
        'characteristic_name': {
            'required': True,
            'description': 'Characteristic name'
        },
        'condition_name': {
            'required': True,
            'description': 'Condition name'
        },
        'relationship_type': {
            'required': True,
            'type': 'enum',
            'allowed': ['Primary Factor', 'Contributing Factor'],
            'description': 'Relationship type'
        }
    },
    'condition_ingredient': {
        'condition_name': {
            'required': True,
            'description': 'Condition name'
        },
        'ingredient_name': {
            'required': True,
            'description': 'Ingredient name'
        },
        'recommendation_strength': {
            'required': True,
            'type': 'enum',
            'allowed': ['First-line', 'Second-line', 'Supportive', 'Adjuvant'],
            'description': 'Recommendation strength'
        },
        'guidance_notes': {
            'required': True,
            'description': 'Guidance notes'
        }
    }
}

def validate_csv_data(csv_file, schema):
    """
    Validate CSV data against a schema definition.
    
    Args:
        csv_file (str): Path to CSV file
        schema (dict): Schema definition with column types and constraints
        
    Returns:
        list: List of validation errors or empty list if valid
    """
    errors = []
    
    try:
        with open(csv_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            
            # Validate header
            required_fields = schema.keys()
            missing_fields = [field for field in required_fields 
                             if field not in reader.fieldnames]
            if missing_fields:
                errors.append(f"Missing required fields: {', '.join(missing_fields)}")
            
            # Validate rows
            for i, row in enumerate(reader, start=2):  # Start at line 2 (after header)
                for field, constraints in schema.items():
                    if field not in row:
                        continue
                        
                    value = row[field]
                    
                    # Check required
                    if constraints.get('required', False) and not value:
                        errors.append(f"Line {i}: Required field '{field}' is empty")
                    
                    # Check type
                    if value and 'type' in constraints:
                        field_type = constraints['type']
                        
                        if field_type == 'integer':
                            if not value.isdigit():
                                errors.append(f"Line {i}: Field '{field}' must be an integer")
                                
                        elif field_type == 'decimal':
                            try:
                                float(value)
                            except ValueError:
                                errors.append(f"Line {i}: Field '{field}' must be a number")
                                
                        elif field_type == 'enum':
                            allowed = constraints.get('allowed', [])
                            if value not in allowed:
                                errors.append(f"Line {i}: Field '{field}' must be one of: {', '.join(allowed)}")
                    
                    # Check pattern
                    if value and 'pattern' in constraints:
                        pattern = constraints['pattern']
                        if not re.match(pattern, value):
                            errors.append(f"Line {i}: Field '{field}' does not match pattern {pattern}")
    except FileNotFoundError:
        errors.append(f"File not found: {csv_file}")
    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")
    
    return errors

def main():
    parser = argparse.ArgumentParser(description="Validate CSV data files")
    parser.add_argument('csv_file', help='CSV file to validate')
    parser.add_argument('--schema', help='Schema to use (default: auto-detect from filename)')
    args = parser.parse_args()
    
    # Auto-detect schema from filename
    if not args.schema:
        basename = os.path.basename(args.csv_file)
        if basename.startswith('snp') and '_' not in basename:
            args.schema = 'snps'
        elif basename.startswith('characteristic') and '_' not in basename:
            args.schema = 'characteristics'
        elif basename == 'ingredients.csv':
            args.schema = 'ingredients'
        elif basename == 'ingredient_cautions.csv':
            args.schema = 'ingredient_cautions'
        elif basename == 'skin_conditions.csv':
            args.schema = 'skin_conditions'
        elif basename == 'snp_characteristic.csv':
            args.schema = 'snp_characteristic'  
        elif basename == 'snp_ingredient.csv':
            args.schema = 'snp_ingredient'
        elif basename == 'snp_ingredientcaution.csv':
            args.schema = 'snp_ingredientcaution'
        elif basename == 'characteristic_condition.csv':
            args.schema = 'characteristic_condition'
        elif basename == 'condition_ingredient.csv':
            args.schema = 'condition_ingredient'
        else:
            print(f"Could not auto-detect schema for {basename}. Please specify with --schema.")
            sys.exit(1)
    
    # Ensure schema exists
    if args.schema not in SCHEMAS:
        print(f"Unknown schema: {args.schema}")
        print(f"Available schemas: {', '.join(SCHEMAS.keys())}")
        sys.exit(1)
    
    # Validate the file
    errors = validate_csv_data(args.csv_file, SCHEMAS[args.schema])
    
    if errors:
        print(f"Validation failed with {len(errors)} errors:")
        for error in errors:
            print(f"- {error}")
        sys.exit(1)
    else:
        print(f"Validation successful: {args.csv_file} matches {args.schema} schema")

if __name__ == "__main__":
    main()