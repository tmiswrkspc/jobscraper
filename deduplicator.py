"""
Enhanced Deduplicator Module

This module provides two-phase deduplication for job records:
1. URL-based deduplication (primary key matching)
2. Fuzzy matching deduplication (title + company similarity)

Key features:
- URL normalization (remove query params, fragments, trailing slashes)
- Fuzzy string matching using difflib (90% similarity threshold)
- Order preservation during deduplication
- Separate statistics for URL and fuzzy duplicates
"""

import logging
from difflib import SequenceMatcher
from typing import List, Dict, Tuple
from urllib.parse import urlparse, urlunparse

# Import configuration
from config import FUZZY_SIMILARITY_THRESHOLD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('Deduplicator')


def normalize_url(url: str) -> str:
    """
    Normalizes a job URL for comparison.
    Removes query parameters and fragments, lowercases domain.
    
    Args:
        url: Raw job URL
        
    Returns:
        Normalized URL string
    """
    try:
        # Parse URL into components
        parsed = urlparse(url)
        
        # Normalize domain to lowercase
        netloc = parsed.netloc.lower()
        
        # Remove query parameters and fragments
        # Keep scheme, netloc, and path only
        normalized = urlunparse((
            parsed.scheme,
            netloc,
            parsed.path.rstrip('/'),  # Remove trailing slashes
            '',  # params (empty)
            '',  # query (empty)
            ''   # fragment (empty)
        ))
        
        return normalized
        
    except Exception as e:
        logger.warning(f"Failed to normalize URL '{url}': {e}")
        # Return original URL if normalization fails
        return url.lower()



def calculate_similarity(str1: str, str2: str) -> float:
    """
    Calculates similarity ratio between two strings using difflib.
    
    Args:
        str1: First string (normalized to lowercase)
        str2: Second string (normalized to lowercase)
        
    Returns:
        Similarity ratio between 0.0 and 1.0
    """
    # Normalize strings to lowercase and strip whitespace
    str1_norm = str1.lower().strip()
    str2_norm = str2.lower().strip()
    
    # Handle empty strings
    if not str1_norm or not str2_norm:
        return 0.0
    
    # Calculate similarity using SequenceMatcher
    similarity = SequenceMatcher(None, str1_norm, str2_norm).ratio()
    
    return similarity



def fuzzy_match_job(job1: Dict, job2: Dict, threshold: float = FUZZY_SIMILARITY_THRESHOLD) -> bool:
    """
    Checks if two jobs are duplicates using fuzzy string matching.
    
    Args:
        job1: First job record dictionary
        job2: Second job record dictionary
        threshold: Similarity threshold (default from config: 0.9)
        
    Returns:
        True if title and company similarity both exceed threshold
    """
    # Extract title and company from both jobs
    title1 = job1.get("title", "")
    title2 = job2.get("title", "")
    company1 = job1.get("company", "")
    company2 = job2.get("company", "")
    
    # Calculate similarities
    title_similarity = calculate_similarity(title1, title2)
    company_similarity = calculate_similarity(company1, company2)
    
    # Both must exceed threshold to be considered duplicates
    is_duplicate = (title_similarity > threshold and company_similarity > threshold)
    
    if is_duplicate:
        logger.debug(f"Fuzzy match found: '{title1}' @ '{company1}' ≈ '{title2}' @ '{company2}' "
                    f"(title: {title_similarity:.2f}, company: {company_similarity:.2f})")
    
    return is_duplicate



def deduplicate_jobs(job_records: List[Dict]) -> Tuple[List[Dict], Dict[str, int]]:
    """
    Removes duplicate job records using URL and fuzzy matching.
    
    Two-phase deduplication:
    1. Phase 1: URL-based deduplication (normalize and compare URLs)
    2. Phase 2: Fuzzy matching deduplication (compare title + company)
    
    Args:
        job_records: List of job record dictionaries
        
    Returns:
        Tuple of (unique_job_records, dedup_stats)
        dedup_stats contains counts: {"url_duplicates": N, "fuzzy_duplicates": M}
    """
    if not job_records:
        logger.info("No job records to deduplicate")
        return [], {"url_duplicates": 0, "fuzzy_duplicates": 0}
    
    logger.info(f"Starting deduplication of {len(job_records)} job records...")
    
    # Statistics tracking
    url_duplicates = 0
    fuzzy_duplicates = 0
    
    # ========================================================================
    # PHASE 1: URL-based deduplication
    # ========================================================================
    
    seen_urls = {}  # Map normalized URL to first occurrence
    url_deduplicated = []
    
    for job in job_records:
        job_url = job.get("link", "")
        
        if not job_url:
            # Skip jobs without URLs
            continue
        
        # Normalize URL
        normalized_url = normalize_url(job_url)
        
        # Check if URL already seen
        if normalized_url in seen_urls:
            url_duplicates += 1
            logger.debug(f"URL duplicate: {job_url}")
        else:
            # First occurrence - add to results
            seen_urls[normalized_url] = job
            url_deduplicated.append(job)
    
    logger.info(f"Phase 1 (URL): Removed {url_duplicates} duplicates, "
               f"{len(url_deduplicated)} unique jobs remaining")
    
    # ========================================================================
    # PHASE 2: Fuzzy matching deduplication
    # ========================================================================
    
    unique_jobs = []
    
    for job in url_deduplicated:
        is_duplicate = False
        
        # Compare with all previously added unique jobs
        for unique_job in unique_jobs:
            if fuzzy_match_job(job, unique_job):
                is_duplicate = True
                fuzzy_duplicates += 1
                break
        
        # If not a duplicate, add to unique list
        if not is_duplicate:
            unique_jobs.append(job)
    
    logger.info(f"Phase 2 (Fuzzy): Removed {fuzzy_duplicates} duplicates, "
               f"{len(unique_jobs)} unique jobs remaining")
    
    # ========================================================================
    # Summary
    # ========================================================================
    
    total_duplicates = url_duplicates + fuzzy_duplicates
    logger.info(f"Deduplication complete: {len(job_records)} → {len(unique_jobs)} "
               f"({total_duplicates} duplicates removed)")
    
    dedup_stats = {
        "url_duplicates": url_duplicates,
        "fuzzy_duplicates": fuzzy_duplicates
    }
    
    return unique_jobs, dedup_stats

