# Comprehensive Project Analysis Report

## 1. PROJECT OVERVIEW

### What does this project do?
This is a Job Preparation Intelligence Platform (currently in Phase 1) that scrapes job listings from Google for Jobs using the Serper.dev API. The system collects, deduplicates, and exports job data to help candidates discover technology job opportunities in India.

### Target User/Purpose
- **Primary Users**: Job seekers in India's technology sector, particularly in Bangalore
- **Secondary Users**: Recruiters, market researchers, career counselors
- **Use Cases**:
  - Automated job discovery and aggregation
  - Market research and salary trend analysis
  - Career planning and skill gap identification
  - Recruitment intelligence

### Problem It Solves
1. **Manual Job Search Fatigue**: Eliminates need to manually check multiple job sites
2. **Data Fragmentation**: Aggregates jobs from multiple sources into single dataset
3. **Duplicate Listings**: Removes duplicate job postings across platforms
4. **Data Format Inconsistency**: Standardizes job data into consistent JSON/CSV format
5. **CAPTCHA Barriers**: Uses API-based approach to avoid browser detection and CAPTCHAs

### Future Vision
The project aims to evolve into a complete Job Preparation Intelligence Platform that provides:
- Detailed skills analysis for each job
- Real-world responsibility breakdowns
- Project portfolio recommendations with GitHub examples
- Personalized learning paths
- Interview preparation materials

---

## 2. TECH STACK

### Languages
- **Python 3.12.2** (detected from venv)
  - Minimum requirement: Python 3.8+
  - Uses type hints (typing module)
  - Modern f-string formatting

### Core Dependencies

From requirements.txt:
- **requests==2.31.0** - HTTP library for API calls
- **python-dotenv>=1.0.0** - Environment variable management

### Standard Library Modules Used
- **logging** - Comprehensive logging system
- **json** - JSON data serialization
- **csv** - CSV export functionality
- **datetime** - Timestamp generation
- **typing** - Type hints (List, Dict, Tuple, Optional)
- **pathlib** - Modern file path handling
- **difflib** - Fuzzy string matching (SequenceMatcher)
- **urllib.parse** - URL parsing and normalization
- **os** - Environment variable access

### External Services
- **Serper.dev API** - Google for Jobs data provider
  - Free tier: 2,500 searches/month
  - Endpoints: /search and /jobs
  - Authentication: API key via X-API-KEY header

### Build Tools
- **pip** - Package management
- **venv** - Virtual environment (Python 3.12)
- No build tools (interpreted Python)
- No bundlers or compilers

### Testing Frameworks
- **None currently active** (pytest was removed during migration)
- Test file exists: test_api.py (manual testing script)
- Previous version had: pytest, hypothesis (property-based testing)

### Linting/Formatting Tools
- **None configured**
- Code follows PEP 8 conventions manually
- No pre-commit hooks
- No CI/CD pipeline

---

## 3. FOLDER STRUCTURE

```
indeed-job-scraper/
├── Core Application Files (5 Python files)
│   ├── scraper.py              # Main orchestrator, entry point
│   ├── serper_api.py           # Serper API client wrapper
│   ├── deduplicator.py         # Two-phase deduplication logic
│   ├── config.py               # Configuration constants
│   └── test_api.py             # Manual API test script
│
├── Configuration Files (3 files)
│   ├── .env                    # API key (SERPER_API_KEY)
│   ├── .gitignore              # Git ignore rules
│   └── requirements.txt        # Python dependencies (2 packages)
│
├── Documentation (9 markdown files)
│   ├── README.md               # Main documentation
│   ├── QUICKSTART.md           # 5-minute setup guide
│   ├── USAGE_EXAMPLES.md       # Code examples and patterns
│   ├── SERPER_WORKFLOW_PLAN.md # Detailed technical workflow
│   ├── CHANGELOG.md            # Version history
│   ├── MIGRATION_SUMMARY.md    # Browser → API migration details
│   ├── PROJECT_OVERVIEW.md     # High-level project summary
│   ├── CURRENT_IMPROVEMENTS.md # Immediate enhancement roadmap
│   └── FUTURE_UPDATES.md       # Long-term vision and phases
│
├── Output Directory (auto-created)
│   └── output/
│       ├── jobs_*.json         # Timestamped JSON exports
│       └── jobs_*.csv          # Timestamped CSV exports
│
├── Python Cache (auto-generated)
│   └── __pycache__/            # Compiled Python bytecode
│
├── Virtual Environment
│   └── venv/                   # Python 3.12 virtual environment
│
└── Version Control
    └── .git/                   # Git repository
```

