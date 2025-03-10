import os
import time
import uuid
import logging
import json
import pickle
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.models.analysis import Analysis
from app.core.config import settings
from app.services.dna_service import DNAService

logger = logging.getLogger(__name__)

class AnalysisService:
    """
    Service for performing genetic analysis on DNA data.
    Handles database queries, SNP matching, and data processing.
    """
    
    @staticmethod
    async def get_batch_snp_details(conn, rsids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves SNP details for multiple rsids in a single database query.
        
        Args:
            conn: Database connection
            rsids: List of rsid values to retrieve
            
        Returns:
            Dictionary mapping rsids to their details
        """
        if not rsids:
            return {}
        
        logger.info(f"Batch fetching {len(rsids)} SNP records")
        
        query = """
            SELECT snp_id, rsid, gene, risk_allele, effect, evidence_strength, category 
            FROM snp
            WHERE rsid = ANY(:rsids)
        """
        
        results = await conn.execute(text(query), {'rsids': rsids})
        results = results.fetchall()
        
        # Convert to dictionary for fast lookup
        snp_details = {}
        logging.info(f'Fetched {len(results)} SNP records {results[:15]}')
        
        for row in results:
            # Handle both tuple and attribute access formats
            try:
                # Try attribute access first (original SQLAlchemy behavior)
                rsid = row.rsid
                snp_details[rsid] = {
                    'snp_id': row.snp_id,
                    'gene': row.gene,
                    'risk_allele': row.risk_allele,
                    'effect': row.effect,
                    'evidence_strength': row.evidence_strength,
                    'category': row.category
                }
            except (AttributeError, TypeError):
                # Fall back to index-based access (for tuple results)
                # Index positions: 0=snp_id, 1=rsid, 2=gene, 3=risk_allele, 4=effect, 5=evidence_strength, 6=category
                rsid = row[1]
                snp_details[rsid] = {
                    'snp_id': row[0],
                    'gene': row[2],
                    'risk_allele': row[3],
                    'effect': row[4],
                    'evidence_strength': row[5],
                    'category': row[6]
                }
        
        logger.info(f"Found {len(snp_details)} matching SNPs in database")
        return snp_details
    
    @staticmethod
    async def get_batch_characteristics(conn, snp_ids: List[int]) -> Dict[int, List[Dict[str, Any]]]:
        """
        Fetches related skin characteristics for multiple SNP IDs in a single query.
        
        Args:
            conn: Database connection
            snp_ids: List of SNP IDs to retrieve characteristics for
            
        Returns:
            Dictionary mapping SNP IDs to lists of characteristic dictionaries
        """
        if not snp_ids:
            return {}
        
        logger.info(f"Batch fetching characteristics for {len(snp_ids)} SNPs")
        
        query = """
            SELECT scl.snp_id, c.name, c.description, scl.effect_direction, scl.evidence_strength
            FROM SNP_Characteristic_Link scl
            JOIN SkinCharacteristic c ON scl.characteristic_id = c.characteristic_id
            WHERE scl.snp_id = ANY(:snp_ids)
        """
        
        results = await conn.execute(text(query), {'snp_ids': snp_ids})
        results = results.fetchall()
        logging.info(f"Fetched {len(results)} characteristics records")
        
        # Group characteristics by SNP ID
        characteristics_by_snp = {}
        for row in results:
            try:
                # Try attribute access first (original SQLAlchemy behavior)
                snp_id = row.snp_id
                
                if snp_id not in characteristics_by_snp:
                    characteristics_by_snp[snp_id] = []
                    
                characteristics_by_snp[snp_id].append({
                    'name': row.name,
                    'description': row.description,
                    'effect_direction': row.effect_direction,
                    'evidence_strength': row.evidence_strength
                })
            except (AttributeError, TypeError):
                # Fall back to index-based access (for tuple results)
                # Index positions: 0=snp_id, 1=name, 2=description, 3=effect_direction, 4=evidence_strength
                snp_id = row[0]
                
                if snp_id not in characteristics_by_snp:
                    characteristics_by_snp[snp_id] = []
                    
                characteristics_by_snp[snp_id].append({
                    'name': row[1],
                    'description': row[2],
                    'effect_direction': row[3],
                    'evidence_strength': row[4]
                })
        
        # Log results summary
        found_snps = len(characteristics_by_snp)
        total_chars = sum(len(chars) for chars in characteristics_by_snp.values())
        logger.info(f"Found characteristics for {found_snps} SNPs, total of {total_chars} characteristics")
        
        return characteristics_by_snp
    
    @staticmethod
    async def get_batch_ingredients(conn, snp_ids: List[int]) -> Dict[int, Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]]:
        """
        Retrieves beneficial and cautionary ingredients for multiple SNP IDs in a single query.
        
        Args:
            conn: Database connection
            snp_ids: List of SNP IDs to retrieve ingredients for
            
        Returns:
            Dictionary mapping SNP IDs to tuples of (beneficial_list, caution_list)
        """
        if not snp_ids:
            return {}
        
        logger.info(f"Batch fetching ingredients for {len(snp_ids)} SNPs")
        
        # Get rsids for the given snp_ids (needed for beneficial ingredients)
        rsid_query = """
            SELECT snp_id, rsid
            FROM snp
            WHERE snp_id = ANY(:snp_ids)
        """
        result = await conn.execute(text(rsid_query), {'snp_ids': snp_ids})
        rsid_results = result.fetchall()
        logging.info(f"Fetched {len(rsid_results)} rsid mappings")
        
        # Create mapping of snp_id to rsid
        snp_to_rsid = {}
        for row in rsid_results:
            try:
                # Try attribute access first
                snp_to_rsid[row.snp_id] = row.rsid
            except (AttributeError, TypeError):
                # Fall back to index-based access
                # Index positions: 0=snp_id, 1=rsid
                snp_to_rsid[row[0]] = row[1]
        
        # Get all beneficial ingredients in one query
        beneficial_query = """
            SELECT s.snp_id, bi.ingredient_name, bi.ingredient_mechanism, 
                   bi.benefit_mechanism, bi.recommendation_strength, bi.evidence_level
            FROM snp s
            JOIN snp_beneficial_ingredients bi ON s.rsid = bi.rsid
            WHERE s.snp_id = ANY(:snp_ids)
        """
        
        # Get all cautionary ingredients in one query
        caution_query = """
            SELECT sicl.snp_id, ic.ingredient_name, ic.risk_mechanism, ic.alternative_ingredients
            FROM SNP_IngredientCaution_Link sicl
            JOIN IngredientCaution ic ON sicl.caution_id = ic.caution_id
            WHERE sicl.snp_id = ANY(:snp_ids)
        """
        
        beneficial_result = await conn.execute(text(beneficial_query), {'snp_ids': snp_ids})
        beneficial_results = beneficial_result.fetchall()
        
        caution_result = await conn.execute(text(caution_query), {'snp_ids': snp_ids})
        caution_results = caution_result.fetchall()
        
        logging.info(f"Fetched {len(beneficial_results)} beneficial ingredients and {len(caution_results)} cautions")
        
        # Initialize results dictionary
        ingredients_by_snp = {snp_id: ([], []) for snp_id in snp_ids}
        
        # Process beneficial ingredients
        for row in beneficial_results:
            try:
                # Try attribute access first
                snp_id = row.snp_id
                beneficial_list, _ = ingredients_by_snp[snp_id]
                
                beneficial_list.append({
                    'ingredient_name': row.ingredient_name,
                    'ingredient_mechanism': row.ingredient_mechanism,
                    'benefit_mechanism': row.benefit_mechanism,
                    'recommendation_strength': row.recommendation_strength,
                    'evidence_level': row.evidence_level
                })
            except (AttributeError, TypeError):
                # Fall back to index-based access
                # Index positions: 0=snp_id, 1=ingredient_name, 2=ingredient_mechanism, 
                #                  3=benefit_mechanism, 4=recommendation_strength, 5=evidence_level
                snp_id = row[0]
                beneficial_list, _ = ingredients_by_snp[snp_id]
                
                beneficial_list.append({
                    'ingredient_name': row[1],
                    'ingredient_mechanism': row[2],
                    'benefit_mechanism': row[3],
                    'recommendation_strength': row[4],
                    'evidence_level': row[5]
                })
        
        # Process cautionary ingredients
        for row in caution_results:
            try:
                # Try attribute access first
                snp_id = row.snp_id
                _, caution_list = ingredients_by_snp[snp_id]
                
                caution_list.append({
                    'ingredient_name': row.ingredient_name,
                    'risk_mechanism': row.risk_mechanism,
                    'alternative_ingredients': row.alternative_ingredients
                })
            except (AttributeError, TypeError):
                # Fall back to index-based access
                # Index positions: 0=snp_id, 1=ingredient_name, 2=risk_mechanism, 3=alternative_ingredients
                snp_id = row[0]
                _, caution_list = ingredients_by_snp[snp_id]
                
                caution_list.append({
                    'ingredient_name': row[1],
                    'risk_mechanism': row[2],
                    'alternative_ingredients': row[3]
                })
        
        # Log results
        total_beneficial = sum(len(b) for b, _ in ingredients_by_snp.values())
        total_cautions = sum(len(c) for _, c in ingredients_by_snp.values())
        logger.info(f"Found {total_beneficial} beneficial ingredients and {total_cautions} cautions across {len(snp_ids)} SNPs")
        
        return ingredients_by_snp
    
    @staticmethod
    async def get_dynamic_summary(conn, report_data: Dict[str, Any]) -> str:
        """
        Gets dynamically generated summary using the SQL summary function
        
        Args:
            conn: Database connection
            report_data: Complete report data
            
        Returns:
            Generated summary text
        """
        variants = [m['rsid'] for m in report_data.get('mutations', [])]
        variants_str = '{' + ','.join(f'"{v}"' for v in variants) + '}'
       
        query = """
        WITH genetic_results AS (
            SELECT * FROM generate_genetic_analysis_section(CAST(:variants_str AS text[]))
        )
        SELECT generate_summary_section(
            CAST(:variants_str AS text[]),
            (SELECT findings FROM genetic_results)
        );
        """
        
        try:
            # Create the SQLAlchemy text object with parameters
            sql = text(query).bindparams(variants_str=variants_str)
            
            # Execute the query
            result = await conn.execute(sql)
            
            # Try to get the scalar result
            try:
                # First try scalar() method
                summary = result.scalar()
            except (AttributeError, TypeError):
                # If that fails, try to get the first element of the first row
                # For tuple-like results
                row = result.fetchone()
                if row:
                    summary = row[0]
                else:
                    raise ValueError("No summary generated")
                    
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            summary = "Your genes reveal how your skin naturally behaves. This report guides you on how to optimize your skincare based on your genetics."
        
        return summary
    
    @staticmethod
    async def process_snp_data(parsed_snps: List[Dict[str, Any]], db: AsyncSession) -> Dict[str, Any]:
        """
        Processes SNP data and creates a complete analysis report.
        
        Args:
            parsed_snps: List of SNP dictionaries from the DNA file
            db: Database session
            
        Returns:
            Complete report data structure
        """
        logger.info(f"Assembling report data for {len(parsed_snps)} SNPs")
        start_time = time.time()
        
        # Extract rsids from parsed SNPs
        rsids = [snp['rsid'] for snp in parsed_snps]
        
        # Use the connection from the session - now awaiting it properly
        conn = await db.connection()
        
        # Use the optimized batch query to get SNP details
        logger.info("Fetching SNP details in batch")
        snp_details = await AnalysisService.get_batch_snp_details(conn, rsids)
        
        # Initialize report structure
        report = {
            'mutations': [],
            'ingredient_recommendations': {
                'prioritize': [],
                'caution': []
            }
        }
        
        # Filter SNPs that match user's risk allele
        matching_snps = []
        matching_snp_ids = []
        
        for snp in parsed_snps:
            # Skip if not in our database
            if snp['rsid'] not in snp_details:
                continue
                
            snp_detail = snp_details[snp['rsid']]
            user_alleles = [snp['allele1'].upper(), snp['allele2'].upper()]
            risk_allele = snp_detail['risk_allele'].upper()
            
            # Skip if risk allele not present
            if risk_allele not in user_alleles:
                continue
                
            # Store matching SNPs and their IDs
            matching_snps.append({
                'parsed_snp': snp,
                'snp_detail': snp_detail
            })
            matching_snp_ids.append(snp_detail['snp_id'])
        
        logger.info(f"Found {len(matching_snps)} SNPs with matching risk alleles")
        
        if not matching_snps:
            logger.info("No matching SNPs found")
            return report
        
        # Batch fetch characteristics and ingredients
        characteristics_by_snp = await AnalysisService.get_batch_characteristics(conn, matching_snp_ids)
        ingredients_by_snp = await AnalysisService.get_batch_ingredients(conn, matching_snp_ids)
        
        # Assemble the report
        for match in matching_snps:
            snp = match['parsed_snp']
            snp_detail = match['snp_detail']
            snp_id = snp_detail['snp_id']
            
            # Get characteristics
            characteristics = characteristics_by_snp.get(snp_id, [])
            
            # Create mutation entry
            mutation = {
                'gene': snp_detail['gene'],
                'rsid': snp['rsid'],
                'allele1': snp['allele1'],
                'allele2': snp['allele2'],
                'risk_allele': snp_detail['risk_allele'],
                'effect': snp_detail['effect'],
                'evidence_strength': snp_detail['evidence_strength'],
                'category': snp_detail['category'],
                'characteristics': characteristics
            }
            report['mutations'].append(mutation)
            
            # Add ingredients if available
            if snp_id in ingredients_by_snp:
                beneficials, cautions = ingredients_by_snp[snp_id]
                report['ingredient_recommendations']['prioritize'].extend(beneficials)
                report['ingredient_recommendations']['caution'].extend(cautions)
        
        # Get a dynamic summary if enough mutations found
        if len(report['mutations']) > 0:
            try:
                report['summary'] = await AnalysisService.get_dynamic_summary(conn, report)
            except Exception as e:
                logger.error(f"Error getting dynamic summary: {e}")
                report['summary'] = "Your genes reveal how your skin naturally behaves. This report guides you on how to optimize your skincare based on your genetics."
        
        # Calculate and log performance metrics
        elapsed_time = time.time() - start_time
        logger.info(f"Report assembly completed in {elapsed_time:.2f} seconds")
        logger.info(f"Report contains {len(report['mutations'])} mutations")
        logger.info(f"Report contains {len(report['ingredient_recommendations']['prioritize'])} beneficial ingredients")
        logger.info(f"Report contains {len(report['ingredient_recommendations']['caution'])} cautionary ingredients")
        
        return report
    
    @staticmethod
    def get_cached_analysis(file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis results for a given file hash.
        
        Args:
            file_hash: Hash of the DNA file
            
        Returns:
            The cached analysis data if available, None otherwise
        """
        return DNAService.load_from_cache(f"analysis_{file_hash}")
    
    @staticmethod
    def cache_analysis_results(file_hash: str, analysis_data: Dict[str, Any]) -> None:
        """
        Cache analysis results for future use.
        
        Args:
            file_hash: Hash of the DNA file
            analysis_data: Analysis results to cache
        """
        DNAService.save_to_cache(analysis_data, f"analysis_{file_hash}")
    
    @staticmethod
    async def record_analysis(db: AsyncSession, file_hash: Optional[str], analysis_data: Dict[str, Any]) -> str:
        """
        Record the analysis results in the database.
        
        Args:
            db: Database session
            file_hash: Hash of the DNA file (optional)
            analysis_data: Complete analysis results
            
        Returns:
            ID of the created analysis record
        """
        # Generate a unique ID for the analysis
        analysis_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Use raw SQL to insert the record directly
        query = """
        INSERT INTO analyses (analysis_id, file_hash, data, created_at, status)
        VALUES (:analysis_id, :file_hash, :data, :created_at, :status)
        """
        
        # Convert datetime to string
        created_at_str = now.isoformat()
        json_data = json.dumps(analysis_data)
        
        params = {
            "analysis_id": analysis_id,
            "file_hash": file_hash,
            "data": json_data,
            "created_at": created_at_str,
            "status": "completed"
        }
        
        # Debug info
        logger.info(f"Attempting to insert analysis with ID: {analysis_id}")
        logger.info(f"Parameters: file_hash={file_hash}, data_length={len(json_data)}, created_at={created_at_str}")
        
        try:
            # Try with explicit transaction control
            conn = await db.connection()
            await conn.execute(text("BEGIN"))
            
            # Execute the insert
            await conn.execute(text(query), params)
            
            # Commit the transaction
            await conn.execute(text("COMMIT"))
            
            logger.info(f"Successfully inserted analysis record with ID: {analysis_id}")
            return analysis_id
        except Exception as e:
            # Log the complete error
            logger.error(f"Error inserting analysis record: {str(e)}")
            try:
                # Try to rollback
                await conn.execute(text("ROLLBACK"))
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {str(rollback_error)}")
            
            # Try direct insertion as a fallback
            try:
                logger.info("Trying alternative insertion method...")
                direct_query = f"""
                INSERT INTO analyses (analysis_id, file_hash, status)
                VALUES ('{analysis_id}', '{file_hash}', 'completed')
                """
                await db.execute(text(direct_query))
                await db.commit()
                logger.info("Alternative insertion succeeded (without data)")
                return analysis_id
            except Exception as alt_error:
                logger.error(f"Alternative insertion failed: {str(alt_error)}")
                raise e
    
    @staticmethod
    async def get_analysis_by_id(analysis_id: str, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Retrieve analysis by ID from the database.
        
        Args:
            analysis_id: ID of the analysis
            db: Database session
            
        Returns:
            Analysis data dictionary if found, None otherwise
        """
        query = """
        SELECT analysis_id, file_hash, status, data, created_at, completed_at
        FROM analyses 
        WHERE analysis_id = :analysis_id
        """
        
        result = await db.execute(text(query), {"analysis_id": analysis_id})
        
        # Get the first row
        row = result.first()
        
        if not row:
            return None
        
        # Create a dictionary instead of an Analysis object to avoid ORM issues
        try:
            # Try attribute access first
            analysis_data = {
                "analysis_id": row.analysis_id,
                "file_hash": row.file_hash,
                "status": row.status,
                "data": json.loads(row.data) if isinstance(row.data, str) else row.data,
                "created_at": row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else row.created_at,
                "completed_at": row.completed_at.isoformat() if hasattr(row.completed_at, 'isoformat') else row.completed_at
            }
        except (AttributeError, TypeError):
            # Fall back to index-based access
            # Positions: 0=analysis_id, 1=file_hash, 2=status, 3=data, 4=created_at, 5=completed_at
            analysis_data = {
                "analysis_id": row[0],
                "file_hash": row[1],
                "status": row[2],
                "data": json.loads(row[3]) if isinstance(row[3], str) else row[3],
                "created_at": row[4].isoformat() if hasattr(row[4], 'isoformat') else row[4],
                "completed_at": row[5].isoformat() if hasattr(row[5], 'isoformat') else row[5]
            }
            
        return analysis_data
        
    @staticmethod
    async def get_all_analyses(db: AsyncSession, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Retrieve all analyses from the database with pagination.
        
        Args:
            db: Database session
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            Dictionary with items (list of analyses) and count (total number of records)
        """
        # Query to get the total count - look for all analyses
        count_query = "SELECT COUNT(*) FROM analyses"
        count_result = await db.execute(text(count_query))
        
        # Get the count value (handle both tuple and attribute access)
        try:
            total_count = count_result.scalar()
        except (AttributeError, TypeError):
            row = count_result.first()
            total_count = row[0] if row else 0
            
        # Query to get the analyses with pagination - include all analyses
        query = """
        SELECT analysis_id, file_hash, status, created_at, data
        FROM analyses 
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
        """
        
        result = await db.execute(text(query), {"limit": limit, "offset": offset})
        
        # Process the rows
        analyses = []
        for row in result:
            try:
                # Try attribute access first
                try:
                    data = json.loads(row.data) if isinstance(row.data, str) else row.data
                    # Calculate SNP count in Python
                    snp_count = len(data.get('mutations', [])) if data and isinstance(data, dict) else 0
                except (json.JSONDecodeError, AttributeError):
                    # If we can't parse the data, default to 0 snp_count
                    snp_count = 0
                    logger.warning(f"Could not parse data for analysis {row.analysis_id}")
                
                analysis = {
                    "analysis_id": row.analysis_id,
                    "file_hash": row.file_hash,
                    "status": row.status,
                    "created_at": row.created_at.isoformat() if hasattr(row.created_at, 'isoformat') else row.created_at,
                    "snp_count": snp_count
                }
            except (AttributeError, TypeError):
                # Fall back to index-based access
                # Positions: 0=analysis_id, 1=file_hash, 2=status, 3=created_at, 4=data
                try:
                    data = json.loads(row[4]) if isinstance(row[4], str) else row[4]
                    # Calculate SNP count in Python
                    snp_count = len(data.get('mutations', [])) if data and isinstance(data, dict) else 0
                except (json.JSONDecodeError, AttributeError, IndexError):
                    # If we can't parse the data, default to 0 snp_count
                    snp_count = 0
                    logger.warning(f"Could not parse data for analysis {row[0]}")
                
                analysis = {
                    "analysis_id": row[0],
                    "file_hash": row[1],
                    "status": row[2],
                    "created_at": row[3].isoformat() if hasattr(row[3], 'isoformat') else row[3],
                    "snp_count": snp_count
                }
                
            analyses.append(analysis)
            
        return {
            "items": analyses,
            "count": total_count
        }