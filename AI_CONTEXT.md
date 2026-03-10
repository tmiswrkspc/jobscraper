# Job Scraper Project - AI Development Context

**Last Updated:** March 10, 2026  
**Purpose:** This document provides comprehensive context for AI assistants (Claude, ChatGPT, Gemini) to understand and contribute to this project.

---

## Project Overview

### What This Is
A Python CLI tool that scrapes technology job listings from Google for Jobs via the Serper.dev API. It collects, deduplicates, extracts skills, categorizes by role type, and exports clean data to JSON and CSV files.

### Target Users
- Primary: Tech job seekers in India (especially Bangalore)
- Secondary: Recruiters, market researchers, career counselors

### Current Status
**Phase 1 (MVP) - COMPLETE with Quick Wins enhancements**
- Scrapes 30 targeted search queries via Serper.dev (expanded from 8)
- Extracts 56 technical skills from job descriptions
- Categorizes jobs into 7 role types (backend, frontend, fullstack, data, devops, mobile, other)
- Two-phase deduplication (URL + fuzzy matching)
- Exports timestamped JSON and CSV files (combined + category-specific)
- Runs in ~49 seconds, produces ~237 unique jobs per run (3x increase from ~75)

---

## Technical Architecture

### Tech Stack
- **Language:** Python 3.12.2 (minimum: 3.8+)
- **Dependencies:** 
  - `requests==2.31.0` (HTTP client - pinned)
  - `python-dotenv>=1.0.0` (.env loading)
  - `tavily-python>=0.3.0` (Optional: Job enrichment)
- **Standard Library:** logging, json, csv, datetime, typing, pathlib, difflib, urllib.parse, os

### External Services
- **Serper.dev API** (Required)
  - Google for Jobs proxy
  - Auth: X-API-KEY header in .env
  - Free tier: 2,500 searches/month
  - Endpoints: POST https://google.serper.dev/jobs (primary), /search (fallback)
  
- **Tavily AI API** (Optional)
  - Job enrichment and research
  - Free tier: 1,000 requests/month
  - Gracefully disabled if not configured

### Project Structure
```
indeed-job-scraper/
├── scraper.py              # ENTRY POINT - SerperJobScraper class
├── serper_api.py           # API client - SerperAPI class
├── deduplicator.py         # Deduplication logic
├── config.py               # Constants only (SEARCH_QUERIES, thresholds, paths)
├── tavily_enricher.py      # Optional job enrichment
├── test_quick_wins.py      # Comprehensive test suite
├── test_categorization_unit.py    # Categorization tests
├── test_category_exports_unit.py  # Export tests
├── test_integration_quick_wins.py # Integration tests
├── requirements.txt        # Dependencies
├── .env                    # Secrets (never committed)
├── .gitignore
└── output/                 # Auto-created exports
    ├── serper_jobs_{timestamp}.json  # Combined export
    ├── serper_jobs_{timestamp}.csv   # Combined export
    └── jobs_{category}_{timestamp}.json  # Category-specific exports
```

### Module Dependencies
```
config.py          ← imported by everything (zero imports itself)
serper_api.py      ← imports config
deduplicator.py    ← imports config
tavily_enricher.py ← imports config
scraper.py         ← imports all above modules
```

---

## Core Features

### 1. Search Query Coverage (30 Queries)
Targets multiple dimensions for comprehensive job discovery:
- **Bangalore core roles (10):** software engineer, python developer, data analyst, frontend developer, java developer, full stack developer, data scientist, devops engineer, backend developer, machine learning engineer
- **Specific technologies (5):** django, react, nodejs, aws, kubernetes
- **Remote India positions (5):** remote software engineer, remote python developer, remote full stack developer, work from home developer, remote backend engineer
- **Other major cities (5):** Mumbai, Pune, Hyderabad, Delhi
- **Experience levels (3):** junior, senior, lead
- **Specific domains (2):** fintech, ecommerce

