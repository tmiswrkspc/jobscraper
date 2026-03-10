# Architecture Decision Records

Key decisions made during development. Read this before making structural changes — these choices were deliberate.

---

## ADR-001: Serper API Over Browser Scraping

**Status**: Active  
**Date**: 2026

**Context**: The original approach used browser automation (Selenium/Playwright) to scrape job listings directly.

**Problem**: Browser scraping had a 62.5% CAPTCHA failure rate, yielding only 37.5% success. Each run took 5–10 minutes.

**Decision**: Switched entirely to Serper.dev API.

**Outcome**:
- 100% success rate
- ~18 second execution (97% faster)
- No proxy or CAPTCHA solver infrastructure needed
- Trade-off: dependency on Serper's free tier (2,500 searches/month)

**Do not revert to browser scraping.**

---

## ADR-002: File-Based Storage (JSON + CSV)

**Status**: Active, planned for migration  
**Date**: 2026

**Context**: Needed a way to persist job data between runs.

**Decision**: Write timestamped JSON and CSV files to `output/` directory.

**Rationale**: Zero setup, human-readable, easy to inspect, no infrastructure dependency.

**Future**: Will migrate to SQLite (then PostgreSQL) once historical tracking and enrichment features are needed. The job dict schema is the contract — don't change field names before the database migration is designed.

---

## ADR-003: Synchronous API Calls

**Status**: Active, may change  
**Date**: 2026

**Context**: 8 search queries × 2 possible endpoints = up to 16 API calls per run.

**Decision**: Use synchronous `requests` calls in a simple for-loop.

**Rationale**: Adequate for current scale. Async adds complexity without benefit at 8 queries.

**Future**: If queries scale to 30+, switch to `asyncio` + `aiohttp`. Do not add async prematurely.

---

## ADR-004: Two-Phase Deduplication

**Status**: Active  
**Date**: 2026

**Context**: Multiple queries return overlapping results. Needed reliable deduplication without excessive compute.

**Decision**: Phase 1 = URL normalization (exact match, O(n)). Phase 2 = fuzzy title+company matching via `difflib.SequenceMatcher` (O(n²)).

**Rationale**: Running Phase 1 first eliminates ~50% of comparisons before the expensive Phase 2. The 90% similarity threshold (`FUZZY_SIMILARITY_THRESHOLD = 0.9`) was tuned to avoid false positives.

**Do not remove either phase or change the order.** Do not lower the threshold below 0.85 without testing.

---

## ADR-005: Monolithic Architecture

**Status**: Active, planned for evolution  
**Date**: 2026

**Context**: Single developer, early-stage MVP.

**Decision**: Single Python application, all modules in one directory, no services.

**Rationale**: Simplicity wins at this scale. Microservices would add operational overhead with no benefit.

**Future**: May split into scraper service, enrichment service, and API server in Phase 3. No splitting until the use case clearly demands it.

---

## ADR-006: Config Centralization in `config.py`

**Status**: Active  
**Date**: 2026

**Decision**: All constants (queries, thresholds, paths) live in `config.py`. Secrets live in `.env`. No other module has hardcoded values.

**Rationale**: Single place to change behavior without touching logic. Prevents scattered magic numbers.

**Do not add constants to any module other than `config.py`.**

---

## ADR-007: Graceful Degradation on API Failure

**Status**: Active  
**Date**: 2026

**Decision**: All API call failures return empty lists. Errors are logged but never raised to the caller.

**Rationale**: A failed query should not abort the entire scraping run. Partial results are better than no results.

**Do not change API error handling to raise exceptions.** If a query fails, log it and continue.

---

## ADR-008: Tavily AI for Optional Job Enrichment

**Status**: Active  
**Date**: 2026-03-09

**Context**: Phase 1 provides basic job listings (title, company, location, link, snippet). To move toward the Job Preparation Intelligence Platform vision, we need richer data: full job descriptions, company research, learning resources, and GitHub project recommendations.

**Decision**: Integrate Tavily AI as an optional enrichment layer.

**Implementation**:
- New module: `tavily_enricher.py`
- Graceful degradation: Works without Tavily API key (logs info, continues)
- Limited enrichment: Max 10 jobs per run (configurable in `config.py`)
- Features: Full job content extraction, company research, learning resources, GitHub discovery

**Rationale**:
- Tavily provides AI-powered content extraction and research capabilities
- Optional integration respects the "minimal dependencies" constraint
- Free tier (1,000 requests/month) is adequate for enrichment use case
- Enables Phase 2 features without requiring LLM integration yet

**Trade-offs**:
- Additional dependency (`tavily-python`)
- Additional API key to manage
- API quota to monitor (1,000/month)
- Enrichment adds ~2-5 seconds per job

**Future**: Tavily enrichment is a stepping stone to full LLM-powered analysis (Phase 2). May be replaced or augmented with OpenAI/Claude integration later.
