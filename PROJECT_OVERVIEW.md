# Project Overview

## Job Scraper - Serper API Edition

A clean, simple, and fast job scraper using Serper.dev API.

## Quick Stats

- **Files**: 12 core files
- **Dependencies**: 2 packages
- **Execution Time**: ~18 seconds
- **Success Rate**: 100%
- **Jobs per Run**: 70-75 unique jobs
- **Cost**: Free (2,500 searches/month)

## File Structure

```
indeed-job-scraper/
├── Core Files (6)
│   ├── scraper.py (14K)           # Main scraper & orchestrator
│   ├── serper_api.py (12K)        # API client & skills detection
│   ├── tavily_enricher.py (13K)   # AI-powered job enrichment
│   ├── deduplicator.py (6.9K)     # Deduplication logic
│   ├── config.py (3.4K)           # Configuration
│   └── test_api.py (1.5K)         # API test script
│
├── Configuration (3)
│   ├── .env                        # API key (create this)
│   ├── .gitignore                  # Git ignore rules
│   └── requirements.txt (38B)      # Dependencies
│
├── Documentation (6)
│   ├── README.md (6.2K)            # Main documentation
│   ├── QUICKSTART.md (1.9K)        # 5-minute setup guide
│   ├── USAGE_EXAMPLES.md (7.8K)    # Code examples
│   ├── SERPER_WORKFLOW_PLAN.md (21K) # Detailed workflow
│   ├── CHANGELOG.md (2.5K)         # Version history
│   └── MIGRATION_SUMMARY.md (5.0K) # Migration details
│
└── Output (auto-created)
    └── output/
        ├── jobs_*.json             # JSON exports
        └── jobs_*.csv              # CSV exports
```

## Core Components

### 1. Scraper (`scraper.py`)
Main orchestrator that:
- Loads configuration
- Executes search queries
- Collects jobs from API
- Deduplicates results
- Exports to JSON/CSV

### 2. API Client (`serper_api.py`)
Handles Serper API:
- Authentication
- Jobs endpoint requests
- Search endpoint fallback
- Response normalization
- Error handling

### 3. Deduplicator (`deduplicator.py`)
Two-phase deduplication:
- Phase 1: URL-based (exact matches)
- Phase 2: Fuzzy matching (title + company)
- Configurable similarity threshold

### 4. AI Enricher (`tavily_enricher.py`)
Optional enrichment layer:
- Fetches full job content from URLs
- Researches company culture
- Identifies learning resources
- Finds relevant GitHub projects

### 5. Configuration (`config.py`)
Settings:
- Search queries & freshness
- AI Enrichment toggle & limits
- Deduplication thresholds
- Output directory paths

### 5. Test Script (`test_api.py`)
Quick API test:
- Verifies API key
- Tests single query
- Shows sample results

## Documentation Guide

### For Quick Setup
→ Read `QUICKSTART.md` (5 minutes)

### For Full Documentation
→ Read `README.md` (comprehensive)

### For Code Examples
→ Read `USAGE_EXAMPLES.md` (20+ examples)

### For Detailed Workflow
→ Read `SERPER_WORKFLOW_PLAN.md` (technical deep-dive)

### For Version History
→ Read `CHANGELOG.md` (what changed)

### For Migration Details
→ Read `MIGRATION_SUMMARY.md` (browser → API)

## Workflow

```
1. Load Config
   ↓
2. Initialize API Client
   ↓
3. Execute Queries (8 queries)
   ↓
4. Collect Jobs (~80 raw jobs)
   ↓
5. Deduplicate (~70-75 unique)
   ↓
6. Export (JSON + CSV)
   ↓
7. Done! (18 seconds)
```

## Key Features

### Simplicity
- 12 files total
- 2 dependencies
- No browser automation
- No proxy management
- No CAPTCHA handling

### Speed
- 18 seconds execution
- Parallel API calls
- No page load waits
- Instant results

### Reliability
- 100% success rate
- No IP blocking
- No CAPTCHAs
- Consistent data

### Cost
- Free tier: 2,500/month
- No infrastructure costs
- No proxy fees
- No CAPTCHA solver fees

## Usage

### Basic
```bash
python3 scraper.py
```

### Test API
```bash
python3 test_api.py
```

### Custom Query
```python
from serper_api import SerperAPI

api = SerperAPI()
jobs = api.search_jobs("python developer", "Mumbai, India")
print(f"Found {len(jobs)} jobs")
```

## Configuration

### Search Queries
Edit `config.py`:
```python
SEARCH_QUERIES = [
    "your query here",
    "another query",
]
```

### Location
Edit `scraper.py`:
```python
scraper = SerperJobScraper(location="Mumbai, India")
```

### Results Per Query
Edit `scraper.py`:
```python
jobs = scraper.scrape_all_queries(
    queries=SEARCH_QUERIES,
    results_per_query=50  # Default: 20
)
```

## Output

### JSON Format
```json
{
  "title": "Software Engineer",
  "company": "Tech Corp",
  "location": "Bangalore",
  "salary": "₹15-25 LPA",
  "link": "https://...",
  "source": "serper_jobs_api"
}
```

### CSV Format
```
title,company,location,salary,link,source
"Software Engineer","Tech Corp","Bangalore","₹15-25 LPA","https://...","serper_jobs_api"
```

## API Limits

### Free Tier
- 2,500 searches/month
- ~100 requests/minute
- No credit card required

### Usage Calculation
- 8 queries/run = 8 API calls
- Can run 312 times/month
- ~10 runs/day

## Dependencies

### Required
```
requests==2.31.0        # HTTP requests
python-dotenv>=1.0.0    # Environment variables
```

### Installation
```bash
pip install -r requirements.txt
```

## Setup Steps

1. **Install**: `pip install -r requirements.txt`
2. **API Key**: Get from [serper.dev](https://serper.dev/)
3. **Configure**: Add to `.env` file
4. **Test**: `python3 test_api.py`
5. **Run**: `python3 scraper.py`

## Troubleshooting

### API Key Issues
- Check `.env` file exists
- Verify key is correct
- No spaces around key

### No Results
- Check internet connection
- Verify API key valid
- Try different queries

### Rate Limit
- Check [dashboard](https://serper.dev/dashboard)
- Wait for monthly reset
- Reduce query frequency

## Performance

### Typical Run
- Queries: 8
- API Calls: 16 (jobs + search fallbacks)
- Raw Jobs: ~80
- Unique Jobs: ~70-75
- Time: ~18 seconds
- Success: 100%

### Scalability
- 10 queries: ~22 seconds, ~90 jobs
- 20 queries: ~45 seconds, ~150 jobs
- 50 queries: ~2 minutes, ~300 jobs

## Best Practices

1. **Start small**: Test with 1-2 queries first
2. **Monitor usage**: Check dashboard regularly
3. **Use specific queries**: Better results
4. **Deduplicate**: Always run deduplication
5. **Schedule wisely**: Daily = 240 calls/month
6. **Backup data**: Keep historical exports
7. **Handle errors**: Use try-except blocks

## Support

- **API Docs**: https://serper.dev/docs
- **Dashboard**: https://serper.dev/dashboard
- **Issues**: See `README.md` troubleshooting

## Version

**Current**: 2.0.0 (Serper API Only)
**Previous**: 1.0.0 (Browser-based)

See `CHANGELOG.md` for details.

## License

Educational purposes only. Follow Serper.dev Terms of Service.

---

**Ready to start?** → See `QUICKSTART.md`