### 2. Technical Skills Extraction (56 Skills)
Detects skills across 6 categories:
- **Programming Languages (13):** Python, Java, JavaScript, TypeScript, Go, Rust, C++, C#, Ruby, PHP, Swift, Kotlin, Scala
- **Frameworks (9):** React, Angular, Vue, Django, Flask, Spring, Node.js, Express, FastAPI
- **Databases (8):** PostgreSQL, MySQL, MongoDB, Redis, Elasticsearch, Cassandra, Oracle, SQL Server
- **DevOps Tools (11):** Docker, Kubernetes, AWS, Azure, GCP, Terraform, Git, CI/CD, Jenkins, GitHub Actions, GitLab CI
- **API Technologies (4):** REST API, GraphQL, gRPC, Microservices
- **Data Science Tools (11):** Machine Learning, Deep Learning, TensorFlow, PyTorch, Pandas, NumPy, Scikit-learn, Kafka, RabbitMQ, Linux, Bash

**Implementation:** Case-insensitive pattern matching in job descriptions/snippets

### 3. Job Categorization (7 Categories)
Classifies jobs by role type using keyword matching:
- **backend:** backend, back-end, django, flask, spring, api, server
- **frontend:** frontend, front-end, react, angular, vue, css, ui
- **fullstack:** full stack, fullstack, full-stack (checked first - highest priority)
- **data:** data scientist, data analyst, ml, machine learning, ai
- **devops:** devops, sre, infrastructure, kubernetes, docker
- **mobile:** mobile, android, ios, flutter, react native
- **other:** Default for jobs without specific keywords

**Logic:** Combines title + description, case-insensitive matching, first match wins

### 4. Export Formats
- **Combined JSON:** All jobs in single file (`serper_jobs_{timestamp}.json`)
- **Combined CSV:** All jobs in single file (`serper_jobs_{timestamp}.csv`)
- **Category JSON:** Separate file per non-empty category (`jobs_{category}_{timestamp}.json`)
- **Encoding:** UTF-8 with ensure_ascii=False (preserves ₹, Hindi, emojis)
- **Formatting:** 2-space indentation for readability

### 5. Deduplication (Two-Phase)
- **Phase 1 (URL):** Removes exact URL duplicates
- **Phase 2 (Fuzzy):** Uses difflib.SequenceMatcher for title similarity (threshold: 0.85)
- **Typical retention:** 60-70% of raw results

---

## Job Dictionary Schema

```python
{
    'title': str,              # Job title
    'company': str,            # Company name
    'location': str,           # Job location
    'link': str,               # Job posting URL
    'salary': str | None,      # Salary information (if available)
    'posted_date': str | None, # Posting date (if available)
    'description': str,        # Job description or snippet
    'source': str,             # 'serper_jobs_api' or 'serper_search_api'
    'skills': List[str]        # Extracted technical skills (NEW)
}
```

---

## Key Implementation Details

### SerperAPI Class (serper_api.py)
**Key Methods:**
- `search_jobs(query, location)` - Main search method with fallback logic
- `_search_jobs_endpoint(query, location)` - Primary endpoint (Google for Jobs)
- `_search_search_endpoint(query, location)` - Fallback endpoint (Google Search)
- `_extract_skills(text)` - Extracts technical skills from text (NEW)
- `_normalize_jobs_endpoint_results(data)` - Normalizes jobs endpoint response
- `_normalize_search_results(data, query, location)` - Normalizes search endpoint response

**Skills Extraction Logic:**
```python
SKILLS_PATTERNS = {
    'Python': ['python'],
    'React': ['react', 'reactjs', 'react.js'],
    'Docker': ['docker'],
    # ... 56 total skills
}

def _extract_skills(self, text: str) -> List[str]:
    if not text:
        return []
    text_lower = text.lower()
    detected = []
    for skill_name, patterns in self.SKILLS_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_lower:
                detected.append(skill_name)
                break  # First match wins, avoid duplicates
    return detected
```

