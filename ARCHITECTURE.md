# Architecture

## System Overview

Monolithic Python CLI application. Single-process, synchronous, stateless. No database, no web server, no background workers.

```
[User] → python3 scraper.py → [Serper API] → [Local files: JSON + CSV]
```

---

## Module Map

```
config.py          ← No imports. Pure constants. Used by all modules.
    ↓
serper_api.py      ← Wraps Serper HTTP API. Returns normalized job dicts.
    ↓
tavily_enricher.py ← Optional enrichment. Adds full descriptions, research.
    ↓
deduplicator.py    ← Two-phase dedup. Takes raw list, returns unique list.
    ↓
scraper.py         ← Orchestrator. Calls all modules. Writes output files.
```

### Module Responsibilities

**`config.py`** — Zero dependencies. Provides `SEARCH_QUERIES`, `FUZZY_SIMILARITY_THRESHOLD`, `OUTPUT_DIR`, `ENABLE_ENRICHMENT`, `MAX_ENRICHMENT_JOBS`. All other modules import from here.

**`serper_api.py`** — `SerperAPI` class. Makes HTTP POST requests to Serper. Tries `/jobs` endpoint first, falls back to `/search`. Normalizes both response shapes into a standard job dict.

**`tavily_enricher.py`** — `TavilyEnricher` class (optional). Enriches jobs with full content from URLs. Provides company research, learning resources, GitHub project discovery. Gracefully disabled if API key not configured.

**`deduplicator.py`** — `deduplicate_jobs(jobs)` function. Phase 1 removes URL duplicates (fast, O(n)). Phase 2 fuzzy-matches title+company pairs (slower, O(n²) — reduced by Phase 1 first).

**`scraper.py`** — `SerperJobScraper` class. Entry point. Loops over `SEARCH_QUERIES`, collects all raw jobs, optionally enriches with Tavily, calls deduplicator, writes JSON and CSV to `output/`.

---

## Data Flow

```
scraper.py: main()
  │
  ├── Load SEARCH_QUERIES from config.py
  ├── Validate SERPER_API_KEY from .env
  │
  └── FOR EACH query:
        │
        ├── SerperAPI.search_jobs(query, location)
        │     ├── Try: POST /jobs → _normalize_jobs_endpoint_results()
        │     └── Fallback: POST /search → _normalize_search_results()
        │
        └── Append results to all_jobs[]
  │
  ├── deduplicate_jobs(all_jobs)
  │     ├── Phase 1: Normalize URLs → remove exact matches
  │     └── Phase 2: SequenceMatcher on title+company → remove near-duplicates
  │
  ├── Write output/jobs_{timestamp}.json
  └── Write output/jobs_{timestamp}.csv
```

---

## External API

**Serper.dev** — Google for Jobs proxy API.

```
Primary:  POST https://google.serper.dev/jobs
Fallback: POST https://google.serper.dev/search

Auth:     Header X-API-KEY: {SERPER_API_KEY}
Timeout:  30 seconds
Limit:    2,500 requests/month (free tier)
```

The `/jobs` endpoint returns structured job data. The `/search` endpoint returns organic results that require company name extraction from title/snippet. Both are normalized to the same internal schema.

---

## Data Schema

**Standard job record (internal + output format)**:

```python
{
    "title":       str,        # Job title (required)
    "company":     str,        # Company name, "Unknown" if missing (required)
    "location":    str,        # Job location (required)
    "link":        str,        # Job posting URL — used as primary dedup key (required)
    "salary":      str | None, # Salary info (optional)
    "posted_date": str | None, # Relative date e.g. "2 days ago" (optional)
    "description": str,        # Job description snippet (required)
    "source":      str         # "serper_jobs_api" or "serper_search_api"
}
```

Records missing `title`, `company`, or `link` are dropped during normalization.

---

## Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| API vs browser scraping | Serper API | Browser had 62.5% CAPTCHA rate; API gives 100% success, 97% faster |
| Storage | JSON + CSV files | Simplicity; no setup; easy to inspect |
| Concurrency | Synchronous | Adequate for 8 queries; reduces complexity |
| Architecture | Monolith | Single developer, small scope, no scaling needs yet |
| Dedup order | URL first, fuzzy second | URL dedup is O(n) and cuts fuzzy comparisons by ~50% |

---

## What NOT to Change

- **Do not revert to browser scraping** — Serper API is a deliberate, proven replacement
- **Do not change the job dict schema** — breaks JSON/CSV export compatibility
- **Do not change output file naming pattern** — `{type}_{timestamp}.{ext}` is established convention
- **Do not hardcode `SERPER_API_KEY`** — must remain in `.env`
- **Do not remove two-phase dedup** — algorithm is proven effective; order matters

---

## Planned Evolution

```
Phase 1 (now)     CLI scraper → JSON/CSV
Phase 2 (planned) + LLM enrichment → SQLite DB
Phase 3 (planned) + GitHub API → Project recommendations
Phase 4 (planned) + FastAPI + React → Web dashboard
```
