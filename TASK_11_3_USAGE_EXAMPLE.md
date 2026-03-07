# Task 11.3: Network Error Handling Function - Usage Example

## Implementation Summary

The `handle_network_error(error, url, error_tracker)` function has been successfully implemented in `scraper.py`. This function provides comprehensive network error handling with the following features:

### Features Implemented

1. **Error Logging with Context**
   - Logs error with URL and timestamp
   - Includes error type and error message
   - Uses ERROR log level for visibility

2. **Error Rate Tracking**
   - Tracks error count per query
   - Calculates error rate (error_count / total_attempts)
   - Maintains state through error_tracker dictionary

3. **High Error Rate Warning**
   - Logs WARNING when error rate exceeds 50%
   - Includes query context and error statistics
   - Helps identify potential blocking or network issues

### Function Signature

```python
def handle_network_error(error: Exception, url: str, error_tracker: dict = None) -> dict:
    """
    Handles network errors by logging with context and tracking error rates.
    
    Args:
        error: Exception object representing the network error
        url: URL that failed to load
        error_tracker: Dictionary tracking errors per query (optional)
        
    Returns:
        Updated error_tracker dictionary with incremented counts
    """
```

### Error Tracker Structure

```python
{
    'query': str,           # Current search query
    'total_attempts': int,  # Total page navigation attempts
    'error_count': int,     # Number of failed attempts
    'error_rate': float     # Calculated error rate (0.0 to 1.0)
}
```

## Usage in Query Executor (Task 12.1)

When implementing the `execute_search_query` function in Task 12.1, the network error handler should be integrated as follows:

```python
def execute_search_query(page: Page, query: str, max_pages: int = 4) -> list:
    """
    Executes a single search query with pagination.
    
    This function demonstrates how to integrate handle_network_error
    for robust error handling during page navigation.
    """
    from playwright.errors import TimeoutError, Error as PlaywrightError
    
    # Initialize error tracker for this query
    error_tracker = {
        'query': query,
        'total_attempts': 0,
        'error_count': 0
    }
    
    # Construct search URL
    base_url = construct_search_url(query)
    
    # Generate pagination URLs
    paginated_urls = get_pagination_urls(base_url, max_pages)
    
    # Collect jobs from all pages
    all_jobs = []
    consecutive_captchas = 0
    
    for page_num, url in enumerate(paginated_urls, start=1):
        logger.info(f"Processing page {page_num}/{len(paginated_urls)} for query '{query}'")
        logger.info(f"URL: {url}")
        
        # Increment total attempts before navigation
        error_tracker['total_attempts'] += 1
        
        try:
            # Navigate to page with timeout
            page.goto(url, timeout=config.PAGE_LOAD_TIMEOUT)
            
            # Reset consecutive CAPTCHA count on successful load
            consecutive_captchas = 0
            
            # Apply anti-detection behavior
            apply_anti_detection_behavior(page)
            
            # Check for CAPTCHA
            if detect_captcha(page):
                consecutive_captchas = handle_captcha_detection(query, page_num, consecutive_captchas)
                continue  # Skip this page
            
            # Extract jobs from page
            jobs = extract_jobs_from_page(page)
            all_jobs.extend(jobs)
            
            logger.info(f"Extracted {len(jobs)} jobs from page {page_num}")
            
            # Random delay before next page
            if page_num < len(paginated_urls):
                random_delay(config.MIN_DELAY, config.MAX_DELAY)
                
        except (TimeoutError, PlaywrightError) as e:
            # Handle network error using the error handler
            error_tracker = handle_network_error(e, url, error_tracker)
            
            # Continue to next page (don't terminate session)
            continue
    
    # Log final statistics
    logger.info(f"Query '{query}' complete: {len(all_jobs)} jobs extracted")
    if error_tracker['error_count'] > 0:
        logger.info(
            f"Error summary: {error_tracker['error_count']}/{error_tracker['total_attempts']} "
            f"pages failed ({error_tracker['error_rate']:.1%})"
        )
    
    return all_jobs
```

## Key Integration Points

1. **Initialize Tracker**: Create error_tracker at the start of each query
2. **Increment Attempts**: Increment `total_attempts` before each `page.goto()`
3. **Catch Exceptions**: Catch `TimeoutError` and `PlaywrightError` during navigation
4. **Call Handler**: Pass exception, URL, and tracker to `handle_network_error()`
5. **Continue Execution**: Use `continue` to skip failed page and proceed to next
6. **Log Summary**: Report error statistics at end of query

## Testing Results

All tests passed successfully:

✅ Test 1: Error logged with URL and timestamp (25% error rate)
✅ Test 2: Error rate calculated correctly (50% error rate)
✅ Test 3: Warning triggered when rate exceeds 50% (75% error rate)
✅ Test 4: Tracker initialized correctly when None is passed

## Requirements Validated

- ✅ **Requirement 9.1**: Logs error with URL when network timeout occurs
- ✅ **Requirement 9.3**: Logs error with URL when page fails to load
- ✅ **Property 21**: Error logging includes contextual information (URL, timestamp)

## Next Steps

When implementing Task 12.1 (Search Query Executor):
1. Import the `handle_network_error` function
2. Initialize error tracker for each query
3. Wrap `page.goto()` calls in try-except blocks
4. Call `handle_network_error()` in exception handlers
5. Continue to next page after errors (don't terminate)
6. Log error summary at end of each query