### SerperJobScraper Class (scraper.py)
**Key Methods:**
- `run()` - Main orchestrator: search → deduplicate → enrich → export
- `categorize_jobs(jobs)` - Categorizes jobs by role type (NEW)
- `export_results(jobs)` - Exports to JSON/CSV (combined + category-specific) (ENHANCED)
- `print_summary(jobs)` - Prints statistics

**Categorization Logic:**
```python
CATEGORY_KEYWORDS = {
    'backend': ['backend', 'back-end', 'django', 'flask', 'spring', 'api', 'server'],
    'frontend': ['frontend', 'front-end', 'react', 'angular', 'vue', 'css', 'ui'],
    'fullstack': ['full stack', 'fullstack', 'full-stack'],
    # ... 7 total categories
}

def categorize_jobs(self, jobs):
    # Check fullstack FIRST (most specific)
    # Then check other categories
    # First match wins
    # Default to 'other' if no matches
```

### Deduplication (deduplicator.py)
**Function:** `deduplicate_jobs(jobs)`
- Phase 1: URL-based deduplication (exact match)
- Phase 2: Fuzzy title matching (SequenceMatcher, threshold 0.85)
- Returns: (deduplicated_jobs, stats_dict)

---

## Configuration (config.py)

### Key Constants
```python
# API Configuration
SERPER_API_KEY = os.getenv('SERPER_API_KEY')
SERPER_JOBS_URL = "https://google.serper.dev/jobs"
SERPER_SEARCH_URL = "https://google.serper.dev/search"

# Search Configuration
SEARCH_QUERIES = [...]  # 30 queries
RESULTS_PER_QUERY = 20
DEFAULT_LOCATION = "Bangalore, India"

# Deduplication Thresholds
URL_DEDUP_THRESHOLD = 1.0
FUZZY_DEDUP_THRESHOLD = 0.85

# Output Configuration
OUTPUT_DIR = "output"

# Enrichment Configuration (Optional)
ENABLE_ENRICHMENT = False
MAX_ENRICHMENT_JOBS = 10
```

---

## Testing Strategy

### Test Files
1. **test_quick_wins.py** - Comprehensive test suite (main runner)
2. **test_categorization_unit.py** - Categorization unit tests
3. **test_category_exports_unit.py** - Export unit tests
4. **test_integration_quick_wins.py** - Integration tests

### Test Coverage
- **Property-Based Tests:** 11 properties, 100-150 iterations each
- **Unit Tests:** 24 test suites covering specific examples
- **Integration Tests:** 6 scenarios including edge cases
- **Total:** 100% pass rate across all tests

### Running Tests
```bash
# Run comprehensive test suite
python test_quick_wins.py

# Run specific test modules
python test_categorization_unit.py
python test_category_exports_unit.py
python test_integration_quick_wins.py
```

---

## Usage

### Basic Usage
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run scraper
python scraper.py

