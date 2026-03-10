# Quick Start Guide

Get up and running with the job scraper in 5 minutes.

## Step 1: Install Dependencies

```bash
cd indeed-job-scraper
pip install -r requirements.txt
```

## Step 2: Get API Key

1. Go to [serper.dev](https://serper.dev/)
2. Sign up for free account
3. Copy your API key from the dashboard

## Step 3: Configure API Key

Create a `.env` file:

```bash
echo "SERPER_API_KEY=your_api_key_here" > .env
```

Replace `your_api_key_here` with your actual API key.

## Step 4: Test API

```bash
python3 test_api.py
```

You should see:
```
✓ API key configured
✓ Found 10 jobs
```

## Step 5: Run Full Scraper

```bash
python3 scraper.py
```

This will:
- Execute 8 search queries
- Collect 100+ jobs
- Save to `output/jobs_*.json` and `output/jobs_*.csv`

## Customization

### Change Search Queries

Edit `config.py`:

```python
SEARCH_QUERIES = [
    "your custom query",
    "another query",
]
```

### Change Location

Edit `scraper.py`:

```python
scraper = SerperJobScraper(location="Mumbai, India")
```

### Get More Results

Edit `scraper.py`:

```python
jobs = scraper.scrape_all_queries(
    queries=SEARCH_QUERIES,
    results_per_query=50  # Increase from 20 to 50
)
```

## Troubleshooting

### "API key not configured"

- Check `.env` file exists
- Verify API key is correct
- No spaces or quotes around the key

### "No jobs found"

- Check internet connection
- Verify API key is valid
- Try different search queries

### Rate limit exceeded

- Check usage at [serper.dev/dashboard](https://serper.dev/dashboard)
- Free tier: 2,500 searches/month
- Reduce query frequency or upgrade plan

## Next Steps

- Read `README.md` for full documentation
- Check `SERPER_WORKFLOW_PLAN.md` for detailed workflow
- Customize queries in `config.py`
- Schedule regular runs with cron

## Support

- API Docs: https://serper.dev/docs
- Dashboard: https://serper.dev/dashboard
