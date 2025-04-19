# Zando Database Refactoring Plan

## Project Overview

Zando is a genomic analysis application that processes DNA data (SNPs) to provide personalized skin characteristics analysis and ingredient recommendations. The system was originally a monolithic Flask/Dash application and has been migrated to a modern architecture with:

- **Backend**: FastAPI with asynchronous processing capabilities
- **Frontend**: React with TypeScript
- **Database**: PostgreSQL hosted on Google Cloud SQL
- **Deployment**: Google Cloud Run for the backend, Google Cloud Storage for the frontend

The core functionality revolves around analyzing genetic variants (SNPs) to determine their impact on skin characteristics and providing customized skincare ingredient recommendations based on a user's genetic profile.

## Current Database Structure

The database is currently defined using two monolithic SQL scripts:

1. **initialize.sql**: Contains all table definitions, types, views, and functions
2. **populate.sql**: Contains all the seed data for reference tables

The database includes several key tables:

- **SNP**: Genetic variants with rsID, gene, allele, and effect details
- **SkinCharacteristic**: Skin traits affected by genetic variations
- **SkinCondition**: Specific skin conditions linked to characteristics
- **Ingredient/IngredientCaution**: Beneficial and cautionary ingredients
- **Association tables**: Linking SNPs to characteristics and ingredients

## Current API-Database Interaction

The FastAPI backend interacts with the database through:

1. **Session Management**:
   - Uses Google Cloud SQL connector for production deployments
   - Implements connection pooling for performance
   - Provides both sync and async database session interfaces

2. **Data Access**:
   - Use of raw SQL queries for SNP, characteristic, and ingredient data
   - SQLAlchemy ORM models for user data, DNA files, analysis results, and reports
   - Multi-level caching for reference data to minimize database queries

3. **Key Services**:
   - **DNAService**: Handles file processing, validation, and caching
   - **AnalysisService**: Performs genetic analysis using cached SNP data
   - **ReportService**: Generates personalized recommendations

4. **API Endpoints**:
   - `/dna` endpoints for file uploads and management
   - `/analysis` endpoints for genetic analysis
   - `/reports` endpoints for generating PDF reports

## Limitations of Current Approach

1. **Schema Maintenance**:
   - No versioning or migration tracking
   - Changes require manual SQL updates across multiple files
   - Difficult to understand table relationships without extensive SQL knowledge

2. **Data Management**:
   - Monolithic seed file makes targeted updates difficult
   - No separation between different types of reference data
   - Risk of data inconsistency during updates

3. **Code Organization**:
   - Disconnect between SQL schema and Python code
   - Inconsistent approach (ORM for new tables, raw SQL for reference tables)
   - Limited type checking and validation for database operations

## Refactoring Goals

1. Create a structured, maintainable database layer with:
   - Clear schema definitions using SQLAlchemy models
   - Version-controlled migrations using Alembic
   - Organized seed data separated by domain

2. Preserve existing functionality:
   - Maintain compatibility with Google Cloud SQL
   - Preserve the effective caching mechanisms
   - Keep the hybrid async/sync database session approach

3. Improve developer experience:
   - Make schema changes trackable and reversible
   - Enable modular updates to reference data
   - Provide better type checking and IDE support

## Implementation Plan

### Phase 1: Setup Migration Framework (Days 1-2)

1. **Create Directory Structure**
   - Set up database subdirectories for models, migrations, and seed data
   - Initialize Alembic for migration management

2. **Configure Alembic**
   - Set up Alembic to work with the existing database connection
   - Configure environment for both development and production
   - Create initial migration from existing schema

### Phase 2: Convert Schema to Models (Days 3-7)

1. **Create Core Reference Models**

   ```python
   # database/models/genomic.py
   from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
   from sqlalchemy.orm import relationship
   
   from app.db.session import Base
   
   class SNP(Base):
       __tablename__ = "snp"
       
       snp_id = Column(Integer, primary_key=True)
       rsid = Column(String, nullable=False, index=True)
       gene = Column(String, nullable=False)
       risk_allele = Column(String, nullable=False)
       effect = Column(Text)
       evidence_strength = Column(String)
       category = Column(String, nullable=False)
       
       # Relationships
       characteristics = relationship("SNPCharacteristicLink", back_populates="snp")
       ingredients = relationship("SNPIngredientLink", back_populates="snp")
       cautions = relationship("SNPIngredientCautionLink", back_populates="snp")
   ```