# Results will be in output/ directory
```

### Output Files
After running, you'll find in `output/`:
- `serper_jobs_{timestamp}.json` - All 237 jobs combined
- `serper_jobs_{timestamp}.csv` - All 237 jobs combined
- `jobs_backend_{timestamp}.json` - 33 backend jobs
- `jobs_frontend_{timestamp}.json` - 29 frontend jobs
- `jobs_fullstack_{timestamp}.json` - 34 fullstack jobs
- `jobs_data_{timestamp}.json` - 58 data jobs
- `jobs_devops_{timestamp}.json` - 20 devops jobs
- `jobs_other_{timestamp}.json` - 63 other jobs

---

## Development Guidelines

### Code Style
- **Naming Conventions:**
  - Modules: `lowercase_with_underscores.py`
  - Classes: `PascalCase`
  - Functions: `snake_case()`
  - Constants: `UPPER_SNAKE_CASE`
- **Type Hints:** Use where appropriate
- **Formatting:** PEP 8 (manual, no linter configured)
- **Docstrings:** Google style

### Architecture Principles
- **Flat Structure:** All modules in root directory (no subdirectories)
- **Synchronous Execution:** No async/await (intentional at current scale)
- **File-Based Storage:** No database (deliberate for Phase 1)
- **Zero New Dependencies:** Use standard library when possible
- **Additive Changes:** Preserve existing functionality

### Important Constraints
- `requests==2.31.0` is pinned - do not upgrade without testing
- Do not suggest async patterns yet - synchronous is intentional
- Do not suggest database - file-based storage is deliberate
- Free tier constraint: 2,500 Serper API calls/month
- Focus market: India (Bangalore primarily), tech jobs only, English only

### Adding New Features
1. **New constants** → Add to `config.py`
2. **New utility functions** → Add to most relevant existing module (not new file)
3. **New output formats** → Write to `output/` with timestamp naming
4. **Schema changes** → Discuss first (breaks all exports)

---

## Recent Enhancements (Quick Wins Implementation)

### What Was Added
1. **Expanded Search Queries:** 8 → 30 queries (3x more jobs)
2. **Skills Extraction:** 56 technical skills across 6 categories
3. **Job Categorization:** 7 role types with keyword matching
4. **Category Exports:** Separate JSON files per category

### Files Modified
- `config.py` - Expanded SEARCH_QUERIES from 8 to 30
- `serper_api.py` - Added SKILLS_PATTERNS and _extract_skills() method
- `scraper.py` - Added categorize_jobs() method and category export logic

### Files Created
- `test_quick_wins.py` - Comprehensive test suite
- `test_categorization_unit.py` - Categorization unit tests
- `test_category_exports_unit.py` - Export unit tests
- `test_integration_quick_wins.py` - Integration tests

### Backward Compatibility
- All existing functionality preserved
- Job schema only adds 'skills' field
- Combined JSON/CSV exports maintained
- No breaking changes

---

## Common Development Tasks

### Adding New Skills
Edit `serper_api.py` → `SKILLS_PATTERNS` dictionary:
```python
'NewSkill': ['pattern1', 'pattern2', 'pattern-with-dash']
```

### Adding New Search Queries
Edit `config.py` → `SEARCH_QUERIES` list:
```python
SEARCH_QUERIES = [
    # ... existing queries
    "new query Bangalore",
]
```

### Adding New Job Categories
Edit `scraper.py` → `categorize_jobs()` method:
```python
CATEGORY_KEYWORDS = {
    # ... existing categories
    'newcategory': ['keyword1', 'keyword2'],
}
```

### Modifying Deduplication Thresholds
Edit `config.py`:
```python
FUZZY_DEDUP_THRESHOLD = 0.85  # Adjust between 0.0-1.0
```

---

## API Usage & Limits

### Serper API
- **Free Tier:** 2,500 searches/month
- **Current Usage:** 30 queries per run = 83 runs/month maximum
- **Rate Limiting:** None observed, but be respectful
- **Cost:** $0 (free tier sufficient for current scale)

### Tavily API (Optional)
- **Free Tier:** 1,000 requests/month
- **Current Usage:** Disabled by default (ENABLE_ENRICHMENT = False)
- **Purpose:** Enhanced job descriptions, company research

---

## Known Issues & Limitations

### Current Limitations
1. **Jobs endpoint 404 errors:** Serper jobs endpoint returns 404, fallback to search endpoint works fine
2. **Snippet-based extraction:** Search endpoint provides snippets, not full descriptions (less skill detection)
3. **Company extraction:** Sometimes inaccurate from search results (marked as "Unknown")
4. **Salary data:** Rarely available in search results
5. **Short skill names:** "Go" and "Git" patterns can have edge cases (99% accuracy in property tests)

### Not Issues (By Design)
- Synchronous execution (intentional for simplicity)
- No database (file-based is deliberate for Phase 1)
- No test framework like pytest (manual test scripts preferred)
- No async/await patterns (not needed at current scale)

---

## Future Roadmap

### Phase 2 (Planned)
- LLM-powered job analysis
- Skills gap analysis
- SQLite database for historical tracking
- Enhanced company information

### Phase 3 (Planned)
- GitHub API integration
- Project recommendations based on skills
- Learning path suggestions

### Phase 4 (Planned)
- Web dashboard (FastAPI + React)
- Resume matching
- Interview preparation tools

---

## Testing Philosophy

### Dual Testing Approach
- **Property-Based Tests:** Validate universal properties across randomized inputs (100+ iterations)
- **Unit Tests:** Verify specific examples and edge cases
- **Integration Tests:** Validate full pipeline end-to-end

### Test Execution
```bash
# Run all tests
python test_quick_wins.py

