import os
import hashlib
import time
import logging
import pickle
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.models.dna_file import DNAFile
from app.core.config import settings

logger = logging.getLogger(__name__)

# Create cache directory if it doesn't exist
os.makedirs(settings.CACHE_DIR, exist_ok=True)

class DNAService:
    """
    Service for handling DNA file operations including parsing, validation,
    and storage.
    """
    
    @staticmethod
    def compute_file_hash_from_content(content: bytes) -> str:
        """
        Compute a hash of file content for cache lookup and identification.
        
        Args:
            content: The binary content of the DNA file
            
        Returns:
            str: A hex digest hash of the content
        """
        hash_obj = hashlib.sha256(content)
        return hash_obj.hexdigest()
    
    @staticmethod
    def compute_file_hash_from_path(filepath: str) -> str:
        """
        Compute a hash of a file for cache lookup.
        
        Args:
            filepath: Path to the file
            
        Returns:
            str: A hex digest hash of the file content
        """
        hash_obj = hashlib.sha256()
        with open(filepath, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    
    @staticmethod
    def get_cache_path(file_hash: str, format_type: str = 'json') -> Path:
        """
        Get the path to a cache file for the given hash.
        
        Args:
            file_hash: Hash of the file content
            format_type: Type of cache file ('json', 'pdf', 'md')
            
        Returns:
            Path: Path object for the cache file
        """
        # Handle analysis_ prefix if it's in the file_hash
        if file_hash.startswith('analysis_'):
            return Path(settings.CACHE_DIR) / f"{file_hash}.{format_type}"
        else:
            return Path(settings.CACHE_DIR) / f"{file_hash}.{format_type}"
    
    @staticmethod
    def save_to_cache(data: Any, file_hash: str, format_type: str = 'json') -> None:
        """
        Save data to the cache.
        
        Args:
            data: Data to cache (dict for 'json', bytes for 'pdf'/'md')
            file_hash: Hash of the file content
            format_type: Type of data being cached ('json', 'pdf', 'md')
        """
        cache_path = DNAService.get_cache_path(file_hash, format_type)
        
        if format_type == 'json':
            # Save metadata with the cache
            cache_data = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'hash': file_hash
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
        else:
            # Binary data (PDF, etc.)
            with open(cache_path, 'wb') as f:
                f.write(data)
        
        logger.info(f"Saved {format_type} cache file: {cache_path}")
    
    @staticmethod
    def load_from_cache(file_hash: str, format_type: str = 'json') -> Optional[Any]:
        """
        Load data from the cache if available and not expired.
        
        Args:
            file_hash: Hash of the file content
            format_type: Type of data to load ('json', 'pdf', 'md')
            
        Returns:
            The cached data if available and not expired, None otherwise
        """
        cache_path = DNAService.get_cache_path(file_hash, format_type)
        
        if not cache_path.exists():
            return None
            
        # Check if cache is expired
        file_age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
        if file_age > settings.CACHE_EXPIRY:
            logger.info(f"Cache expired ({file_age.days} days old): {cache_path}")
            cache_path.unlink(missing_ok=True)
            return None
        
        if format_type == 'json':
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                logger.info(f"Loaded cache from {cache_path}, created at {cache_data['timestamp']}")
                return cache_data['data']
            except (pickle.PickleError, KeyError, EOFError) as e:
                logger.warning(f"Error loading cache: {e}")
                cache_path.unlink(missing_ok=True)
                return None
        else:
            # Binary data (PDF, etc.)
            try:
                with open(cache_path, 'rb') as f:
                    data = f.read()
                logger.info(f"Loaded {format_type} from cache: {cache_path}")
                return data
            except IOError as e:
                logger.warning(f"Error loading {format_type} cache: {e}")
                cache_path.unlink(missing_ok=True)
                return None
                
    @staticmethod
    def get_cache_metadata(file_hash: str, format_type: str = 'json') -> Optional[Dict[str, Any]]:
        """
        Get metadata about a cached file without loading the full data.
        
        Args:
            file_hash: Hash of the file content
            format_type: Type of cached data ('json', 'pdf', 'md')
            
        Returns:
            Dictionary with cache metadata if available, None otherwise
        """
        cache_path = DNAService.get_cache_path(file_hash, format_type)
        
        if not cache_path.exists():
            return None
        
        # Get file stats
        stats = cache_path.stat()
        file_age = datetime.now() - datetime.fromtimestamp(stats.st_mtime)
        is_expired = file_age > settings.CACHE_EXPIRY
        
        if format_type == 'json':
            try:
                # For JSON, try to get the timestamp from the cached data
                with open(cache_path, 'rb') as f:
                    # Just load the header without the full data
                    cache_data = pickle.load(f)
                
                return {
                    'file_hash': file_hash,
                    'format': format_type,
                    'size': stats.st_size,
                    'created_at': cache_data.get('timestamp'),
                    'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    'age_days': file_age.days,
                    'expired': is_expired,
                    'path': str(cache_path)
                }
            except Exception as e:
                logger.warning(f"Error reading cache metadata: {e}")
        
        # For non-JSON files or if JSON reading failed
        return {
            'file_hash': file_hash,
            'format': format_type,
            'size': stats.st_size,
            'modified_at': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'age_days': file_age.days,
            'expired': is_expired,
            'path': str(cache_path)
        }
    
    @staticmethod
    def delete_from_cache(file_hash: str, format_type: str = 'json') -> bool:
        """
        Delete a specific item from the cache.
        
        Args:
            file_hash: Hash of the file content
            format_type: Type of cached data ('json', 'pdf', 'md')
            
        Returns:
            True if file was deleted, False otherwise
        """
        cache_path = DNAService.get_cache_path(file_hash, format_type)
        
        if cache_path.exists():
            try:
                cache_path.unlink()
                logger.info(f"Deleted cache file: {cache_path}")
                return True
            except Exception as e:
                logger.warning(f"Error deleting cache file {cache_path}: {e}")
                return False
        
        return False
    
    @staticmethod
    def check_file_cache(file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Check if a file has been processed before and is in the cache.
        
        Args:
            file_hash: Hash of the file content
            
        Returns:
            Dict with cache metadata if available, None otherwise
        """
        cached_data = DNAService.load_from_cache(file_hash)
        if cached_data is not None:
            return {
                "snp_count": len(cached_data),
                "cached": True
            }
        return None
    
    @staticmethod
    def verify_dna_file_format(filepath: str) -> List[str]:
        """
        Verify if a file is a valid DNA file and identify its format.
        
        Args:
            filepath: Path to the file to check
            
        Returns:
            List of column names if valid, empty list otherwise
        """
        # Check if the file exists
        if not os.path.isfile(filepath):
            raise FileNotFoundError("The file does not exist")
    
        # Define possible sets of valid columns
        valid_columns_set1 = ['rsid', 'chromosome', 'position', 'allele1', 'allele2']
        valid_columns_set2 = ['rsid', 'chromosome', 'position', 'genotype']
    
        # Read the first 100 lines of the file
        with open(filepath, 'r') as file:
            for i, line in enumerate(file):
                if i >= 100:
                    break
                # Check if all valid columns from set 1 are in the line
                if all(column in line for column in valid_columns_set1):
                    return valid_columns_set1
                # Check if all valid columns from set 2 are in the line
                if all(column in line for column in valid_columns_set2):
                    return valid_columns_set2
    
        return []
    
    @staticmethod
    def read_dna_file(filepath: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Reads and parses a DNA file, with optional caching.
        
        Args:
            filepath: Path to the DNA file
            use_cache: Whether to use/update cache (default: True)
            
        Returns:
            List of dictionaries with SNP data
        """
        # Check for cached version if caching is enabled
        if use_cache:
            file_hash = DNAService.compute_file_hash_from_path(filepath)
            cached_data = DNAService.load_from_cache(file_hash)
            if cached_data is not None:
                logger.info(f"Using cached SNP data for {filepath}")
                return cached_data
        
        # No cache hit or caching disabled, parse the file
        logger.info(f"Parsing DNA file: {filepath}")
        start_time = time.time()
        
        columns = DNAService.verify_dna_file_format(filepath)
        if not columns:
            raise ValueError("The file does not contain the expected columns")
    
        # Read the data into a DataFrame
        df = pd.read_csv(filepath, sep='\t', comment='#', names=columns, dtype=str)
    
        # If the file contains a genotype column, split it into allele1 and allele2
        if 'genotype' in df.columns:
            df[['allele1', 'allele2']] = df['genotype'].apply(lambda x: pd.Series(list(x)))
            df.drop(columns=['genotype'], inplace=True)
        
        # Convert to records
        parsed_data = df.to_dict(orient='records')
        
        elapsed_time = time.time() - start_time
        logger.info(f"Parsed {len(parsed_data)} SNP records from {filepath} in {elapsed_time:.2f}s")
        
        # Cache the parsed data if caching is enabled
        if use_cache:
            file_hash = DNAService.compute_file_hash_from_path(filepath)
            DNAService.save_to_cache(parsed_data, file_hash)
            logger.info(f"Cached parsed SNP data for {filepath}")
        
        return parsed_data
    
    @staticmethod
    def validate_dna_analysis(filepath: str) -> Dict[str, Any]:
        """
        Perform detailed validation and analysis of a DNA file.
        
        Args:
            filepath: Path to the DNA file
            
        Returns:
            Dictionary with validation results and statistics
        """
        try:
            # Check the file format
            columns = DNAService.verify_dna_file_format(filepath)
            format_valid = len(columns) > 0
            
            if not format_valid:
                return {
                    "valid": False,
                    "format": "unknown",
                    "snp_count": 0,
                    "chromosomes": {},
                    "statistics": {},
                    "errors": ["Unrecognized file format"]
                }
            
            # Determine the format name
            format_name = "AncestryDNA" if 'allele1' in columns else "23andMe"
            
            # Parse the file
            snps = DNAService.read_dna_file(filepath, use_cache=False)
            
            # Collect statistics
            chromosome_counts = {}
            allele_stats = {'A': 0, 'T': 0, 'G': 0, 'C': 0, 'other': 0}
            rsid_patterns = {}
            errors = []
            
            # Analyze SNPs
            for snp in snps:
                # Count by chromosome
                chrom = snp.get('chromosome', 'unknown')
                chromosome_counts[chrom] = chromosome_counts.get(chrom, 0) + 1
                
                # Count alleles
                for allele in [snp.get('allele1', ''), snp.get('allele2', '')]:
                    if allele in allele_stats:
                        allele_stats[allele] += 1
                    else:
                        allele_stats['other'] += 1
                
                # Check rsID pattern (should start with 'rs')
                rsid = snp.get('rsid', '')
                if rsid.startswith('rs'):
                    rsid_patterns['rs'] = rsid_patterns.get('rs', 0) + 1
                else:
                    rsid_patterns['other'] = rsid_patterns.get('other', 0) + 1
            
            # Check for potential errors
            if len(snps) < 10000:
                errors.append("Low SNP count - file may be incomplete")
            
            if rsid_patterns.get('other', 0) > rsid_patterns.get('rs', 0) * 0.1:
                errors.append("Unusual number of non-standard rsIDs")
            
            # Compile the validation results
            return {
                "valid": True,
                "format": format_name,
                "snp_count": len(snps),
                "chromosomes": chromosome_counts,
                "statistics": {
                    "alleles": allele_stats,
                    "rsid_patterns": rsid_patterns
                },
                "errors": errors
            }
            
        except Exception as e:
            return {
                "valid": False,
                "format": "unknown",
                "snp_count": 0,
                "chromosomes": {},
                "statistics": {},
                "errors": [str(e)]
            }
    
    @staticmethod
    async def record_file_upload(db: AsyncSession, filename: str, file_hash: str, snp_count: int) -> DNAFile:
        """
        Record a DNA file upload in the database.
        
        Args:
            db: Database session
            filename: Original filename
            file_hash: Hash of the file content
            snp_count: Number of SNPs in the file
            
        Returns:
            The created DNAFile record
        """
        # Create a new DNA file record
        dna_file = DNAFile(
            file_hash=file_hash,
            filename=filename,
            snp_count=snp_count,
            status="processed"
        )
        
        # Add and commit to database
        db.add(dna_file)
        await db.commit()
        await db.refresh(dna_file)
        
        return dna_file
    
    @staticmethod
    async def get_snp_data_by_hash(file_hash: str, db: AsyncSession) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve SNP data by file hash, either from cache or database.
        
        Args:
            file_hash: Hash of the file content
            db: Database session
            
        Returns:
            List of SNP dictionaries if found, None otherwise
        """
        # First check cache
        cached_data = DNAService.load_from_cache(file_hash)
        if cached_data is not None:
            logger.info(f"Found SNP data in main cache for hash: {file_hash}")
            return cached_data
        
        # Check in uploads directory
        uploads_dir = Path(settings.UPLOADS_DIR)
        uploads_cache_dir = Path(settings.UPLOADS_CACHE_DIR)
        
        # Check for files with hash prefix (using the way we store files in upload_dna_file)
        potential_files = list(uploads_dir.glob(f"{file_hash[:8]}_*.txt"))
        potential_cache_files = list(uploads_cache_dir.glob(f"{file_hash[:8]}_*.txt"))
        
        # Combine all potential files to check
        all_potential_files = potential_files + potential_cache_files
        
        if all_potential_files:
            logger.info(f"Found {len(all_potential_files)} potential DNA files for hash prefix {file_hash[:8]}")
            
            # Check each file to find an exact hash match
            for file_path in all_potential_files:
                try:
                    # Compute hash of this file
                    file_actual_hash = DNAService.compute_file_hash_from_path(str(file_path))
                    logger.info(f"Checking file {file_path.name}: computed hash = {file_actual_hash}")
                    
                    # If hash matches what we're looking for
                    if file_actual_hash == file_hash:
                        logger.info(f"Found exact hash match in file: {file_path}")
                        # Parse and cache the file
                        snp_data = DNAService.read_dna_file(str(file_path), use_cache=True)
                        logger.info(f"Successfully parsed file with {len(snp_data)} SNP records")
                        return snp_data
                except Exception as e:
                    logger.error(f"Error processing potential file {file_path}: {str(e)}")
                    continue
        
        # If not found in uploads, check database
        try:
            result = await db.execute(
                text("SELECT * FROM dna_files WHERE file_hash = :file_hash"),
                {"file_hash": file_hash}
            )
            dna_file = result.first()
            
            if dna_file and hasattr(dna_file, 'file_path') and dna_file.file_path:
                if os.path.exists(dna_file.file_path):
                    logger.info(f"Found DNA file in database: {dna_file.file_path}")
                    # For synchronous operations in async functions, we don't need to await them
                    return DNAService.read_dna_file(dna_file.file_path, use_cache=True)
        except Exception as e:
            logger.error(f"Error querying database for DNA file: {str(e)}")
        
        logger.warning(f"No SNP data found for hash: {file_hash}")
        return None