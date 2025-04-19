# CLAUDE Optimization Plan

## Performance Analysis & Optimization Roadmap

This document outlines a comprehensive plan to optimize the Zando genomic analysis application, with particular focus on the frontend-backend communication and database interaction efficiency.

## Current Bottlenecks

### 1. Database Interaction Inefficiencies

- **Multiple Independent Database Queries**: The current implementation makes separate database calls for each SNP's details, characteristics, and recommendations.
- **Inefficient Data Loading**: The entire SNP table is loaded into memory, even though only a small subset of records are actually needed.
- **Repeated Connection Establishment**: Database connections are established for each user request, adding overhead.
- **Synchronous Processing**: All database operations are performed sequentially, waiting for each to complete.

### 2. PDF Generation Overhead

- **Report Generation in Request Path**: PDF generation happens synchronously while the user waits, potentially causing timeouts with large data sets.
- **Markdown-to-PDF Conversion**: The new markdown-styled PDF generation adds processing overhead in the request path.

### 3. Frontend Experience

- **Single Callback Chain**: All processing happens in a single callback chain, blocking the UI during processing.
- **Lack of Progress Information**: Users have no visibility into the progress of report generation.

## Optimization Plan

### Phase 1: Database Interaction (High Priority)

#### 1.1 Implement Batch Database Operations
```python
# Instead of:
for snp in parsed_snps:
    snp_detail = get_snp_details(snp_df, snp['rsid'])
    characteristics = get_related_skin_characteristics(conn, snp_detail['snp_id'])
    
# Use batch operations:
def get_batch_snp_details(conn, rsids):
    query = """
        SELECT snp_id, rsid, gene, risk_allele, effect, evidence_strength, category 
        FROM snp
        WHERE rsid = ANY(:rsids)
    """
    return conn.execute(sqlalchemy.text(query), {'rsids': rsids}).fetchall()
```

#### 1.2 Create Combined Queries
```python
# Create a single query that retrieves SNPs with their characteristics and recommendations:
def get_complete_snp_data(conn, rsids):
    query = """
    WITH relevant_snps AS (
        SELECT snp_id, rsid, gene, risk_allele, effect, evidence_strength, category
        FROM snp
        WHERE rsid = ANY(:rsids)
    )
    SELECT 
        s.snp_id, s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category,
        json_agg(DISTINCT jsonb_build_object(
            'name', sc.name,
            'description', sc.description,
            'effect_direction', scl.effect_direction,
            'evidence_strength', scl.evidence_strength
        )) as characteristics,
        -- Add ingredient recommendations here
    FROM relevant_snps s
    LEFT JOIN snp_characteristic_link scl ON s.snp_id = scl.snp_id
    LEFT JOIN skincharacteristic sc ON scl.characteristic_id = sc.characteristic_id
    -- Add more joins for ingredients
    GROUP BY s.snp_id, s.rsid, s.gene, s.risk_allele, s.effect, s.evidence_strength, s.category
    """
    return conn.execute(sqlalchemy.text(query), {'rsids': rsids}).fetchall()
```

#### 1.3 Implement Connection Pooling
- Modify the connection management to use a persistent connection pool, reducing the overhead of establishing new connections for each request.
- Configure idle timeouts and max connections appropriately.

### Phase 2: Asynchronous Processing (Medium Priority)

#### 2.1 Implement Background Processing
- Move report generation to a background task
- Provide a job ID to the client for status polling

```python
# In app.py
@app.callback(
    Output('job-status', 'data'),
    Input('submit-button', 'n_clicks'),
    [...]
)
def start_report_generation(n_clicks, contents, filename, report_format):
    if n_clicks is not None and contents is not None:
        snps = parse_contents(contents, filename)
        if snps is not None:
            job_id = str(uuid.uuid4())
            # Store job in Redis or another lightweight store
            redis_client.set(f"job:{job_id}:status", "PROCESSING")
            redis_client.set(f"job:{job_id}:data", json.dumps({
                'snps': snps,
                'format': report_format
            }))
            # Start background task
            threading.Thread(target=process_report_job, args=(job_id,)).start()
            return {'job_id': job_id}
    return {'error': 'Invalid input'}

# Background processing function
def process_report_job(job_id):
    try:
        job_data = json.loads(redis_client.get(f"job:{job_id}:data"))
        snps = job_data['snps']
        report_format = job_data['format']
        
        # Process normally
        engine = connect_to_database()
        with engine.connect() as conn:
            report_data = assemble_report_data(conn, snps)
            output_file = f"/tmp/{job_id}.pdf"
            
            if report_format == 'md':
                generate_markdown(report_data, output_file, conn)
            else:
                generate_pdf(report_data, output_file, conn)
            
            # Update job status
            redis_client.set(f"job:{job_id}:status", "COMPLETED")
            redis_client.set(f"job:{job_id}:file", output_file)
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {e}")
        redis_client.set(f"job:{job_id}:status", "ERROR")
        redis_client.set(f"job:{job_id}:error", str(e))
```

