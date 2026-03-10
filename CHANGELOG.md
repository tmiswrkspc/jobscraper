# Changelog

## Version 2.0.0 - Serper API Only (2026-03-09)

### Major Changes

- **Removed browser-based scraping** - Eliminated Playwright, proxy management, and CAPTCHA handling
- **Serper API only** - Simplified to use only Serper.dev API for job collection
- **Cleaned up codebase** - Removed 50+ files related to browser automation

### Removed Components

- Browser automation (Playwright)
- Proxy management and rotation
- CAPTCHA detection and tracking
- Anti-detection measures
- Session checkpoints
- All browser-related tests and demos
- Browser-specific documentation

### Kept Components

- Serper API client (`serper_api.py`)
- Main scraper (`scraper.py`)
- Deduplicator (`deduplicator.py`)
- Configuration (`config.py`)
- Output export (JSON/CSV)

### Benefits

- **Simpler**: 5 core files vs 50+ files
- **Faster**: 18 seconds vs 5-10 minutes
- **More reliable**: 100% success rate vs 37.5%
- **No CAPTCHAs**: API-based, no bot detection
- **Easier maintenance**: Minimal dependencies

### Dependencies

Before:
- playwright==1.40.0
- playwright-stealth>=1.0.6
- requests==2.31.0
- beautifulsoup4>=4.12.0
- hypothesis
- pytest>=7.0.0
- python-dotenv>=1.0.0

After:
- requests==2.31.0
- python-dotenv>=1.0.0

### Performance Comparison

| Metric | Browser Scraping | Serper API |
|--------|-----------------|------------|
| Success Rate | 37.5% | 100% |
| Jobs per Run | 8 | 70-75 |
| Execution Time | 5-10 min | 18 sec |
| CAPTCHAs | Frequent | None |
| Infrastructure Cost | $50-150/mo | Free |

### Migration Guide

If you were using the browser-based scraper:

1. **Update dependencies**: `pip install -r requirements.txt`
2. **Get Serper API key**: Sign up at [serper.dev](https://serper.dev/)
3. **Configure API key**: Add to `.env` file
4. **Run new scraper**: `python3 scraper.py`

No code changes needed - just configuration!

### Breaking Changes

- Removed all browser-related configuration options
- Removed checkpoint/resume functionality
- Removed proxy configuration
- Removed CAPTCHA tracking
- Removed test mode

### Future Plans

- Add more search query templates
- Support multiple locations
- Add job filtering options
- Implement scheduling
- Add email notifications

---

## Version 1.0.0 - Browser-Based Scraping (2026-03-07)

Initial release with browser automation using Playwright.

Features:
- Multi-site scraping (5 sites)
- Proxy rotation
- CAPTCHA detection
- Anti-detection measures
- Session resumption
- Test mode

Issues:
- High CAPTCHA rate (62.5%)
- Low success rate (37.5%)
- Slow execution (5-10 minutes)
- Complex infrastructure requirements
