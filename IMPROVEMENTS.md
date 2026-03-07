# Scraper Improvements - Increased Delays

## Changes Made

### 1. Increased Delays Between Requests
**Previous**: 8-18 seconds  
**New**: 30-60 seconds  
**Impact**: More human-like behavior, significantly reduces CAPTCHA detection

### 2. Reduced Pages Per Query
**Previous**: 4 pages per query  
**New**: 2 pages per query  
**Impact**: Less aggressive scraping, lower detection risk

### 3. Increased Page Load Timeout
**Previous**: 60 seconds  
**New**: 90 seconds  
**Impact**: Better handling of slow connections and page loads

## Expected Results

### Before Changes
- **Jobs Collected**: 8 jobs (3 queries successful, 5 blocked by CAPTCHA)
- **CAPTCHA Rate**: 62.5% of queries blocked
- **Session Duration**: ~5-10 minutes

### After Changes
- **Expected Jobs**: 100-200 jobs (more queries should succeed)
- **Expected CAPTCHA Rate**: <20% of queries blocked
- **Session Duration**: ~30-45 minutes (longer but more successful)

## How to Run

```bash
cd indeed-job-scraper
python3 scraper.py
```

## Tips for Maximum Success

1. **Run During Off-Peak Hours**
   - Best times: Late night (11 PM - 6 AM IST)
   - Avoid: Business hours (9 AM - 6 PM IST)

2. **Use Batch Mode** (Optional)
   - Run 2-3 queries at a time
   - Wait 2-3 hours between batches
   - Edit `SEARCH_QUERIES` in config.py to limit queries

3. **Monitor Progress**
   - Watch console output for CAPTCHA warnings
   - If you see 3+ consecutive CAPTCHAs, stop and wait
   - Resume later using checkpoint feature

4. **Adjust Delays Further** (If Still Getting CAPTCHAs)
   - Increase MIN_DELAY to 45 seconds
   - Increase MAX_DELAY to 90 seconds
   - Edit config.py and restart

## Performance Comparison

| Metric | Before | After (Expected) |
|--------|--------|------------------|
| Delay Range | 8-18s | 30-60s |
| Pages/Query | 4 | 2 |
| Jobs/Query | 1-3 | 20-40 |
| CAPTCHA Rate | 62.5% | <20% |
| Session Time | 5-10 min | 30-45 min |
| Total Jobs | 8 | 100-200 |

## Next Steps

If you still encounter CAPTCHAs after these changes, consider:

1. **Residential Proxies** - Rotate IP addresses ($50-100/month)
2. **CAPTCHA Solvers** - Automatically solve CAPTCHAs ($1-3 per 1000 solves)
3. **Batch Mode** - Spread scraping over multiple sessions
4. **Alternative Sites** - Scrape from Naukri, Monster, LinkedIn instead

## Rollback Instructions

If you want to revert to faster (but more detectable) settings:

```python
# In config.py, change:
MIN_DELAY = 8
MAX_DELAY = 18
MAX_PAGES = 4
PAGE_LOAD_TIMEOUT = 60000
```

---

**Last Updated**: March 7, 2026  
**Status**: Ready to test