# Run specific test modules
python test_categorization_unit.py
python test_category_exports_unit.py
python test_integration_quick_wins.py
```

### Property-Based Testing
Uses Python's standard library `random` module (no hypothesis dependency):
- Generates randomized test inputs
- Validates correctness properties hold across diverse scenarios
- Minimum 100 iterations per property
- Reports detailed failure cases when properties violated

---

## Environment Setup

### Prerequisites
- Python 3.8+ (3.12.2 recommended)
- pip package manager
- Serper API key (get from serper.dev)

### Installation
```bash
# Clone repository
git clone <repo-url>
cd indeed-job-scraper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "SERPER_API_KEY=your_key_here" > .env

# Run scraper
python scraper.py
```

---

## Debugging Tips

### Common Issues

**1. API Key Not Found**
```
Error: SERPER_API_KEY not found in environment
Solution: Check .env file exists and contains SERPER_API_KEY=your_key
```

**2. 404 Errors on Jobs Endpoint**
```
Warning: Jobs endpoint returned 404
Solution: This is expected - fallback to search endpoint works automatically
```

**3. No Skills Detected**
```
Issue: Jobs have empty skills list
Cause: Search endpoint provides short snippets, not full descriptions
Solution: This is expected for some jobs - skills extraction works best with detailed descriptions
```

**4. Import Errors**
```
Error: ModuleNotFoundError
Solution: Ensure virtual environment is activated and dependencies installed
```

### Logging
- **Level:** INFO (configured in scraper.py)
- **Format:** `[timestamp] [level] [module] message`
- **Output:** Console (stdout)

---

## Performance Metrics

### Current Performance (30 Queries)
- **Execution Time:** ~49 seconds
- **Raw Jobs Collected:** ~299 jobs (10 per query average)
- **After Deduplication:** ~237 unique jobs (79% retention)
- **Skills Detection Rate:** ~53% of jobs (126/237)
- **API Calls:** 30 per run (well within free tier)

### Comparison to Previous (8 Queries)
- **Jobs:** 237 vs ~75 (3.16x increase) ✓
- **Execution Time:** 49s vs ~18s (2.7x increase)
- **API Efficiency:** 7.9 unique jobs per query vs 9.4 (slight decrease due to overlap)

---

## Code Quality

### Testing
- **Test Coverage:** Comprehensive (property + unit + integration)
- **Test Framework:** None (manual test scripts)
- **Test Execution:** All tests passing (100% success rate)

### Documentation
- **README.md** - User-facing documentation
- **ARCHITECTURE.md** - System design
- **CONVENTIONS.md** - Coding standards
- **AI_CONTEXT.md** - This file (AI development context)

### Error Handling
- Graceful API fallback (jobs → search endpoint)
- None/empty input handling in skill extraction
- Missing field handling in categorization
- File system error propagation (fail-fast for data integrity)

---

## Security & Privacy

### API Keys
- Stored in `.env` file (gitignored)
- Never hardcoded in source
- Loaded via python-dotenv

### Data Privacy
- No user authentication (CLI tool)
- No personal data collected
- Job data is public information from job boards
- No data sent to third parties (except Serper/Tavily APIs)

### Dependencies
- Minimal attack surface (only 2-3 dependencies)
- `requests==2.31.0` pinned for stability
- No known vulnerabilities in dependencies

---

## Contributing Guidelines

### When Working with AI Assistants

**DO:**
- Provide this document for full context
- Ask about specific features or bugs
- Request explanations of existing code
- Suggest improvements with rationale
- Test changes thoroughly

**DON'T:**
- Ask to add databases (Phase 1 is file-based by design)
- Suggest async/await patterns (not needed yet)
- Recommend new dependencies without strong justification
- Upgrade requests package (pinned for stability)
- Create subdirectories (flat structure is intentional)

### Code Review Checklist
- [ ] Follows naming conventions
- [ ] No new dependencies (or justified)
- [ ] Backward compatible
- [ ] Tests included
- [ ] No hardcoded secrets
- [ ] Proper error handling
- [ ] Logging added for important operations
- [ ] Documentation updated

---

## Useful Commands

```bash
# Run scraper
python scraper.py

