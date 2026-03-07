"""
Configuration constants for Indeed Job Scraper.

This module contains all configurable parameters for the scraper including
search queries, timing delays, pagination settings, CSS selectors, and output paths.
"""

# Search Queries
# List of job search queries to execute
SEARCH_QUERIES = [
    "software engineer Bangalore",
    "python developer Bangalore",
    "data analyst Bangalore",
    "frontend developer Bangalore",
    "java developer Bangalore",
    "full stack developer Bangalore",
    "remote software engineer India",
    "data scientist Bangalore"
]

# Delay Ranges (seconds)
# Random delays between actions to mimic human behavior
# Increased delays to reduce CAPTCHA detection (more human-like)
MIN_DELAY = 30  # Increased from 8 to 30 seconds
MAX_DELAY = 60  # Increased from 18 to 60 seconds

# Pagination Parameters
MAX_PAGES = 2  # Reduced from 4 to 2 pages to avoid detection (can increase later)
RESULTS_PER_PAGE = 50  # Indeed shows 50 results per page
START_VALUES = [0, 50, 100, 150]  # Pagination start parameters

# Timeout Values (milliseconds)
PAGE_LOAD_TIMEOUT = 90000  # Increased to 90 seconds for slower connections

# CSS Selectors
# Verified March 2026
SELECTORS = {
    # Job card container - primary and fallback selectors
    'job_card': [
        'div.job_seen_beacon',  # Primary - Verified March 2026
        'div.cardOutline',      # Fallback 1
        'div.tapItem',          # Fallback 2
        '[data-testid="slider_item"]'  # Fallback 3
    ],
    
    # Job title selectors
    'title': [
        'h2.jobTitle span',     # Primary - Verified March 2026
        'h2.jobTitle',          # Fallback 1
        '[data-testid="jobTitle"]'  # Fallback 2
    ],
    
    # Company name selectors
    'company': [
        'span[data-testid="company-name"]',  # Primary - Verified March 2026
        'span.companyName'      # Fallback
    ],
    
    # Location selectors
    'location': [
        '[data-testid="text-location"]',  # Primary - Verified March 2026
        'div.companyLocation'   # Fallback
    ],
    
    # Salary selectors
    'salary': [
        '[data-testid="salaryOnly"]',  # Primary - Verified March 2026
        'div.salary-snippet-container',  # Fallback 1
        'div.salary-snippet'    # Fallback 2
    ],
    
    # Posted date selectors
    'posted': [
        'span[data-testid="myJobsStateDate"]',  # Primary - Verified March 2026
        'span.date'             # Fallback
    ],
    
    # Job link selectors (extract href from anchor tag)
    'link': [
        'a.jcs-JobTitle',       # Primary - Verified March 2026
        'h2 a'                  # Fallback - anchor inside h2
    ],
    
    # Job description snippet selectors
    'snippet': [
        'div.job-snippet',      # Primary - Verified March 2026
        '[data-testid="job-snippet"]'  # Fallback
    ]
}

# CAPTCHA Detection
# Selectors and keywords for detecting CAPTCHA challenges
CAPTCHA_SELECTORS = [
    '#recaptcha',
    '.g-recaptcha',
    '#captcha'
]

CAPTCHA_KEYWORDS = [
    'captcha',
    'robot',
    'verify'
]

# Output Paths
OUTPUT_DIR = 'output'
CHECKPOINT_DIR = 'checkpoints'
INTERMEDIATE_RESULTS_FILENAME = 'intermediate_results.json'
CHECKPOINT_FILENAME = 'session_checkpoint.json'

# Browser Configuration
LOCALE = 'en-IN'
TIMEZONE = 'Asia/Kolkata'
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# Resource Blocking Patterns
# Block these resource types to reduce bandwidth and detection surface
BLOCKED_RESOURCE_TYPES = ['image', 'font']

# Block requests to these domains/patterns
BLOCKED_URL_PATTERNS = [
    '*google-analytics.com*',
    '*doubleclick.net*',
    '*facebook.com/tr*',
    '*analytics*',
    '*tracking*'
]

# Anti-Detection Parameters
SCROLL_CHUNK_MIN = 100  # Minimum pixels per scroll chunk
SCROLL_CHUNK_MAX = 300  # Maximum pixels per scroll chunk
SCROLL_DELAY_MIN = 0.1  # Minimum delay between scroll chunks (seconds)
SCROLL_DELAY_MAX = 0.3  # Maximum delay between scroll chunks (seconds)
SCROLL_UP_PROBABILITY = 0.1  # 10% chance to scroll up slightly

MOUSE_MOVEMENT_POINTS_MIN = 3  # Minimum random mouse movement points
MOUSE_MOVEMENT_POINTS_MAX = 7  # Maximum random mouse movement points

# Error Handling
CONSECUTIVE_CAPTCHA_THRESHOLD = 3  # Log critical warning after this many consecutive CAPTCHAs
ERROR_RATE_THRESHOLD = 0.5  # Log warning if error rate exceeds 50%
SELECTOR_FAILURE_THRESHOLD = 0.3  # Log critical warning if selector failure rate exceeds 30%
