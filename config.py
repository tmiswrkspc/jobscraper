"""
Job Scraper Configuration - Serper API

This module contains configuration for the Serper API-based job scraper.
Uses Serper.dev API for clean, structured job data without CAPTCHAs.

Free tier: 2,500 searches/month
API docs: https://serper.dev/docs
"""

# ============================================================================
# SEARCH QUERIES
# ============================================================================

# Search queries targeting technology jobs in Bangalore and remote India
# Expanded to 30 queries for 3x more job discovery
SEARCH_QUERIES = [
    # Bangalore core roles (10 queries)
    "software engineer Bangalore",
    "python developer Bangalore",
    "data analyst Bangalore",
    "frontend developer Bangalore",
    "java developer Bangalore",
    "full stack developer Bangalore",
    "data scientist Bangalore",
    "devops engineer Bangalore",
    "backend developer Bangalore",
    "machine learning engineer Bangalore",
    
    # Bangalore specific technologies (5 queries)
    "django developer Bangalore",
    "react developer Bangalore",
    "nodejs developer Bangalore",
    "aws engineer Bangalore",
    "kubernetes engineer Bangalore",
    
    # Remote India positions (5 queries)
    "remote software engineer India",
    "remote python developer India",
    "remote full stack developer India",
    "work from home developer India",
    "remote backend engineer India",
    
    # Other major Indian cities (5 queries)
    "software engineer Mumbai",
    "python developer Pune",
    "full stack developer Hyderabad",
    "data scientist Delhi",
    "devops engineer Mumbai",
    
    # Experience levels (3 queries)
    "junior developer Bangalore",
    "senior software engineer Bangalore",
    "lead engineer Bangalore",
    
    # Specific domains (2 queries)
    "fintech developer Bangalore",
    "ecommerce developer Bangalore"
]

# ============================================================================
# DEDUPLICATION CONFIGURATION
# ============================================================================

# Fuzzy matching similarity threshold for title and company comparison
# Jobs with similarity > 0.9 for both title AND company are considered duplicates
FUZZY_SIMILARITY_THRESHOLD = 0.9  # 90% similarity required

# ============================================================================
# FILE PATHS
# ============================================================================

# Output directory
OUTPUT_DIR = "output"

# Output file base names (timestamps will be added)
JSON_OUTPUT_BASENAME = "jobs"
CSV_OUTPUT_BASENAME = "jobs"

# ============================================================================
# ENRICHMENT CONFIGURATION (Optional - Tavily API)
# ============================================================================

# Enable Tavily enrichment (requires TAVILY_API_KEY in .env)
ENABLE_ENRICHMENT = True

# Maximum jobs to enrich per run (to stay within API limits)
MAX_ENRICHMENT_JOBS = 10  # Tavily free tier: 1,000 requests/month