### Module Responsibilities

**scraper.py** (Main Orchestrator)
- Entry point (main() function)
- SerperJobScraper class - coordinates entire workflow
- Query execution loop
- Result export (JSON/CSV)
- Summary statistics and logging

**serper_api.py** (API Client)
- SerperAPI class - handles all API communication
- Two endpoint strategies: /jobs (primary), /search (fallback)
- Response normalization to standard format
- Company/title extraction from search results
- Job result validation and filtering

**deduplicator.py** (Data Cleaning)
- Two-phase deduplication algorithm
- Phase 1: URL-based (normalize and compare)
- Phase 2: Fuzzy matching (title + company similarity)
- URL normalization (remove params, fragments)
- Similarity calculation using difflib

**config.py** (Configuration)
- Search queries list (8 default queries)
- Deduplication threshold (0.9 = 90% similarity)
- Output directory paths
- File naming patterns

**test_api.py** (Testing)
- Manual API connectivity test
- Single query execution
- Sample result display
- Configuration validation

### File Naming Patterns
- **Python modules**: lowercase_with_underscores.py
- **Classes**: PascalCase (SerperJobScraper, SerperAPI)
- **Functions**: lowercase_with_underscores()
- **Constants**: UPPERCASE_WITH_UNDERSCORES
- **Output files**: {type}_{timestamp}.{ext} (e.g., jobs_20260309_143052.json)
- **Documentation**: UPPERCASE.md or PascalCase.md

---

## 4. ARCHITECTURE & DATA FLOW

### System Structure
**Architecture Type**: Monolithic Python application
- Single-process execution
- Synchronous API calls
- No microservices
- No database (file-based storage)
- Stateless (no session management)

### Data Flow Diagram
```
User runs scraper.py
        ↓
SerperJobScraper.__init__()
        ↓
Load config.py (SEARCH_QUERIES)
        ↓
Check API key (.env → SERPER_API_KEY)
        ↓
FOR EACH query in SEARCH_QUERIES:
    ↓
    SerperAPI.search_jobs(query, location)
        ↓
        Try: POST /jobs endpoint
        ↓
        If fails: POST /search endpoint (fallback)
        ↓
        Normalize response → standard format
        ↓
        Return List[Dict] of jobs
    ↓
    Append to all_jobs list
        ↓
END FOR
        ↓
deduplicate_jobs(all_jobs)
    ↓
    Phase 1: URL deduplication
    ↓
    Phase 2: Fuzzy matching
    ↓
    Return (unique_jobs, stats)
        ↓
export_results(unique_jobs)
    ↓
    Write JSON file (output/jobs_{timestamp}.json)
    ↓
    Write CSV file (output/jobs_{timestamp}.csv)
        ↓
print_summary(unique_jobs)
    ↓
Display statistics and samples
        ↓
END
```

### Module Interactions

**scraper.py** (Orchestrator)
- Imports: serper_api, deduplicator, config
- Creates: SerperAPI instance
- Calls: api.search_jobs() for each query
- Calls: deduplicate_jobs() on collected data
- Writes: JSON and CSV files to output/

**serper_api.py** (API Client)
- Imports: os, requests, dotenv
- Reads: .env file for API key
- Makes: HTTP POST requests to Serper API
- Returns: Normalized job dictionaries

**deduplicator.py** (Data Processor)
- Imports: difflib, urllib.parse, config
- Receives: List of job dictionaries
- Processes: URL normalization, fuzzy matching
- Returns: Deduplicated list + statistics

**config.py** (Configuration)
- No imports (pure constants)
- Provides: SEARCH_QUERIES, thresholds, paths
- Used by: All other modules

### External API Communication

**Serper API Endpoints**:

1. **Jobs Endpoint** (Primary)
   - URL: https://google.serper.dev/jobs
   - Method: POST
   - Headers: X-API-KEY, Content-Type: application/json
   - Payload: {q, location, gl, hl, num}
   - Response: {jobs: [{title, company, location, link, salary, date, description}]}

2. **Search Endpoint** (Fallback)
   - URL: https://google.serper.dev/search
   - Method: POST
   - Headers: X-API-KEY, Content-Type: application/json
   - Payload: {q, gl, hl, num}
   - Response: {organic: [{title, link, snippet}]}

**API Flow**:
```
SerperAPI.search_jobs()
    ↓
Try: _search_jobs_endpoint()
    ↓
    POST /jobs with query + location
    ↓
    If 404 or empty: Fallback
    ↓
    _normalize_jobs_endpoint_results()
    ↓
    Return jobs
        ↓
If empty: _search_regular_endpoint()
    ↓
    POST /search with "{query} jobs in {location}"
    ↓
    _normalize_search_results()
    ↓
    Filter job-related results
    ↓
    Extract company from title/snippet
    ↓
    Return jobs
```

### Key Design Patterns

1. **Facade Pattern**: SerperAPI wraps complex API logic
2. **Strategy Pattern**: Two endpoint strategies (jobs vs search)
3. **Pipeline Pattern**: Scrape → Deduplicate → Export
4. **Singleton-like**: Single SerperAPI instance per scraper
5. **Separation of Concerns**: Each module has single responsibility

---

## 5. CODING CONVENTIONS

### Naming Conventions

**Variables**:
- Local variables: `lowercase_with_underscores`
- Examples: `job_records`, `api_key`, `normalized_url`

**Functions**:
- Function names: `lowercase_with_underscores()`
- Private methods: `_leading_underscore()`
- Examples: `search_jobs()`, `_normalize_results()`, `deduplicate_jobs()`

**Classes**:
- Class names: `PascalCase`
- Examples: `SerperJobScraper`, `SerperAPI`

**Constants**:
- Module-level constants: `UPPERCASE_WITH_UNDERSCORES`
- Examples: `SEARCH_QUERIES`, `FUZZY_SIMILARITY_THRESHOLD`, `OUTPUT_DIR`

**Files**:
- Python modules: `lowercase_with_underscores.py`
- Documentation: `UPPERCASE.md` or `PascalCase.md`

### Code Patterns Consistently Used

**Type Hints**:
```python
def search_jobs(
    self,
    query: str,
    location: str = "Bangalore, India",
    num_results: int = 10
) -> List[Dict]:
```

**Docstrings** (Google Style):
```python
"""
Brief description.

Args:
    param1: Description
    param2: Description
    
Returns:
    Description of return value
"""
```

**Logging Pattern**:
```python
logger = logging.getLogger(__name__)
logger.info("Message")
logger.warning("Warning")
logger.error("Error")
logger.debug("Debug info")
```

**Error Handling**:
```python
try:
    # API call or operation
    response = requests.post(...)
    response.raise_for_status()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return []  # Graceful degradation
```

**Configuration Loading**:
```python
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('SERPER_API_KEY')
```

**Path Handling**:
```python
from pathlib import Path
Path(OUTPUT_DIR).mkdir(exist_ok=True)
json_path = Path(OUTPUT_DIR) / filename
```

**String Formatting**:
- F-strings preferred: `f"Found {len(jobs)} jobs"`
- No old-style % formatting
- No .format() method

**List Comprehensions**:
```python
with_salary = sum(1 for job in jobs if job.get('salary'))
filtered = [job for job in jobs if condition]
```

### Import Style and Ordering

**Standard Library First**:
```python
import os
import logging
import json
import csv
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from difflib import SequenceMatcher
from urllib.parse import urlparse, urlunparse
```

**Third-Party Second**:
```python
import requests
from dotenv import load_dotenv
```

**Local Modules Last**:
```python
from serper_api import SerperAPI
from deduplicator import deduplicate_jobs
from config import SEARCH_QUERIES, OUTPUT_DIR
```

**Import Conventions**:
- Absolute imports only (no relative imports)
- One import per line for clarity
- Grouped by category with blank lines
- No wildcard imports (no `from module import *`)

### Patterns to Avoid (Anti-patterns)