#### 2.2 Add Progress Reporting
- Implement a progress tracking mechanism
- Update the UI with real-time progress information

### Phase 3: Caching and Data Optimization (Medium Priority)

#### 3.1 Implement Response Caching
- Cache report data and generated PDFs for recently processed files to avoid reprocessing the same data.
- Use a unique hash of the file contents as the cache key.

#### 3.2 Optimize Data Structures
- Review data storage and retrieval patterns
- Minimize data duplication and redundant processing

#### 3.3 Implement Partial Data Loading
- Load only the required SNP data from the database

### Phase 4: UI/UX Improvements (Lower Priority)

#### 4.1 Add Progress Indicators
- Provide detailed progress information during report generation
- Implement a multi-step progress bar

#### 4.2 Implement Parallel Processing for UI
- Use Web Workers for client-side processing where possible
- Offload heavy tasks to background threads

## Implementation Roadmap

### Immediate Actions (1-2 days)
1. Implement batch database operations (Phase 1.1)
2. Create combined SQL queries (Phase 1.2)
3. Add basic caching for generated reports

### Short-term Improvements (1-2 weeks)
1. Set up connection pooling (Phase 1.3)
2. Implement background processing (Phase 2.1)
3. Add progress tracking (Phase 2.2)

### Medium-term Enhancements (2-4 weeks)
1. Optimize data structures (Phase 3.2)
2. Implement response caching (Phase 3.1)
3. Add detailed progress indicators (Phase 4.1)

### Long-term Strategy (1-2 months)
1. Implement partial data loading (Phase 3.3)
2. Add parallel processing (Phase 4.2)
3. Comprehensive system monitoring and optimization

## Expected Performance Gains

- **Database Interaction**: 60-80% reduction in database query time
- **Report Generation**: 40-60% faster report generation
- **User Experience**: Improved responsiveness and feedback
- **Scalability**: Support for significantly more concurrent users

By implementing these optimizations, the application should be able to handle more users concurrently while providing a faster, more responsive experience.

## Detailed Execution Plan

### Phase 1: Database Optimization (Week 1)

#### Day 1-2: Batch Database Operations
1. Create new batch query functions in process_dna.py:
   ```python
   def get_batch_snp_details(conn, rsids_list)
   def get_batch_characteristics(conn, snp_ids)
   def get_batch_ingredients(conn, snp_ids)
   ```
2. Refactor `assemble_report_data()` to use these batch functions
3. Measure and document performance improvement

#### Day 3-4: Combined Query Implementation
1. Create a unified SQL query that joins SNP, characteristics, and ingredients tables
2. Implement a new function to process the combined query results
3. Update report assembly process to use the combined data
4. Test with various dataset sizes

#### Day 5: Connection Pooling Setup
1. Modify database connection code to maintain a connection pool
2. Implement connection reuse throughout the application
3. Configure proper connection timeouts and limits

### Phase 2: Asynchronous Processing (Week 2)

#### Day 1-3: Background Processing Implementation
1. Create job management system with unique IDs
2. Implement job storage mechanism (SQLite or Redis)
3. Create background worker thread system
4. Update UI to handle job status checking
5. Add job result retrieval endpoint

#### Day 4-5: Progress Reporting
1. Add progress tracking to all major processing steps
2. Create a progress endpoint for client polling
3. Implement UI elements to display progress
4. Test with large datasets to verify smooth updates

### Phase 3: Caching System (Week 3)

#### Day 1-2: Report Caching
1. Create file hashing mechanism for DNA data
2. Implement cache storage system (file-based or Redis)
3. Add cache lookup before processing
4. Implement cache insertion after processing

#### Day 3-5: Data Structure Optimization
1. Analyze current data patterns and memory usage
2. Optimize data structure for SNP storage
3. Implement improved parsing and processing algorithms
4. Reduce memory footprint during processing

### Phase 4: Polish and Long-term Improvements (Week 4+)

#### Week 4: UI Improvements
1. Implement detailed progress bar with percentage
2. Add status messages for each processing phase
3. Create cancelable job processes
4. Improve error handling and user feedback

#### Ongoing: Monitoring and Optimization
1. Add performance logging throughout the system
2. Create benchmarking tools for continuous improvement
3. Implement automatic optimization based on data patterns
4. Regular review and refinement of database queries