2. **Create Association Models**

   ```python
   # database/models/associations.py
   from sqlalchemy import Column, Integer, String, Text, ForeignKey
   from sqlalchemy.orm import relationship
   
   from app.db.session import Base
   
   class SNPCharacteristicLink(Base):
       __tablename__ = "snp_characteristic_link"
       
       snp_id = Column(Integer, ForeignKey("snp.snp_id"), primary_key=True)
       characteristic_id = Column(Integer, ForeignKey("skincharacteristic.characteristic_id"), primary_key=True)
       effect_direction = Column(String)
       evidence_strength = Column(String)
       
       # Relationships
       snp = relationship("SNP", back_populates="characteristics")
       characteristic = relationship("SkinCharacteristic", back_populates="snps")
   ```

3. **Create View and Function Models**
   - Define SQLAlchemy models for database views
   - Document SQL functions for reference

### Phase 3: Organize Seed Data (Days 8-10)

1. **Create Seed Data Modules**

   ```python
   # database/seed_data/snps.py
   def get_snps():
       return [
           {
               "rsid": "rs1805007",
               "gene": "MC1R",
               "risk_allele": "T",
               "effect": "Associated with red hair, fair skin, and UV sensitivity",
               "evidence_strength": "Strong",
               "category": "Pigmentation"
           },
           # Add more SNPs here
       ]
   ```

2. **Develop Seeding Script**

   ```python
   # database/seed.py
   import logging
   from sqlalchemy.orm import Session
   from app.db.session import get_db_engine
   from database.models.genomic import SNP, SkinCharacteristic
   from database.seed_data.snps import get_snps
   
   logger = logging.getLogger(__name__)
   
   def seed_database():
       """Seed the database with reference data"""
       engine = get_db_engine()
       
       with Session(engine) as session:
           # Seed SNPs
           for snp_data in get_snps():
               snp = SNP(**snp_data)
               session.add(snp)
           
           # Seed other data...
           
           session.commit()
           logger.info("Database seeded successfully")
   ```

### Phase 4: Integration with Existing Services (Days 11-14)

1. **Update Analysis Service**
   - Gradually replace raw SQL queries with SQLAlchemy queries
   - Maintain existing caching mechanisms

2. **Create Helper Functions**
   - Develop reusable query functions
   - Add type annotations for better IDE support

3. **Update API Endpoints**
   - Ensure all endpoints use the new database access methods
   - Add transaction management for multi-step operations

### Phase 5: Testing and Documentation (Days 15-17)

1. **Create Database Tests**
   - Test model definitions
   - Test migrations
   - Test seed data integrity

2. **Document Database Structure**
   - Create comprehensive documentation of models and relationships
   - Document migration and seeding processes

3. **Create Developer Guidelines**
   - How to make schema changes
   - How to update reference data
   - How to run migrations

## Migration Strategy

For the transition from the current SQL-based schema to the SQLAlchemy ORM approach:

1. **Generate Initial Schema**
   - Use Alembic's "autogenerate" feature to create migration from existing database
   - Review and adjust the generated migration to ensure accuracy

2. **Test in Development**
   - Apply migrations to a development database
   - Verify all tables, views, and functions work correctly
   - Seed with test data and validate integrity

3. **Gradual Service Updates**
   - Update one service at a time to use the new models
   - Start with less critical services to minimize risk
   - Keep the existing raw SQL queries as fallback

4. **Production Deployment**
   - First deploy the new code without schema changes
   - Then apply schema migrations during a maintenance window
   - Roll back capability if issues arise

## Benefits of Refactored Approach

1. **Improved Maintainability**
   - Clear model definitions show table structure and relationships
   - Version-controlled schema changes
   - Modular seed data organization

2. **Better Developer Experience**
   - Type checking and IDE auto-completion
   - Consistent approach across the codebase
   - Easier onboarding for new developers

3. **Enhanced Reliability**
   - Migration tracking prevents schema drift
   - Validation at the model level
   - Clearer transaction boundaries

4. **Future Extensibility**
   - Easy to add new tables and relationships
   - Clear path for database schema evolution
   - Better support for automated testing

## Conclusion

This database refactoring plan addresses the current limitations while preserving the strengths of the existing implementation. By moving to a SQLAlchemy ORM approach with Alembic migrations, we can maintain the high performance of the current system while making it significantly more maintainable and extensible for the future.

The modular approach allows for incremental updates, minimizing risk while progressively improving the codebase. The end result will be a database layer that is easier to work with, better documented, and more robust against schema inconsistencies.