**Avoided in this codebase**:
1. ❌ Global mutable state (uses class instances)
2. ❌ Hardcoded credentials (uses .env)
3. ❌ Silent failures (logs all errors)
4. ❌ Magic numbers (uses named constants)
5. ❌ Deep nesting (max 2-3 levels)
6. ❌ God objects (single responsibility per class)
7. ❌ Tight coupling (dependency injection via __init__)

**Good practices followed**:
1. ✅ Explicit is better than implicit
2. ✅ Fail gracefully with logging
3. ✅ Return empty collections instead of None
4. ✅ Use type hints for clarity
5. ✅ Comprehensive docstrings
6. ✅ Separation of concerns
7. ✅ Configuration externalization

---

## 6. DATABASE / DATA MODEL

### Current State
**No database currently implemented**
- Data stored in files (JSON/CSV)
- No persistence between runs
- No historical tracking
- Stateless operation

### Data Model (In-Memory)

**Job Record Dictionary**:
```python
{
    "title": str,           # Job title (required)
    "company": str,         # Company name (required, "Unknown" if missing)
    "location": str,        # Job location (required)
    "link": str,            # Job posting URL (required, unique)
    "salary": str | None,   # Salary info (optional)
    "posted_date": str | None,  # Posted date (optional)
    "description": str,     # Job description/snippet (required)
    "source": str          # Data source identifier (required)
}
```

**Source Values**:
- `"serper_jobs_api"` - From /jobs endpoint
- `"serper_search_api"` - From /search endpoint

**Validation Rules**:
- title, company, link must be non-empty
- link must be valid HTTP/HTTPS URL
- Records without required fields are skipped

### Planned Database Schema (Future)

From FUTURE_UPDATES.md, planned SQLite/PostgreSQL schema:

**jobs table**:
- id (PK), title, company, location, salary, link (unique)
- description, source, experience, skills, job_type
- first_seen, last_seen, times_seen

**job_enrichment table**:
- job_id (FK), experience_level, years_experience
- domain_knowledge, education_required, certifications
- work_environment, typical_day, enriched_date

**skills table**:
- id (PK), name (unique), category, subcategory
- difficulty, learning_time_hours, description

**job_skills table** (many-to-many):
- job_id (FK), skill_id (FK)
- importance, proficiency_level

**projects table**:
- id (PK), name, description, difficulty
- estimated_hours, category, github_examples

**learning_paths table**:
- id (PK), job_id (FK), total_duration_hours
- phases (JSON), created_date

### Key Relationships (Planned)
- jobs ↔ job_enrichment (1:1)
- jobs ↔ job_skills ↔ skills (many-to-many)
- jobs ↔ job_project_recommendations ↔ projects (many-to-many)
- jobs ↔ learning_paths (1:many)

---

## 7. API SURFACE

### Current API Surface
**No REST API or GraphQL** - This is a CLI application

### External API Consumed

**Serper.dev API**:

**Authentication**:
- Method: API Key
- Header: `X-API-KEY: {api_key}`
- Source: Environment variable `SERPER_API_KEY`
- No OAuth, no JWT, no session cookies

**Endpoint 1: Jobs Search**
```
POST https://google.serper.dev/jobs
Headers:
  X-API-KEY: {api_key}
  Content-Type: application/json
Body:
  {
    "q": "software engineer",
    "location": "Bangalore, India",
    "gl": "in",
    "hl": "en",
    "num": 20
  }
Response:
  {
    "jobs": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "location": "Bangalore",
        "link": "https://...",
        "salary": "₹15-25 LPA",
        "date": "2 days ago",
        "description": "..."
      }
    ]
  }
```

**Endpoint 2: General Search (Fallback)**
```
POST https://google.serper.dev/search
Headers:
  X-API-KEY: {api_key}
  Content-Type: application/json
Body:
  {
    "q": "software engineer jobs in Bangalore, India",
    "gl": "in",
    "hl": "en",
    "num": 20
  }
Response:
  {
    "organic": [
      {
        "title": "Software Engineer Jobs - Naukri",
        "link": "https://...",
        "snippet": "Apply to Software Engineer jobs..."
      }
    ]
  }
```

**Rate Limits**:
- Free tier: 2,500 searches/month
- ~100 requests/minute
- No explicit rate limit headers

