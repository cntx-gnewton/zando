# CLAUDE.md - Assistant Guide for Zando Genomic Analysis Project

## Build & Run Commands
- Install dependencies: `pip install -r requirements.txt`
- Run web app: `python src/app.py`
- Process DNA file: `python src/process_dna.py <input_dna_file.txt> <output_report.pdf>`
- Generate skin report: `python src/generate_skin_report.py <input_dna_file> <output_pdf>`
- Validate DNA file: `python src/dna_validator.py <input_dna_file>`
- Docker build: `docker build -t zando .`
- Docker run: `docker run -p 8080:8080 zando`

## Project Architecture

### Frontend
- **Web Framework**: Built with Dash/Flask for interactive web applications
- **UI Components**: Uses dash-bootstrap-components for responsive design
- **Core Features**:
  - File upload interface for genomic data (.txt files)
  - Progress indicators during processing
  - Downloadable PDF reports
  - Option to generate dummy reports for testing
- **Main Files**:
  - `ALGORYTHM/src/app.py`: Web application using Dash with file upload interface
  - `ALGORYTHM/src/reports/`: Directory where PDF reports are stored

### Backend
- **Core Processing Components**:
  - DNA file parser: Extracts SNP records from 23andMe/Ancestry-style raw data files
  - Database connector: Interfaces with PostgreSQL for genetic data lookup
  - Analysis engine: Cross-references user SNPs with database to find matches
  - PDF generator: Creates personalized reports using ReportLab
- **Main Files**:
  - `ALGORYTHM/src/process_dna.py`: Core functionality for DNA processing and report generation
  - `ALGORYTHM/src/generate_skin_report.py`: Alternative report generator with simpler database connection
  - `ALGORYTHM/src/dna_validator.py`: Tool for validating DNA files with detailed analysis
  
### Database
- **Engine**: PostgreSQL database with custom functions for genetic analysis
- **Schema**:
  - `snp`: Contains genetic variants with rsID, gene, risk allele, effect, evidence strength
  - `skincharacteristic`: Skin traits that can be affected by genetic variations
  - `ingredientcaution`/`ingredient`: Active ingredients with benefits or cautions
  - `snp_characteristic_link`/`snp_ingredient_link`: Association tables linking SNPs to characteristics and ingredients
- **SQL Functions**:
  - `generate_genetic_analysis_section`: Analyzes genetic variants
  - `generate_summary_section`: Creates readable summaries from genetic findings
  - `get_ingredient_recommendations`: Fetches product recommendations based on genetics
- **Main Files**:
  - `ALGORYTHM/database/initialize.sql`: Database schema setup
  - `ALGORYTHM/database/populate.sql`: Populates database with genetic data
  
### Frontend-Backend Integration
- **Data Flow**:
  1. User uploads raw genetic data through web interface
  2. Frontend streams file data to backend parser
  3. Backend extracts SNP data and connects to database
  4. Database queries match user SNPs with known variants
  5. Backend processes matches to generate personalized recommendations
  6. PDF report is generated and stored in the reports directory
  7. Frontend provides download link for the completed report
- **API Pattern**:
  - Uses Flask route for file download functionality (`/download/<path:filename>`)
  - Dash callbacks for reactive UI updates and processing flow
- **Environment Configuration**:
  - Uses environment variables for connection settings
  - Debug mode toggle for development environments
  - Cloud SQL connector for production PostgreSQL connections

## Code Style Guidelines
- Use snake_case for variables, functions, and file names
- Group imports: standard library, third-party, local modules
- Add type hints to function signatures where possible
- Document functions with docstrings ("""Description.""")
- Follow PEP 8 standards for Python code
- Use specific exception handling (avoid bare except blocks)
- SQL: Use consistent indentation and snake_case naming
- Keep functions focused on a single responsibility
- Log errors with context (file, line, detailed message)
- Use environment variables for configuration (via dotenv)

## Database Interaction
- Database initialization: Run `database/initialize.sql`
- Database population: Run `database/populate.sql`
- Database tests: Execute SQL in `database/_Archive/tests/`
- Connection string format: `postgresql+pg8000://USER:PASSWORD@HOST/DATABASE`
- Production environment uses Google Cloud SQL Connector (see `process_dna.py`)
- Local development uses direct psycopg2/pg8000 connection