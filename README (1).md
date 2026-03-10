# Job Preparation Intelligence Platform

A Python CLI tool that aggregates technology job listings from Google for Jobs using the Serper.dev API. It collects, deduplicates, and exports job data to help candidates discover tech opportunities in India.

## What It Does

- Scrapes job listings across 8 targeted search queries
- Deduplicates results using a two-phase algorithm (URL-based + fuzzy matching)
- Exports clean data to JSON and CSV with timestamps
- Runs in ~18 seconds with ~70–75 unique jobs per execution

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 (requires 3.8+) |
| HTTP Client | requests==2.31.0 |
| Config | python-dotenv>=1.0.0 |
| External API | Serper.dev (Google for Jobs) |
| Storage | File-based (JSON + CSV) |

## Quick Start

```bash
# 1. Clone and enter the project
cd indeed-job-scraper

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo "SERPER_API_KEY=your_api_key_here" > .env

# 5. Verify setup
python3 test_api.py

# 6. Run the scraper
python3 scraper.py
```

Get your free Serper API key at [https://serper.dev](https://serper.dev) (2,500 searches/month free).

## Project Structure

```
indeed-job-scraper/
├── scraper.py          # Main entry point and orchestrator
├── serper_api.py       # Serper API client (jobs + search endpoints)
├── deduplicator.py     # Two-phase deduplication logic
├── config.py           # Search queries, thresholds, paths
├── test_api.py         # Manual API connectivity test
├── requirements.txt    # Python dependencies
├── .env                # API key (not committed)
└── output/             # Auto-created; timestamped JSON + CSV exports
```

## Configuration

Edit `config.py` to customize:
- `SEARCH_QUERIES` — list of search terms (default: 8 queries)
- `FUZZY_SIMILARITY_THRESHOLD` — dedup sensitivity (default: 0.9)
- `OUTPUT_DIR` — output folder path

Edit `scraper.py` to customize:
- `location` — target city (default: `"Bangalore, India"`)
- `results_per_query` — results per API call (default: 20)

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SERPER_API_KEY` | ✅ Yes | Your Serper.dev API key |

## Output

Each run produces two files in `output/`:
- `jobs_YYYYMMDD_HHMMSS.json` — full job records
- `jobs_YYYYMMDD_HHMMSS.csv` — spreadsheet-friendly export

Each job record contains: `title`, `company`, `location`, `link`, `salary`, `posted_date`, `description`, `source`.

## Current Status

**Phase 1 — MVP Complete.** Core scraping, deduplication, and export pipeline is fully functional.

See [FUTURE_UPDATES.md](FUTURE_UPDATES.md) for the roadmap toward a full Job Preparation Intelligence Platform.

## Troubleshooting

| Error | Fix |
|---|---|
| `API key not configured` | Check `.env` file exists, no spaces around `=` |
| `No module named 'requests'` | Run `source venv/bin/activate` then `pip install -r requirements.txt` |
| `No jobs found` | Verify internet connection and API key validity at serper.dev/dashboard |
| Permission errors | Run `mkdir -p output && chmod 755 output` |