**Error Responses**:
- 401: Invalid API key
- 404: Jobs endpoint not available (triggers fallback)
- 429: Rate limit exceeded
- 500: Server error

### Request/Response Patterns

**Request Pattern**:
1. Load API key from environment
2. Construct payload with query parameters
3. POST to endpoint with headers
4. Set 30-second timeout
5. Raise for HTTP errors
6. Parse JSON response

**Response Handling**:
1. Check for expected keys (jobs/organic)
2. Iterate through results
3. Normalize to standard format
4. Validate required fields
5. Filter invalid/non-job results
6. Return list of dictionaries

**Error Handling**:
- Network errors: Log warning, return empty list
- Invalid responses: Log error, return empty list
- Missing fields: Skip record, continue processing
- API errors: Log error, try fallback endpoint

---

## 8. CURRENT STATE OF THE PROJECT

### Features Complete ✅

**Core Functionality**:
- ✅ Serper API integration (jobs + search endpoints)
- ✅ Multi-query job scraping (8 default queries)
- ✅ Two-phase deduplication (URL + fuzzy matching)
- ✅ JSON export with timestamps
- ✅ CSV export with UTF-8 encoding
- ✅ Comprehensive logging system
- ✅ Error handling and graceful degradation
- ✅ API key configuration via .env
- ✅ Summary statistics and reporting

**Data Processing**:
- ✅ URL normalization (remove params, fragments)
- ✅ Fuzzy string matching (90% threshold)
- ✅ Company name extraction from titles
- ✅ Job result validation and filtering
- ✅ Source tracking (jobs_api vs search_api)

**Documentation**:
- ✅ Comprehensive README
- ✅ Quick start guide
- ✅ Usage examples
- ✅ Detailed workflow documentation
- ✅ Migration summary (browser → API)
- ✅ Future roadmap
- ✅ Current improvements guide

### Features In Progress 🔄

**None currently** - All planned features are in FUTURE_UPDATES.md

### Features Planned (Not Started) 📋

From FUTURE_UPDATES.md:

**Phase 1** (1 month):
- LLM integration for job description analysis
- Skills extraction and categorization
- Experience level detection
- Database setup (SQLite/PostgreSQL)

**Phase 2** (2-3 months):
- GitHub API integration
- Project recommendation engine
- GitHub repository finder and ranker
- Learning path generation

**Phase 3** (4-6 months):
- Web dashboard (React/Vue + FastAPI)
- Resume matching
- Interview preparation
- Salary insights

### Known Issues and TODOs

**From Code Analysis**:
- No TODO or FIXME comments found in codebase
- No known bugs documented in code
- Clean codebase with no technical debt markers

**Potential Improvements** (from CURRENT_IMPROVEMENTS.md):
1. Extract more details from job descriptions (experience, skills, job type)
2. Expand search queries to 30+ (currently 8)
3. Add job categorization (backend, frontend, data, etc.)
4. Add filtering by skills, experience, salary
5. Add Excel export with formatting
6. Add Markdown summary reports
7. Setup SQLite database for historical tracking
8. Add email notifications
9. Setup cron job for daily automation
10. Improve logging with rotation

**Testing Gaps**:
- No unit tests (pytest removed during migration)
- No integration tests
- No property-based tests (hypothesis removed)
- Only manual test script (test_api.py)

**Documentation Gaps**:
- No API documentation (not applicable - CLI tool)
- No contribution guidelines
- No code of conduct
- No issue templates

---

## 9. KEY DECISIONS & CONSTRAINTS

### Architectural Decisions

**1. API-Based vs Browser Scraping**
- **Decision**: Use Serper API instead of browser automation
- **Rationale**:
  - Browser scraping had 62.5% CAPTCHA rate
  - Only 37.5% success rate with browser approach
  - API provides 100% success rate
  - 97% faster execution (18s vs 5-10 min)
  - No infrastructure costs (proxies, CAPTCHA solvers)
- **Trade-off**: Dependency on third-party API, monthly limit (2,500 searches)

**2. File-Based Storage vs Database**
- **Decision**: Use JSON/CSV files for now
- **Rationale**: Simplicity, no setup required, easy to inspect
- **Future**: Will migrate to database for historical tracking

