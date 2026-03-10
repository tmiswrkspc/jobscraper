# Job Scraper - Serper API

A Python-based job scraper that collects job listings from Google for Jobs using the Serper.dev API. Clean, fast, and CAPTCHA-free.

## Features

- **API-Based Scraping**: Uses Serper.dev API for reliable data collection
- **AI Enrichment (Optional)**: Uses Tavily AI to fetch full job descriptions and research companies
- **No CAPTCHAs**: API-based approach avoids browser detection
- **Fast Execution**: Collects 100+ jobs in under 30 seconds
- **Enhanced Deduplication**: Two-phase deduplication (URL + fuzzy title-company matching)
- **Skills Extraction**: Automatically identifies technical skills in job listings
- **Export Formats**: JSON and CSV with UTF-8 encoding

## Requirements

- **Python 3.8+**
- **Serper API Key**: Get free key from [serper.dev](https://serper.dev/)
- **Tavily API Key (Optional)**: Required for AI enrichment features [tavily.com](https://tavily.com/)
- **Internet Connection**: Required for API calls

## Installation

### 1. Install Python Dependencies

```bash
cd indeed-job-scraper
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project directory:

```bash
# .env
SERPER_API_KEY=your_serper_key_here
TAVILY_API_KEY=your_tavily_key_here  # Optional: for AI enrichment
```

Get your free API key from [serper.dev](https://serper.dev/) (2,500 searches/month free).

### 3. Verify Installation

```bash
python3 -c "import requests; print('✓ Requests installed')"
python3 -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"
python3 -c "import tavily; print('✓ Tavily installed')" # If using enrichment
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python3 scraper.py
```

The scraper will:
1. Load search queries from `config.py`
2. Call Serper API for each query
3. Deduplicate results
4. Export to JSON and CSV

### Test Serper API

Test the API integration:

```bash
python3 test_serper_google_jobs.py
```

## Output Files

### Location

All output files are saved to the `output/` directory:

```
output/
├── jobs_20260309_143052.json    # JSON export with timestamp
└── jobs_20260309_143052.csv     # CSV export with timestamp
```

### JSON Format

```json
[
  {
    "title": "Senior Software Engineer",
    "company": "Tech Corp India",
    "location": "Bangalore, Karnataka",
    "salary": "₹15-25 LPA",
    "posted_date": "2 days ago",
    "link": "https://www.naukri.com/job/...",
    "description": "We are looking for...",
    "source": "serper_jobs_api"
  }
]
```

### CSV Format

Headers: `title`, `company`, `location`, `salary`, `posted_date`, `link`, `description`, `source`

- UTF-8 encoding with BOM for Excel compatibility
- QUOTE_MINIMAL quoting strategy
- Handles special characters and commas

## Configuration

### Search Queries

Edit `SEARCH_QUERIES` in `config.py`:

```python
SEARCH_QUERIES = [
    "software engineer Bangalore",
    "python developer remote India",
    "data scientist Mumbai",
    # Add more queries...
]

# AI Enrichment
ENABLE_ENRICHMENT = True      # Set to False to disable Tavily
MAX_ENRICHMENT_JOBS = 10      # Max jobs to enrich per run
```

### Location

Edit location in `scraper.py`:

```python
scraper = SerperJobScraper(location="Mumbai, India")
```

### Results Per Query

Edit in `scraper.py`:

```python
jobs = scraper.scrape_all_queries(
    queries=SEARCH_QUERIES,
    results_per_query=50  # Default is 20
)
```

## API Usage & Limits

### Serper API Free Tier

- **2,500 searches per month**
- No credit card required
- Rate limit: ~100 requests per minute

### Current Usage

- 8 queries per run = 8 API calls
- Can run ~312 times per month (2,500 / 8)
- ~10 runs per day

### Optimization Tips

1. Reduce number of queries in `config.py`
2. Increase results per query (max 100)
3. Run less frequently (daily instead of hourly)

## Project Structure

```
indeed-job-scraper/
├── .env                    # API key configuration
├── config.py              # Search queries and settings
├── scraper.py             # Main scraper
├── serper_api.py          # Serper API client
├── deduplicator.py        # Deduplication logic
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── SERPER_WORKFLOW_PLAN.md  # Detailed workflow documentation
└── output/               # Output directory (created automatically)
    ├── jobs_*.json
    └── jobs_*.csv
```

## Architecture

### Components

1. **Serper API Client** (`serper_api.py`)
   - Handles API authentication
   - Makes requests to jobs and search endpoints
   - Normalizes responses to standard format

2. **Job Scraper** (`scraper.py`)
   - Orchestrates query execution
   - Manages API calls
   - Exports results

3. **Deduplicator** (`deduplicator.py`)
   - Phase 1: URL-based deduplication
   - Phase 2: Fuzzy title-company matching
   - Preserves order of unique records

4. **Configuration** (`config.py`)
   - Search queries
   - Deduplication thresholds
   - Output settings

### Workflow

```
1. Load Config → 2. Execute Queries → 3. Deduplicate → 4. Export
```

## Performance

### Typical Run (8 queries, 20 results each)

- Execution time: ~18 seconds
- API calls: 16 (8 jobs + 8 search fallbacks)
- Jobs collected: 80 raw
- Jobs after deduplication: 70-75 unique
- Success rate: 100%

## Troubleshooting

### API Key Issues

**Symptoms**: "API key not configured" or 401 errors

**Solutions**:
1. Check `.env` file exists and contains `SERPER_API_KEY=your_key`
2. Verify key is valid on [serper.dev/dashboard](https://serper.dev/dashboard)
3. Ensure no extra spaces or quotes around the key

### No Results

**Symptoms**: Empty output files

**Solutions**:
1. Check internet connection
2. Verify API key is valid
3. Check Serper API status
4. Try different search queries

### Rate Limit Exceeded

**Symptoms**: 429 errors

**Solutions**:
1. Check usage on [serper.dev/dashboard](https://serper.dev/dashboard)
2. Wait for monthly reset
3. Reduce query frequency
4. Upgrade to paid plan if needed

## Best Practices

1. **Monitor API Usage**: Check dashboard regularly
2. **Optimize Queries**: Use specific, targeted search terms
3. **Batch Processing**: Run once daily instead of continuously
4. **Backup Results**: Keep historical data for analysis

## License

This project is for educational purposes only. Ensure compliance with Serper.dev Terms of Service.

## Support

For issues or questions:
1. Check [Serper API docs](https://serper.dev/docs)
2. Review troubleshooting guide above
3. Check console output for error messages

## Resources

- **Serper API**: https://serper.dev/
- **Documentation**: https://serper.dev/docs
- **Dashboard**: https://serper.dev/dashboard
- **Workflow Plan**: See `SERPER_WORKFLOW_PLAN.md` for detailed workflow
