# Database Functions Migration (0004)

This migration adds a comprehensive set of PostgreSQL functions to enhance the database capabilities for the Zando Genomic Analysis application.

## Function Categories

### Utility Functions

- `update_timestamp()`: Trigger function to automatically update timestamp columns
- `generate_prefixed_uuid(prefix)`: Generates a UUID with a custom prefix
- `hash_password(password)`: Securely hashes passwords using bcrypt
- `verify_password(password, hash)`: Verifies a password against a stored hash

### Search Functions

- `search_snps(search_term)`: Full-text search for SNPs by rsid, gene, or effect
- `search_characteristics(search_term)`: Full-text search for skin characteristics
- `search_ingredients(search_term)`: Full-text search for ingredients by name or mechanism
- `global_search(search_term)`: Cross-entity search that returns results from all tables

### Analysis Functions

- `get_snp_characteristics(snp_rsid)`: Returns all characteristics related to a SNP
- `get_snp_beneficial_ingredients(snp_rsid)`: Returns beneficial ingredients for a SNP
- `get_snp_caution_ingredients(snp_rsid)`: Returns ingredients to be cautious with for a SNP
- `get_characteristic_conditions(characteristic_name)`: Returns conditions related to a characteristic

### Reporting Functions

- `generate_analysis_summary(user_id, file_id, rsids)`: Generates a comprehensive analysis in JSON format
- `generate_ingredient_recommendations(rsids)`: Creates prioritized ingredient recommendations based on SNPs
- `generate_ingredient_cautions(rsids)`: Creates a list of cautions for ingredients based on SNPs

### User Management Functions

- `register_user(email, password, first_name, last_name)`: Creates a new user account
- `authenticate_user(email, password)`: Authenticates a user and returns account details
- `log_user_action(user_id, action_type, entity_type, entity_id, ip, agent, details)`: Logs user actions for audit

## Technical Implementation

### Security Features

- Password hashing uses bcrypt via the pgcrypto extension
- Audit logging captures user actions with timestamps and IP addresses
- User authentication is handled within the database for consistency

### Performance Considerations

- Full-text search functions use PostgreSQL's GIN indexes and tsvector columns
- Analysis functions use optimized joins with proper sorting
- Result sets are structured for efficient client-side processing

### Extensions Required

- pgcrypto: For secure password hashing
- uuid-ossp: For UUID generation

## Usage Examples

### Search Example
```sql
-- Search for SNPs related to "melanin"
SELECT * FROM search_snps('melanin');

-- Global search across all entities
SELECT * FROM global_search('vitamin C');
```

### Analysis Example
```sql
-- Get all characteristics for a specific SNP
SELECT * FROM get_snp_characteristics('rs1805007');

-- Get ingredient recommendations for multiple SNPs
SELECT * FROM generate_ingredient_recommendations(ARRAY['rs1805007', 'rs2228479']);
```

### User Management Example
```sql
-- Register a new user
SELECT register_user('user@example.com', 'secure_password', 'John', 'Doe');

-- Authenticate a user
SELECT * FROM authenticate_user('user@example.com', 'secure_password');
```

## Maintenance and Extensibility

These functions are designed to be maintainable and extensible. To add new functionality:

1. Follow the existing patterns for input validation and error handling
2. Maintain consistent return types for similar functions
3. Document the new functions in this README
4. Add appropriate down migration entries for clean removal