**3. Synchronous vs Asynchronous**
- **Decision**: Synchronous API calls
- **Rationale**: Simple, adequate for current scale (8 queries)
- **Future**: May add async for 30+ queries

**4. Monolithic vs Microservices**
- **Decision**: Single Python application
- **Rationale**: Small scope, single developer, no scaling needs yet
- **Future**: May split into services (scraper, enricher, API)

**5. Two-Phase Deduplication**
- **Decision**: URL-based first, then fuzzy matching
- **Rationale**: URL dedup is fast (O(n)), fuzzy is slow (O(n²))
- **Optimization**: Reduces fuzzy comparisons by ~50%

### Constraints

**Technical Constraints**:
1. **API Limits**: 2,500 Serper API calls/month (free tier)
2. **Python Version**: Requires Python 3.8+ (uses type hints, f-strings)
3. **Internet Required**: Cannot work offline
4. **No Database**: Currently file-based only
5. **Single-threaded**: No parallel processing

**Business Constraints**:
1. **Free Infrastructure**: Must remain free (no paid services)
2. **India Focus**: Targets Indian job market only
3. **Tech Jobs Only**: Focused on software/IT roles
4. **English Only**: No multi-language support

**Data Constraints**:
1. **No Historical Data**: Each run is independent
2. **No User Accounts**: No personalization
3. **No Real-time Updates**: Manual execution only
4. **Limited Enrichment**: Basic data only (no skills analysis yet)

### Things That Should NOT Be Changed

**Locked Dependencies**:
- **requests==2.31.0**: Pinned for stability
- **Python 3.8+**: Minimum version for type hints

**Core Architecture**:
- **Serper API**: Don't revert to browser scraping
- **Two-phase deduplication**: Algorithm is proven effective
- **File structure**: Keep flat structure (no deep nesting)

**Data Format**:
- **Job dictionary schema**: Changing breaks exports
- **Output file naming**: `{type}_{timestamp}.{ext}` pattern
- **CSV field order**: Maintains compatibility

**Configuration**:
- **.env for secrets**: Never hardcode API keys
- **config.py for constants**: Centralized configuration
- **Logging format**: Consistent across modules

### Design Principles Followed

1. **Explicit over Implicit**: Clear function names, no magic
2. **Fail Gracefully**: Return empty lists, log errors
3. **Single Responsibility**: Each module has one job
4. **Dependency Injection**: Pass dependencies via __init__
5. **Configuration Externalization**: No hardcoded values
6. **Comprehensive Logging**: Track everything
7. **Type Safety**: Use type hints everywhere
8. **Documentation First**: Docstrings for all public functions

---

## 10. ENVIRONMENT & SETUP

### Required Environment Variables

**From .env file**:
```bash
SERPER_API_KEY=your_api_key_here
```

**How to obtain**:
1. Go to https://serper.dev/
2. Sign up for free account
3. Copy API key from dashboard
4. Paste into .env file

**No other environment variables required**

### Installation Steps

**1. Prerequisites**:
```bash
# Check Python version (3.8+ required)
python3 --version  # Should show 3.8 or higher

# Check pip is installed
pip3 --version
```

**2. Clone/Download Project**:
```bash
cd /path/to/projects
# (Assuming project is already downloaded)
cd indeed-job-scraper
```

**3. Create Virtual Environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

**4. Install Dependencies**:
```bash
pip install -r requirements.txt
```

This installs:
- requests==2.31.0
- python-dotenv>=1.0.0

**5. Configure API Key**:
```bash
# Create .env file
echo "SERPER_API_KEY=your_actual_api_key" > .env

# OR edit .env manually
nano .env
```

**6. Verify Installation**:
```bash
# Test API connectivity
python3 test_api.py

# Expected output:
# ✓ API key configured
# ✓ Found 10 jobs
```

### Running the Project

**Basic Usage**:
```bash
# Activate virtual environment
source venv/bin/activate

# Run scraper
python3 scraper.py

# Output will be in output/ directory
ls output/
```

**Expected Execution**:
- Duration: ~18 seconds
- API calls: 16 (8 queries × 2 endpoints)
- Jobs collected: ~80 raw, ~70-75 unique
- Output: 2 files (JSON + CSV)