# Run all tests
python test_quick_wins.py

# Check Python version
python --version

# List output files
ls -lh output/

# View sample job from category
python -c "import json; print(json.dumps(json.load(open('output/jobs_backend_*.json'))[0], indent=2))"

# Count jobs by category
python -c "import json; from pathlib import Path; files = Path('output').glob('jobs_*_*.json'); print('\n'.join(f'{f.stem.split(\"_\")[1]}: {len(json.load(open(f)))}' for f in files if not f.stem.startswith('jobs_serper')))"

# Check skills distribution
python -c "import json; jobs = json.load(open('output/serper_jobs_*.json')); skills = [s for j in jobs for s in j.get('skills', [])]; from collections import Counter; print(Counter(skills).most_common(10))"
```

---

## Contact & Resources

### Documentation
- **README.md** - Getting started guide
- **ARCHITECTURE.md** - System design details
- **QUICKSTART.md** - Quick setup guide
- **USAGE_EXAMPLES.md** - Usage examples

### External Resources
- Serper API Docs: https://serper.dev/docs
- Tavily API Docs: https://docs.tavily.com/
- Python Docs: https://docs.python.org/3/

---

## Questions for AI Assistants

When discussing this project with AI assistants, consider asking:

1. **Feature Development:**
   - "How can I add support for [new skill/category/location]?"
   - "What's the best way to implement [feature] while maintaining the flat structure?"
   - "How can I improve [specific component] without breaking backward compatibility?"

2. **Debugging:**
   - "Why are some jobs not being categorized correctly?"
   - "How can I improve skill detection accuracy for [specific skill]?"
   - "What's causing [specific error] and how do I fix it?"

3. **Optimization:**
   - "How can I reduce execution time while maintaining accuracy?"
   - "What's the best way to handle [edge case]?"
   - "How can I improve deduplication accuracy?"

4. **Testing:**
   - "How do I add tests for [new feature]?"
   - "What edge cases should I test for [component]?"
   - "How can I improve test coverage for [area]?"

---

## Version History

### v1.1.0 (March 10, 2026) - Quick Wins Implementation
- Expanded search queries from 8 to 30
- Added technical skills extraction (56 skills)
- Added job categorization (7 categories)
- Added category-specific exports
- Comprehensive test suite (property + unit + integration)
- 3x increase in job discovery (75 → 237 jobs)

### v1.0.0 (March 7, 2026) - Initial Release
- Basic scraping via Serper API
- Two-phase deduplication
- JSON/CSV exports
- 8 search queries
- ~75 unique jobs per run

---

**End of AI Context Document**

*This document is designed to provide AI assistants with complete context for understanding and contributing to the Job Scraper project. Keep it updated as the project evolves.*
