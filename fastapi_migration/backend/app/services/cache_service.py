import os
import glob
import shutil
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.services.dna_service import DNAService

# Set up logging
logger = logging.getLogger(__name__)

class CacheService:
    """
    Service for managing the application's cache.
    Provides methods for inspecting, cleaning, and managing cached files.
    """
    
    @staticmethod
    def list_cache_files(format_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all files in the cache, optionally filtered by format type.
        
        Args:
            format_type: Optional filter for specific format types ('json', 'pdf', 'md', etc.)
            
        Returns:
            List of dictionaries with cache file metadata
        """
        cache_dir = Path(settings.CACHE_DIR)
        
        # Get the pattern based on format type
        if format_type:
            pattern = f"*.{format_type}"
        else:
            pattern = "*.*"
            
        # Find all matching files
        cache_files = []
        for file_path in cache_dir.glob(pattern):
            # Extract file hash from filename (remove extension)
            file_hash = file_path.stem
            
            # Get format from extension
            file_format = file_path.suffix.lstrip('.')
            
            # Get metadata for this file
            metadata = DNAService.get_cache_metadata(file_hash, file_format)
            if metadata:
                cache_files.append(metadata)
                
        # Sort by modified date (newest first)
        cache_files.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
        return cache_files
    
    @staticmethod
    def get_cache_stats() -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        cache_dir = Path(settings.CACHE_DIR)
        
        # Initialize stats
        stats = {
            'total_files': 0,
            'total_size_bytes': 0,
            'expired_files': 0,
            'formats': {},
            'oldest_file': None,
            'newest_file': None,
            'cache_directory': str(cache_dir),
            'cache_expiry_days': settings.CACHE_EXPIRY.days
        }
        
        # Get all files and their metadata
        cache_files = CacheService.list_cache_files()
        
        if not cache_files:
            return stats
            
        stats['total_files'] = len(cache_files)
        
        # Calculate other stats
        for file_meta in cache_files:
            # Add to total size
            stats['total_size_bytes'] += file_meta.get('size', 0)
            
            # Count expired files
            if file_meta.get('expired', False):
                stats['expired_files'] += 1
                
            # Track by format
            file_format = file_meta.get('format', 'unknown')
            if file_format not in stats['formats']:
                stats['formats'][file_format] = {
                    'count': 0,
                    'size_bytes': 0
                }
                
            stats['formats'][file_format]['count'] += 1
            stats['formats'][file_format]['size_bytes'] += file_meta.get('size', 0)
            
            # Track oldest/newest files
            modified_at = file_meta.get('modified_at')
            if modified_at:
                if stats['oldest_file'] is None or modified_at < stats['oldest_file']['modified_at']:
                    stats['oldest_file'] = {
                        'file_hash': file_meta.get('file_hash'),
                        'modified_at': modified_at,
                        'format': file_meta.get('format')
                    }
                    
                if stats['newest_file'] is None or modified_at > stats['newest_file']['modified_at']:
                    stats['newest_file'] = {
                        'file_hash': file_meta.get('file_hash'),
                        'modified_at': modified_at,
                        'format': file_meta.get('format')
                    }
                    
        # Calculate total size in MB
        stats['total_size_mb'] = stats['total_size_bytes'] / (1024 * 1024)
        
        return stats
    
    @staticmethod
    def clean_expired_cache() -> Dict[str, Any]:
        """
        Remove all expired cache files.
        
        Returns:
            Dictionary with cleanup results
        """
        cache_files = CacheService.list_cache_files()
        
        results = {
            'files_removed': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
        for file_meta in cache_files:
            if file_meta.get('expired', False):
                file_hash = file_meta.get('file_hash')
                file_format = file_meta.get('format')
                
                if file_hash and file_format:
                    deleted = DNAService.delete_from_cache(file_hash, file_format)
                    if deleted:
                        results['files_removed'] += 1
                        results['bytes_freed'] += file_meta.get('size', 0)
                    else:
                        results['errors'].append(f"Failed to delete {file_hash}.{file_format}")
                        
        # Convert bytes to MB
        results['mb_freed'] = results['bytes_freed'] / (1024 * 1024)
        
        return results
    
    @staticmethod
    def clean_all_cache() -> Dict[str, Any]:
        """
        Remove all cache files.
        
        Returns:
            Dictionary with cleanup results
        """
        cache_dir = Path(settings.CACHE_DIR)
        
        # Get stats before cleanup
        stats_before = CacheService.get_cache_stats()
        
        results = {
            'files_removed': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
        # First check which files actually exist to avoid error messages for non-existent files
        existing_files = list(cache_dir.glob("*.*"))
        
        # Remove all files that exist in the cache directory
        for file_path in existing_files:
            try:
                # Get file size before deletion for accurate byte count
                file_size = file_path.stat().st_size
                file_path.unlink()
                results['files_removed'] += 1
                results['bytes_freed'] += file_size
                logger.info(f"Deleted cache file: {file_path.name}")
            except Exception as e:
                logger.error(f"Error deleting cache file {file_path}: {e}")
                results['errors'].append(f"Failed to delete {file_path.name}: {str(e)}")
                
        # Convert bytes to MB
        results['mb_freed'] = results['bytes_freed'] / (1024 * 1024)
        results['total_files_before'] = stats_before['total_files']
        results['total_size_mb_before'] = stats_before.get('mb_freed', 0)
        
        return results
    
    @staticmethod
    def get_cache_for_file(file_hash: str) -> Dict[str, Any]:
        """
        Get all cache files associated with a specific file hash.
        
        Args:
            file_hash: Hash of the file content
            
        Returns:
            Dictionary with information about all cached files for this hash
        """
        cache_dir = Path(settings.CACHE_DIR)
        
        result = {
            'file_hash': file_hash,
            'cache_files': [],
            'total_files': 0,
            'total_size_bytes': 0
        }
        
        # Get all files for this hash (any extension)
        for file_path in cache_dir.glob(f"{file_hash}.*"):
            file_format = file_path.suffix.lstrip('.')
            
            # Get metadata for this file
            metadata = DNAService.get_cache_metadata(file_hash, file_format)
            if metadata:
                result['cache_files'].append(metadata)
                result['total_files'] += 1
                result['total_size_bytes'] += metadata.get('size', 0)
                
        # Sort by format for readability
        result['cache_files'].sort(key=lambda x: x.get('format', ''))
        
        # Add total size in MB
        result['total_size_mb'] = result['total_size_bytes'] / (1024 * 1024)
        
        return result
    
    @staticmethod
    def delete_cache_for_file(file_hash: str) -> Dict[str, Any]:
        """
        Delete all cache files associated with a specific file hash.
        
        Args:
            file_hash: Hash of the file content
            
        Returns:
            Dictionary with deletion results
        """
        cache_info = CacheService.get_cache_for_file(file_hash)
        
        results = {
            'file_hash': file_hash,
            'files_removed': 0,
            'bytes_freed': 0,
            'errors': []
        }
        
        # Also check for analysis files with this hash
        analysis_file_hash = f"analysis_{file_hash}"
        analysis_cache_info = CacheService.get_cache_for_file(analysis_file_hash)
        
        # Process normal cache files
        for file_meta in cache_info.get('cache_files', []):
            file_format = file_meta.get('format')
            
            if file_format:
                deleted = DNAService.delete_from_cache(file_hash, file_format)
                if deleted:
                    results['files_removed'] += 1
                    results['bytes_freed'] += file_meta.get('size', 0)
                else:
                    logger.debug(f"File {file_hash}.{file_format} not found or couldn't be deleted")
        
        # Process analysis cache files 
        for file_meta in analysis_cache_info.get('cache_files', []):
            file_format = file_meta.get('format')
            
            if file_format:
                deleted = DNAService.delete_from_cache(analysis_file_hash, file_format)
                if deleted:
                    results['files_removed'] += 1
                    results['bytes_freed'] += file_meta.get('size', 0)
                else:
                    logger.debug(f"Analysis file {analysis_file_hash}.{file_format} not found or couldn't be deleted")
                    
        # Convert bytes to MB
        results['mb_freed'] = results['bytes_freed'] / (1024 * 1024)
        
        return results