**Customization**:
```bash
# Edit search queries
nano config.py
# Modify SEARCH_QUERIES list

# Change location
nano scraper.py
# Edit: SerperJobScraper(location="Mumbai, India")

# Adjust results per query
nano scraper.py
# Edit: results_per_query=50
```

### External Services Required

**1. Serper.dev API** (Required):
- Service: Job search API
- Cost: Free (2,500 searches/month)
- Setup: Sign up at https://serper.dev/
- Configuration: Add API key to .env

**2. Internet Connection** (Required):
- Purpose: API calls to Serper
- Bandwidth: Minimal (~1-2 MB per run)

**No other external services required**:
- ❌ No database server
- ❌ No Redis
- ❌ No message queue
- ❌ No web server
- ❌ No Docker (optional, not required)

### Troubleshooting

**"API key not configured"**:
```bash
# Check .env file exists
ls -la .env

# Check contents
cat .env

# Ensure no spaces around =
# Correct: SERPER_API_KEY=abc123
# Wrong: SERPER_API_KEY = abc123
```

**"No module named 'requests'"**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**"No jobs found"**:
```bash
# Check internet connection
ping google.com

# Verify API key is valid
# Go to https://serper.dev/dashboard

# Check API usage/limits
# Free tier: 2,500/month
```

**Permission errors**:
```bash
# Create output directory
mkdir -p output

# Fix permissions
chmod 755 output
```

### Development Setup

**For Contributors**:
```bash
# Install development dependencies (none currently)
# pip install -r requirements-dev.txt  # (doesn't exist yet)

# Run tests
python3 test_api.py

# Check code style (manual - no linter configured)
# Follow PEP 8 conventions

# Run scraper in verbose mode
# (Edit scraper.py: logging.basicConfig(level=logging.DEBUG))
```

### Deployment

**Not applicable** - This is a CLI tool, not a web service

**For Automation**:
```bash
# Add to crontab for daily runs
crontab -e

# Run every day at 9 AM
0 9 * * * cd /path/to/indeed-job-scraper && /path/to/venv/bin/python3 scraper.py
```

---

## SUMMARY STATISTICS

**Project Metrics**:
- **Total Files**: 12 core files (5 Python, 3 config, 9 docs)
- **Lines of Code**: ~800 lines (Python only)
- **Dependencies**: 2 packages
- **Documentation**: 9 markdown files (~50 KB)
- **Test Coverage**: 0% (no automated tests)
- **API Endpoints Used**: 2 (Serper jobs + search)
- **Execution Time**: ~18 seconds
- **Success Rate**: 100%
- **Jobs per Run**: 70-75 unique

**Code Quality**:
- Type hints: ✅ Comprehensive
- Docstrings: ✅ All public functions
- Error handling: ✅ Graceful degradation
- Logging: ✅ Comprehensive
- Tests: ❌ None (removed during migration)
- Linting: ❌ Not configured
- CI/CD: ❌ Not configured

**Maturity Level**: Early Stage (MVP)
- Core functionality: Complete
- Testing: Minimal
- Documentation: Excellent
- Scalability: Limited (single-threaded)
- Maintainability: Good (clean code, well-documented)

---

## NEXT STEPS RECOMMENDATIONS

**Immediate (This Week)**:
1. Add unit tests for deduplicator.py
2. Add integration test for full scraping workflow
3. Configure linting (flake8 or pylint)
4. Add pre-commit hooks

**Short-term (This Month)**:
1. Implement skills extraction from descriptions
2. Expand to 30+ search queries
3. Add Excel export with formatting
4. Setup SQLite database for historical tracking

**Medium-term (Next Quarter)**:
1. Integrate LLM for job analysis (Phase 1)
2. Add GitHub API integration (Phase 2)
3. Build project recommendation engine
4. Create web dashboard prototype

**Long-term (6+ Months)**:
1. Full Job Preparation Intelligence Platform
2. Resume matching and interview prep
3. Mobile app
4. Monetization strategy

---

**END OF REPORT**

Generated: 2026-03-09
Version: 2.0.0 (Serper API Only)
Analyst: Kiro AI Assistant
