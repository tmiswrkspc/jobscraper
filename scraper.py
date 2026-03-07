"""
Indeed Job Scraper - High-Volume Stealthy Web Scraping System

This module implements a sophisticated web scraping system for extracting job listings
from Indeed India (in.indeed.com). The scraper is designed to collect 1000-2000 unique
job records per session while implementing advanced anti-detection techniques to avoid
rate limiting and blocking.

Key Features:
- Targets technology jobs in Bangalore and remote positions across India
- Executes 8 predefined search queries with pagination support (up to 4 pages per query)
- Implements human-like browsing behavior (random delays, scrolling, mouse movements)
- Handles errors gracefully (network failures, CAPTCHAs, selector changes)
- Supports session resumability through checkpoint-based recovery
- Exports data to both JSON and CSV formats with proper encoding

Architecture:
The scraper follows a modular design with clear separation of concerns:
- Browser Profile Manager: Configures Playwright with Indian locale and stealth settings
- Anti-Detection Module: Implements random delays, scrolling, and mouse movements
- Search Query Executor: Coordinates query execution and pagination
- Data Extractor: Parses HTML to extract structured job information
- Deduplicator: Removes duplicate job records based on normalized URLs
- Data Exporter: Writes results to JSON and CSV formats
- Session Manager: Handles checkpointing and session resumption
- Error Handler: Manages network failures, CAPTCHA detection, and selector validation

Usage:
    python scraper.py

Requirements:
- Python 3.8+
- Playwright 1.40.0
- playwright-stealth 1.0.0
- Hypothesis (for property-based testing)

Configuration:
All configuration parameters are defined in config.py including search queries,
delay ranges, pagination settings, CSS selectors, and output paths.

Author: Indeed Job Scraper Team
Last Updated: March 2026
"""

from playwright.sync_api import sync_playwright, Browser, Page
import config
from config import (
    LOCALE, TIMEZONE, VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
    BLOCKED_RESOURCE_TYPES, BLOCKED_URL_PATTERNS
)

# Try to import playwright-stealth for anti-detection
# Note: playwright-stealth may not be compatible with all Playwright versions
# If import fails, the browser will still work but without stealth plugins
try:
    from playwright_stealth import Stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
    print("Warning: playwright-stealth not available. Browser will run without stealth plugins.")
    print("Install with: pip install playwright-stealth")


def create_browser_profile(playwright_instance) -> Browser:
    """
    Creates a configured browser instance with Indian locale and stealth settings.
    
    This function initializes a Playwright browser with settings designed to appear
    as a legitimate Indian user browsing Indeed. It configures locale, timezone,
    viewport, and implements resource blocking to reduce bandwidth and detection surface.
    
    Args:
        playwright_instance: Active Playwright instance from sync_playwright().start()
        
    Returns:
        Configured Browser object with stealth plugins and resource blocking
        
    Configuration:
        - Locale: en-IN (Indian English)
        - Timezone: Asia/Kolkata
        - Viewport: 1920x1080 pixels
        - Headless: False (visible browser for debugging)
        - Stealth: Applied if playwright-stealth is available
        - Resource Blocking: Images, fonts, analytics trackers, ad trackers
        
    Example:
        >>> with sync_playwright() as p:
        ...     browser = create_browser_profile(p)
        ...     page = browser.new_page()
        ...     # Use page for scraping
        ...     browser.close()
    """
    # Launch browser with Indian locale and timezone settings
    # headless=False makes the browser visible for debugging
    browser = playwright_instance.chromium.launch(
        headless=False,  # Visible browser for debugging
        args=[
            '--disable-blink-features=AutomationControlled',  # Hide automation flags
            '--disable-dev-shm-usage',  # Overcome limited resource problems
            '--no-sandbox',  # Required for some environments
        ]
    )
    
    # Create browser context with Indian locale and timezone
    context = browser.new_context(
        locale=LOCALE,
        timezone_id=TIMEZONE,
        viewport={'width': VIEWPORT_WIDTH, 'height': VIEWPORT_HEIGHT},
        user_agent=None,  # Let Playwright use default Chrome user agent
    )
    
    # Create a page to apply stealth and resource blocking
    page = context.new_page()
    
    # Apply playwright-stealth if available
    if STEALTH_AVAILABLE:
        stealth_config = Stealth(
            navigator_languages_override=('en-IN', 'en'),  # Match Indian locale
            navigator_platform_override='Linux x86_64',  # Common platform
        )
        stealth_config.apply_stealth_sync(page)
        print("Stealth plugins applied successfully")
    
    # Implement resource blocking using page.route()
    def block_resources(route):
        """
        Route handler to block unnecessary resources.
        Blocks images, fonts, analytics trackers, and ad trackers.
        """
        request = route.request
        resource_type = request.resource_type
        url = request.url
        
        # Block by resource type (images, fonts)
        if resource_type in BLOCKED_RESOURCE_TYPES:
            route.abort()
            return
        
        # Block by URL pattern (analytics, trackers, ads)
        for pattern in BLOCKED_URL_PATTERNS:
            # Convert glob pattern to simple substring match
            pattern_check = pattern.replace('*', '')
            if pattern_check in url:
                route.abort()
                return
        
        # Allow all other requests
        route.continue_()
    
    # Register the route handler for all requests
    page.route('**/*', block_resources)
    
    print(f"Browser profile configured: locale={LOCALE}, timezone={TIMEZONE}, viewport={VIEWPORT_WIDTH}x{VIEWPORT_HEIGHT}")
    print(f"Resource blocking enabled: {BLOCKED_RESOURCE_TYPES} + analytics/ad trackers")
    
    # Note: We return the browser, not the page or context
    # The caller will need to access context and create pages as needed
    # For this implementation, we're storing the context on the browser object
    # so it can be accessed later
    browser._scraper_context = context
    browser._scraper_page = page
    
    return browser


# ============================================================================
# Anti-Detection Module
# ============================================================================

import time
import random


def random_delay(min_seconds: float, max_seconds: float) -> None:
    """
    Waits for a random duration between min and max seconds.
    
    This function implements rate limiting by introducing random delays between
    actions to mimic human browsing behavior. The randomization helps avoid
    detection patterns that could flag the scraper as automated.
    
    Args:
        min_seconds: Minimum delay duration in seconds (inclusive)
        max_seconds: Maximum delay duration in seconds (inclusive)
        
    Returns:
        None
        
    Example:
        >>> random_delay(8, 18)  # Waits between 8-18 seconds
        >>> # Continues after random delay
        
    Note:
        - Uses random.uniform() for continuous distribution
        - Configured for 8-18 second delays per requirements 3.1, 3.2
        - Called between page navigations and actions
        
    Requirements:
        - 3.1: Rate limiter shall wait random duration 8-18s between page navigation
        - 3.2: Rate limiter shall wait random duration 8-18s between actions
    """
    delay = random.uniform(min_seconds, max_seconds)
    time.sleep(delay)


def simulate_human_scrolling(page: Page) -> None:
    """
    Performs slow, variable-speed scrolling to simulate human reading behavior.
    
    This function mimics natural human scrolling patterns by dividing the page into
    random-sized chunks and scrolling through them with variable speeds and pauses.
    Occasionally scrolls up slightly to simulate re-reading behavior.
    
    Args:
        page: Playwright Page object with loaded content
        
    Returns:
        None
        
    Scrolling Strategy:
        1. Calculate total page height using JavaScript
        2. Divide height into random chunks (100-300px each)
        3. Scroll each chunk with variable speed
        4. Pause randomly between chunks (0.1-0.3s)
        5. Occasionally scroll up slightly (10% chance) to mimic re-reading
        
    Example:
        >>> page.goto("https://in.indeed.com/jobs?q=software+engineer")
        >>> simulate_human_scrolling(page)  # Scrolls through entire page naturally
        
    Note:
        - Chunk sizes randomized to avoid pattern detection
        - Scroll speeds vary to simulate acceleration/deceleration
        - Upward scrolls add realism to browsing behavior
        - Triggers lazy-loaded content during scroll
        
    Requirements:
        - 3.3: Anti-detection module shall perform slow scrolling simulating human reading
        - 3.5: Anti-detection module shall vary scroll speeds with random acceleration/deceleration
        - 3.7: Anti-detection module shall execute scrolling before data extraction
    """
    # Calculate total page height
    page_height = page.evaluate("() => document.body.scrollHeight")
    
    # Start from top of page
    current_position = 0
    
    # Scroll through page in random chunks
    while current_position < page_height:
        # Generate random chunk size (100-300px)
        chunk_size = random.randint(100, 300)
        
        # Calculate next scroll position
        next_position = min(current_position + chunk_size, page_height)
        
        # Scroll to next position with smooth behavior
        page.evaluate(f"window.scrollTo({{ top: {next_position}, behavior: 'smooth' }})")
        
        # Random pause between chunks (0.1-0.3s) to simulate reading
        pause_duration = random.uniform(0.1, 0.3)
        time.sleep(pause_duration)
        
        # 10% chance to scroll up slightly (mimic re-reading)
        if random.random() < 0.1:
            # Scroll up by 50-150px
            scroll_up_amount = random.randint(50, 150)
            scroll_up_position = max(0, next_position - scroll_up_amount)
            page.evaluate(f"window.scrollTo({{ top: {scroll_up_position}, behavior: 'smooth' }})")
            
            # Brief pause after scrolling up
            time.sleep(random.uniform(0.1, 0.2))
            
            # Continue from where we scrolled up
            current_position = scroll_up_position
        else:
            current_position = next_position
    
    # Final pause at bottom of page
    time.sleep(random.uniform(0.2, 0.4))


def simulate_mouse_movement(page: Page) -> None:
    """
    Performs random mouse movements across the page to simulate human interaction.
    
    This function generates random coordinates within the viewport and moves the mouse
    along curved paths with variable speeds. The movement patterns are randomized to
    avoid detection as automated behavior.
    
    Args:
        page: Playwright Page object with loaded content
        
    Returns:
        None
        
    Movement Strategy:
        1. Generate 3-7 random coordinates within viewport bounds
        2. Move mouse along curved paths (using intermediate points)
        3. Vary movement speed (faster in middle, slower at endpoints)
        4. Add small pauses at some waypoints to simulate reading/hovering
        
    Example:
        >>> page.goto("https://in.indeed.com/jobs?q=software+engineer")
        >>> simulate_mouse_movement(page)  # Moves mouse naturally across page
        
    Note:
        - Coordinates are constrained to viewport dimensions (1920x1080)
        - Curved paths created using intermediate waypoints
        - Speed variation simulates natural mouse acceleration/deceleration
        - Occasional pauses add realism to interaction patterns
        
    Requirements:
        - 3.4: Anti-detection module shall perform random mouse movements
        - 3.6: Anti-detection module shall vary mouse movement trajectories
    """
    from config import (
        VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
        MOUSE_MOVEMENT_POINTS_MIN, MOUSE_MOVEMENT_POINTS_MAX
    )
    
    # Generate random number of movement points (3-7)
    num_points = random.randint(MOUSE_MOVEMENT_POINTS_MIN, MOUSE_MOVEMENT_POINTS_MAX)
    
    # Generate random coordinates within viewport
    target_points = []
    for _ in range(num_points):
        x = random.randint(50, VIEWPORT_WIDTH - 50)  # Leave margin from edges
        y = random.randint(50, VIEWPORT_HEIGHT - 50)
        target_points.append((x, y))
    
    # Get starting position (center of viewport)
    current_x = VIEWPORT_WIDTH // 2
    current_y = VIEWPORT_HEIGHT // 2
    
    # Move mouse to each target point along curved path
    for target_x, target_y in target_points:
        # Calculate distance to target
        dx = target_x - current_x
        dy = target_y - current_y
        
        # Generate curved path using intermediate waypoints
        # Use 3-5 intermediate points for smooth curve
        num_steps = random.randint(3, 5)
        
        for step in range(num_steps + 1):
            # Calculate progress along path (0.0 to 1.0)
            progress = step / num_steps
            
            # Apply easing function for variable speed
            # Slower at start and end, faster in middle
            if progress < 0.5:
                # Ease in (quadratic)
                eased_progress = 2 * progress * progress
            else:
                # Ease out (quadratic)
                eased_progress = 1 - 2 * (1 - progress) * (1 - progress)
            
            # Add curve to path using sine wave offset
            # This creates a natural arc instead of straight line
            curve_offset_x = random.uniform(-30, 30) * (1 - abs(2 * progress - 1))
            curve_offset_y = random.uniform(-30, 30) * (1 - abs(2 * progress - 1))
            
            # Calculate intermediate position with curve
            intermediate_x = current_x + dx * eased_progress + curve_offset_x
            intermediate_y = current_y + dy * eased_progress + curve_offset_y
            
            # Ensure coordinates stay within viewport bounds
            intermediate_x = max(0, min(VIEWPORT_WIDTH, intermediate_x))
            intermediate_y = max(0, min(VIEWPORT_HEIGHT, intermediate_y))
            
            # Move mouse to intermediate position
            page.mouse.move(intermediate_x, intermediate_y)
            
            # Small delay between movements (faster in middle, slower at endpoints)
            if progress < 0.2 or progress > 0.8:
                # Slower at start and end
                time.sleep(random.uniform(0.02, 0.05))
            else:
                # Faster in middle
                time.sleep(random.uniform(0.01, 0.03))
        
        # Update current position
        current_x = target_x
        current_y = target_y
        
        # 30% chance to pause briefly at this point (simulate reading/hovering)
        if random.random() < 0.3:
            time.sleep(random.uniform(0.1, 0.3))
    
    # Final small pause after all movements
    time.sleep(random.uniform(0.05, 0.15))


def apply_anti_detection_behavior(page: Page) -> None:
    """
    Applies full anti-detection suite: scrolling and mouse movements.
    
    This function orchestrates the complete anti-detection behavior by executing
    both scrolling and mouse movement simulations in sequence. It ensures that
    scrolling completes before returning, which is critical for triggering
    lazy-loaded content before data extraction begins.
    
    Args:
        page: Playwright Page object with loaded content
        
    Returns:
        None
        
    Execution Order:
        1. Simulate human scrolling (completes fully before proceeding)
        2. Simulate mouse movements
        3. Return (guarantees scrolling is complete)
        
    Example:
        >>> page.goto("https://in.indeed.com/jobs?q=software+engineer")
        >>> apply_anti_detection_behavior(page)  # Scrolls and moves mouse
        >>> jobs = extract_jobs_from_page(page)  # Extract after anti-detection
        
    Note:
        - Called after each page load before data extraction
        - Scrolling must complete first to trigger lazy-loaded content
        - Sequential execution ensures proper ordering (Property 6)
        - Both functions are synchronous, so completion is guaranteed
        
    Requirements:
        - 3.3: Anti-detection module shall perform slow scrolling
        - 3.4: Anti-detection module shall perform random mouse movements
        - 3.7: Anti-detection module shall execute scrolling before data extraction
        
    Validates:
        - Property 6: Scroll Before Extract Ordering
    """
    # Execute scrolling first - this must complete before extraction
    # Scrolling triggers lazy-loaded content and simulates reading behavior
    simulate_human_scrolling(page)
    
    # Execute mouse movements after scrolling
    # Mouse movements add additional human-like interaction patterns
    simulate_mouse_movement(page)
    
    # Function returns only after both operations complete
    # This guarantees scrolling is done before data extraction begins



# ============================================================================
# URL Construction and Pagination Handler
# ============================================================================

import urllib.parse


def construct_search_url(query: str) -> str:
    """
    Constructs a search URL for Indeed India with the given query.
    
    This function builds a properly formatted Indeed search URL targeting the
    in.indeed.com domain with URL-encoded query parameters and date sorting.
    The URL is constructed to retrieve the newest job listings first.
    
    Args:
        query: Search query string (e.g., "software engineer Bangalore")
        
    Returns:
        Complete search URL string with encoded query and sort parameter
        
    URL Structure:
        https://in.indeed.com/jobs?q={encoded_query}&sort=date
        
    Example:
        >>> construct_search_url("software engineer Bangalore")
        'https://in.indeed.com/jobs?q=software+engineer+Bangalore&sort=date'
        
        >>> construct_search_url("python developer")
        'https://in.indeed.com/jobs?q=python+developer&sort=date'
        
    Note:
        - Uses urllib.parse.quote_plus() for proper URL encoding
        - Spaces are encoded as '+' signs
        - Special characters are percent-encoded
        - Always includes '&sort=date' to get newest listings first
        - Targets in.indeed.com domain (Indeed India)
        
    Requirements:
        - 2.1: Scraper shall execute searches for predefined search queries
        - 2.2: Scraper shall append "&sort=date" parameter to search URL
        - 2.4: Scraper shall construct search URLs targeting in.indeed.com domain
        
    Validates:
        - Property 1: Search URL Construction
          For any search query string, the constructed URL should contain
          the in.indeed.com domain, the encoded query parameter, and the
          "&sort=date" parameter.
    """
    # Base URL for Indeed India job search
    base_url = "https://in.indeed.com/jobs"
    
    # Encode the query parameter using quote_plus (spaces become '+')
    encoded_query = urllib.parse.quote_plus(query)
    
    # Construct full URL with query and sort parameters
    # Format: https://in.indeed.com/jobs?q={encoded_query}&sort=date
    search_url = f"{base_url}?q={encoded_query}&sort=date"
    
    return search_url


def get_pagination_urls(base_query_url: str, max_pages: int = 4) -> list:
    """
    Generates paginated URLs for a search query.
    
    This function takes a base search URL and generates a list of URLs for
    multiple pages by appending pagination start parameters. Indeed uses a
    'start' parameter to paginate results, with each page showing 50 results.
    
    Args:
        base_query_url: Base search URL with query and sort parameters
                       (e.g., "https://in.indeed.com/jobs?q=software+engineer&sort=date")
        max_pages: Maximum number of pages to generate (default 4)
        
    Returns:
        List of URLs with start parameters [0, 50, 100, 150] for 4 pages
        
    Pagination Logic:
        - Page 1: start=0 (results 1-50)
        - Page 2: start=50 (results 51-100)
        - Page 3: start=100 (results 101-150)
        - Page 4: start=150 (results 151-200)
        
    Example:
        >>> base_url = construct_search_url("software engineer Bangalore")
        >>> urls = get_pagination_urls(base_url, max_pages=4)
        >>> len(urls)
        4
        >>> urls[0]
        'https://in.indeed.com/jobs?q=software+engineer+Bangalore&sort=date&start=0'
        >>> urls[3]
        'https://in.indeed.com/jobs?q=software+engineer+Bangalore&sort=date&start=150'
        
    Note:
        - Uses START_VALUES from config.py: [0, 50, 100, 150]
        - Each page shows RESULTS_PER_PAGE (50) results
        - Start parameter increments by 50 for each page
        - Maximum of 4 pages per query to balance volume and detection risk
        - URLs are generated but not validated (validation happens during navigation)
        
    Requirements:
        - 2.3: Pagination handler shall navigate through pages using start parameters 0, 50, 100, 150
        - 2.5: Scraper shall extract job records from minimum 3 pages and maximum 4 pages
        
    Validates:
        - Property 2: Pagination URL Generation
          For any search query, the pagination handler should generate URLs with
          start parameters [0, 50, 100, 150], resulting in 4 pages.
    """
    from config import START_VALUES
    
    # Generate paginated URLs by appending start parameter
    paginated_urls = []
    
    # Use the configured START_VALUES (default: [0, 50, 100, 150])
    # Limit to max_pages to allow flexibility
    for start_value in START_VALUES[:max_pages]:
        # Append start parameter to base URL
        # Check if URL already has query parameters (should always be true)
        if '?' in base_query_url:
            paginated_url = f"{base_query_url}&start={start_value}"
        else:
            # Fallback if no query parameters (shouldn't happen with our construct_search_url)
            paginated_url = f"{base_query_url}?start={start_value}"
        
        paginated_urls.append(paginated_url)
    
    return paginated_urls


# ============================================================================
# Data Extractor Component
# ============================================================================

import re
import logging
from typing import Optional, Dict
from urllib.parse import urljoin

# Configure logging for extraction warnings
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def extract_single_job(job_element) -> Optional[Dict]:
    """
    Extracts data from a single job card element.
    
    This function parses a job listing element and extracts all available fields
    using a fallback selector strategy. It validates required fields, normalizes
    text content, and converts relative URLs to absolute URLs.
    
    Args:
        job_element: Playwright ElementHandle for a job card container
        
    Returns:
        Job record dictionary with extracted fields, or None if validation fails
        
    Job Record Schema:
        {
            'title': str,           # Required: Job title
            'company': str,         # Required: Company name
            'location': str,        # Required: Job location
            'link': str,            # Required: Absolute URL to job posting
            'salary': str | None,   # Optional: Salary information
            'posted_date': str | None,  # Optional: When job was posted
            'description': str | None   # Optional: Job description snippet
        }
        
    Extraction Strategy:
        - Uses multiple fallback selectors per field (defined in config.py)
        - Tries each selector in order until one succeeds
        - Logs warnings when primary selectors fail
        - Validates required fields are non-empty
        - Normalizes text: trims whitespace, collapses multiple spaces
        - Converts relative URLs to absolute URLs
        - Returns None if any required field is missing or invalid
        
    Example:
        >>> page.goto("https://in.indeed.com/jobs?q=software+engineer")
        >>> job_cards = page.query_selector_all('div.job_seen_beacon')
        >>> for card in job_cards:
        ...     job = extract_single_job(card)
        ...     if job:
        ...         print(f"Found job: {job['title']} at {job['company']}")
        
    Note:
        - Selectors verified March 2026 (see config.py)
        - Required fields: title, company, location, link
        - Optional fields: salary, posted_date, description
        - Invalid records are logged and skipped (return None)
        - URL validation ensures proper format
        
    Requirements:
        - 4.1: Scraper shall extract job title for all job listings
        - 4.2: Scraper shall extract company name for all job listings
        - 4.3: Scraper shall extract location for all job listings
        - 4.4: Scraper shall extract full job link URL for all job listings
        - 4.5: Scraper shall extract short description or snippet for all job listings
        - 4.6: Scraper shall extract salary value where displayed
        - 4.7: Scraper shall extract posted date value where displayed
        - 4.8: Scraper shall store extracted data as Job_Record objects with consistent field names
        - 4.9: Scraper shall ensure job link is an absolute URL
        - 18.1: Scraper shall verify job title is not empty before adding to Job_Record
        - 18.2: Scraper shall verify company name is not empty before adding to Job_Record
        - 18.3: Scraper shall verify URL format is valid before adding to Job_Record
        - 18.6: Scraper shall trim whitespace from all extracted text fields
        - 18.7: Scraper shall normalize whitespace by replacing multiple spaces with single spaces
        
    Validates:
        - Property 7: Required Field Extraction
        - Property 8: Conditional Field Extraction
        - Property 9: Absolute URL Conversion
        - Property 10: Consistent Field Names
        - Property 33: URL Validation
        - Property 34: Text Normalization
    """
    from config import SELECTORS
    
    # Initialize job record with None values
    job_record = {
        'title': None,
        'company': None,
        'location': None,
        'link': None,
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    # ========================================================================
    # Extract Title (Required Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['title']:
        try:
            title_element = job_element.query_selector(selector)
            if title_element:
                title_text = title_element.inner_text()
                if title_text and title_text.strip():
                    job_record['title'] = normalize_text(title_text)
                    break
        except Exception as e:
            logger.debug(f"Title selector '{selector}' failed: {e}")
            continue
    
    if not job_record['title']:
        logger.warning("Failed to extract title - trying all selectors")
        return None
    
    # ========================================================================
    # Extract Company (Required Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['company']:
        try:
            company_element = job_element.query_selector(selector)
            if company_element:
                company_text = company_element.inner_text()
                if company_text and company_text.strip():
                    job_record['company'] = normalize_text(company_text)
                    break
        except Exception as e:
            logger.debug(f"Company selector '{selector}' failed: {e}")
            continue
    
    if not job_record['company']:
        logger.warning(f"Failed to extract company for job: {job_record['title']}")
        return None
    
    # ========================================================================
    # Extract Location (Required Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['location']:
        try:
            location_element = job_element.query_selector(selector)
            if location_element:
                location_text = location_element.inner_text()
                if location_text and location_text.strip():
                    job_record['location'] = normalize_text(location_text)
                    break
        except Exception as e:
            logger.debug(f"Location selector '{selector}' failed: {e}")
            continue
    
    if not job_record['location']:
        logger.warning(f"Failed to extract location for job: {job_record['title']} at {job_record['company']}")
        return None
    
    # ========================================================================
    # Extract Job Link (Required Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['link']:
        try:
            link_element = job_element.query_selector(selector)
            if link_element:
                href = link_element.get_attribute('href')
                if href:
                    # Convert relative URL to absolute URL
                    absolute_url = urljoin('https://in.indeed.com', href)
                    
                    # Validate URL format
                    if is_valid_url(absolute_url):
                        job_record['link'] = absolute_url
                        break
        except Exception as e:
            logger.debug(f"Link selector '{selector}' failed: {e}")
            continue
    
    if not job_record['link']:
        logger.warning(f"Failed to extract link for job: {job_record['title']} at {job_record['company']}")
        return None
    
    # ========================================================================
    # Extract Salary (Optional Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['salary']:
        try:
            salary_element = job_element.query_selector(selector)
            if salary_element:
                salary_text = salary_element.inner_text()
                if salary_text and salary_text.strip():
                    job_record['salary'] = normalize_text(salary_text)
                    break
        except Exception as e:
            logger.debug(f"Salary selector '{selector}' failed: {e}")
            continue
    
    # No warning if salary not found - it's optional
    
    # ========================================================================
    # Extract Posted Date (Optional Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['posted']:
        try:
            posted_element = job_element.query_selector(selector)
            if posted_element:
                posted_text = posted_element.inner_text()
                if posted_text and posted_text.strip():
                    job_record['posted_date'] = normalize_text(posted_text)
                    break
        except Exception as e:
            logger.debug(f"Posted date selector '{selector}' failed: {e}")
            continue
    
    # No warning if posted date not found - it's optional
    
    # ========================================================================
    # Extract Description Snippet (Optional Field)
    # Verified March 2026
    # ========================================================================
    for selector in SELECTORS['snippet']:
        try:
            snippet_element = job_element.query_selector(selector)
            if snippet_element:
                snippet_text = snippet_element.inner_text()
                if snippet_text and snippet_text.strip():
                    job_record['description'] = normalize_text(snippet_text)
                    break
        except Exception as e:
            logger.debug(f"Snippet selector '{selector}' failed: {e}")
            continue
    
    # No warning if description not found - it's optional
    
    # All required fields validated - return the job record
    return job_record


def normalize_text(text: str) -> str:
    """
    Normalizes text by trimming whitespace and collapsing multiple spaces.
    
    This function cleans extracted text fields by removing leading/trailing
    whitespace and replacing multiple consecutive spaces with single spaces.
    This ensures consistent formatting across all extracted data.
    
    Args:
        text: Raw text string to normalize
        
    Returns:
        Normalized text string with trimmed whitespace and collapsed spaces
        
    Normalization Steps:
        1. Strip leading and trailing whitespace
        2. Replace multiple consecutive spaces with single space
        3. Replace tabs and newlines with single space
        4. Collapse any remaining multiple spaces
        
    Example:
        >>> normalize_text("  Software Engineer  ")
        'Software Engineer'
        
        >>> normalize_text("Senior   Software    Engineer")
        'Senior Software Engineer'
        
        >>> normalize_text("Software\\nEngineer\\t-\\tRemote")
        'Software Engineer - Remote'
        
    Note:
        - Uses regex to replace multiple whitespace characters
        - Handles tabs, newlines, and multiple spaces
        - Preserves single spaces between words
        - Returns empty string if input is None or empty
        
    Requirements:
        - 18.6: Scraper shall trim whitespace from all extracted text fields
        - 18.7: Scraper shall normalize whitespace by replacing multiple spaces with single spaces
        
    Validates:
        - Property 34: Text Normalization
    """
    if not text:
        return ""
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    # Replace multiple whitespace characters (spaces, tabs, newlines) with single space
    # Pattern: \s+ matches one or more whitespace characters
    text = re.sub(r'\s+', ' ', text)
    
    return text


def is_valid_url(url: str) -> bool:
    """
    Validates that a URL has proper format with protocol, domain, and path.
    
    This function checks if a URL string is properly formatted and contains
    the required components (protocol and domain). It ensures that extracted
    job links are valid before adding them to job records.
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL is valid, False otherwise
        
    Validation Criteria:
        - Must start with http:// or https://
        - Must contain a domain name
        - Must not be empty or None
        
    Example:
        >>> is_valid_url("https://in.indeed.com/viewjob?jk=abc123")
        True
        
        >>> is_valid_url("/viewjob?jk=abc123")
        False
        
        >>> is_valid_url("")
        False
        
    Note:
        - Simple validation focused on protocol and basic structure
        - Does not validate domain existence or reachability
        - Does not validate query parameters or fragments
        - Sufficient for ensuring URLs are absolute and well-formed
        
    Requirements:
        - 18.3: Scraper shall verify URL format is valid before adding to Job_Record
        
    Validates:
        - Property 33: URL Validation
    """
    if not url:
        return False
    
    # Check if URL starts with http:// or https://
    if not (url.startswith('http://') or url.startswith('https://')):
        return False
    
    # Check if URL has a domain (at least one dot after protocol)
    # Simple check: must have at least "http://x.x" format
    if len(url) < 12:  # Minimum: "http://a.b/"
        return False
    
    # URL passes basic validation
    return True



# ============================================================================
# Page Extraction Function
# ============================================================================


def extract_jobs_from_page(page: Page) -> list:
    """
    Extracts all job listings from the current page.
    
    This function finds all job card elements on an Indeed search results page
    and extracts structured data from each one. It uses the container selector
    to locate job cards, then calls extract_single_job() for each element.
    Invalid records (where extraction fails) are filtered out automatically.
    
    Args:
        page: Playwright Page object with loaded search results
        
    Returns:
        List of job record dictionaries with validated fields
        Empty list if no valid jobs found or page has no job cards
        
    Extraction Process:
        1. Find all job card elements using container selector from config
        2. Iterate through each job card element
        3. Call extract_single_job() to extract data from each card
        4. Filter out None results (invalid/incomplete records)
        5. Return list of valid job records
        
    Example:
        >>> page.goto("https://in.indeed.com/jobs?q=software+engineer&sort=date")
        >>> jobs = extract_jobs_from_page(page)
        >>> print(f"Found {len(jobs)} valid jobs")
        Found 47 valid jobs
        >>> for job in jobs:
        ...     print(f"{job['title']} at {job['company']}")
        
    Note:
        - Uses fallback selectors from config.SELECTORS['job_card']
        - Tries each selector until one finds elements
        - Logs warning if no job cards found on page
        - Returns empty list if extraction fails completely
        - Invalid records are automatically filtered out
        - Each job record is validated by extract_single_job()
        
    Requirements:
        - 4.1: Scraper shall extract job title for all job listings on a page
        - 4.2: Scraper shall extract company name for all job listings on a page
        - 4.3: Scraper shall extract location for all job listings on a page
        - 4.4: Scraper shall extract full job link URL for all job listings on a page
        - 4.5: Scraper shall extract short description or snippet for all job listings on a page
        
    Validates:
        - Property 7: Required Field Extraction (via extract_single_job)
        - Property 8: Conditional Field Extraction (via extract_single_job)
        - Property 9: Absolute URL Conversion (via extract_single_job)
        - Property 10: Consistent Field Names (via extract_single_job)
    """
    from config import SELECTORS
    
    job_records = []
    job_elements = []
    
    # ========================================================================
    # Find all job card elements using fallback selectors
    # Try each selector until one succeeds
    # ========================================================================
    for selector in SELECTORS['job_card']:
        try:
            elements = page.query_selector_all(selector)
            if elements and len(elements) > 0:
                job_elements = elements
                logger.info(f"Found {len(job_elements)} job cards using selector: {selector}")
                break
        except Exception as e:
            logger.debug(f"Job card selector '{selector}' failed: {e}")
            continue
    
    # Check if we found any job cards
    if not job_elements:
        logger.warning(f"No job cards found on page: {page.url}")
        return []
    
    # ========================================================================
    # Extract data from each job card element
    # Filter out None results (invalid records)
    # ========================================================================
    for index, job_element in enumerate(job_elements):
        try:
            job_record = extract_single_job(job_element)
            
            # Only add valid records (extract_single_job returns None for invalid)
            if job_record:
                job_records.append(job_record)
            else:
                logger.debug(f"Skipped invalid job record at index {index}")
                
        except Exception as e:
            logger.warning(f"Error extracting job at index {index}: {e}")
            continue
    
    # Log extraction summary
    logger.info(f"Successfully extracted {len(job_records)} valid jobs from {len(job_elements)} job cards")
    
    return job_records


# ============================================================================
# Deduplicator Component
# ============================================================================


def normalize_url(url: str) -> str:
    """
    Normalizes a job URL for comparison to enable effective deduplication.
    
    This function standardizes job URLs by removing variations that don't affect
    the actual job posting (query parameters, fragments, trailing slashes) and
    extracting the core job identifier. This ensures that different URL formats
    pointing to the same job are recognized as duplicates.
    
    Args:
        url: Raw job URL (e.g., "https://in.indeed.com/viewjob?jk=abc123&from=serp")
        
    Returns:
        Normalized URL string containing only the essential job identifier
        
    Normalization Steps:
        1. Parse URL into components (scheme, netloc, path, query, fragment)
        2. Lowercase the domain (netloc) for case-insensitive comparison
        3. Extract job ID from query parameters (jk parameter) or path
        4. Remove all other query parameters
        5. Remove URL fragments (#section)
        6. Remove trailing slashes from path
        7. Reconstruct URL with normalized components
        
    URL Patterns Handled:
        - Query-based: https://in.indeed.com/viewjob?jk=abc123&from=serp
          → https://in.indeed.com/viewjob?jk=abc123
        
        - Path-based: https://in.indeed.com/jobs/software-engineer-abc123
          → https://in.indeed.com/jobs/software-engineer-abc123
        
        - With fragment: https://in.indeed.com/viewjob?jk=abc123#section
          → https://in.indeed.com/viewjob?jk=abc123
        
        - Trailing slash: https://in.indeed.com/viewjob?jk=abc123/
          → https://in.indeed.com/viewjob?jk=abc123
        
        - Mixed case domain: https://IN.Indeed.COM/viewjob?jk=abc123
          → https://in.indeed.com/viewjob?jk=abc123
        
    Example:
        >>> normalize_url("https://in.indeed.com/viewjob?jk=abc123&from=serp&tk=xyz")
        'https://in.indeed.com/viewjob?jk=abc123'
        
        >>> normalize_url("https://IN.Indeed.COM/viewjob?jk=abc123#apply")
        'https://in.indeed.com/viewjob?jk=abc123'
        
        >>> normalize_url("https://in.indeed.com/jobs/software-engineer-abc123/")
        'https://in.indeed.com/jobs/software-engineer-abc123'
        
    Note:
        - Job ID (jk parameter) is preserved as it uniquely identifies the job
        - All other query parameters are removed (from, tk, etc.)
        - Domain is lowercased for case-insensitive comparison
        - Path is preserved as-is (except trailing slash removal)
        - Fragments are always removed
        - Invalid URLs return the original URL unchanged
        
    Requirements:
        - 5.4: Deduplicator shall normalize job link URLs before comparison
        
    Validates:
        - Property 13: URL Normalization for Deduplication
          For any two job URLs that differ only in query parameters, fragments,
          or trailing slashes, they should be considered duplicates after normalization.
    """
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
    try:
        # Parse URL into components
        parsed = urlparse(url)
        
        # Lowercase the domain (netloc) for case-insensitive comparison
        normalized_netloc = parsed.netloc.lower()
        
        # Remove trailing slashes from path
        normalized_path = parsed.path.rstrip('/')
        
        # Parse query parameters
        query_params = parse_qs(parsed.query)
        
        # Extract and preserve only the job ID parameter (jk)
        # Indeed uses 'jk' parameter to uniquely identify jobs
        normalized_query = ''
        if 'jk' in query_params:
            # Keep only the jk parameter (job key)
            # parse_qs returns lists, so we take the first value
            job_id = query_params['jk'][0]
            normalized_query = urlencode({'jk': job_id})
        
        # Remove fragment (everything after #)
        # Fragments are client-side navigation and don't affect the job posting
        normalized_fragment = ''
        
        # Reconstruct the normalized URL
        normalized_url = urlunparse((
            parsed.scheme,      # Keep original scheme (http/https)
            normalized_netloc,  # Lowercased domain
            normalized_path,    # Path without trailing slash
            '',                 # params (not used by Indeed)
            normalized_query,   # Only jk parameter if present
            normalized_fragment # No fragment
        ))
        
        return normalized_url
        
    except Exception as e:
        # If URL parsing fails, return original URL
        # This ensures the function doesn't crash on malformed URLs
        logger.warning(f"Failed to normalize URL '{url}': {e}")
        return url



def deduplicate_jobs(job_records: list) -> list:
    """
    Removes duplicate job records based on normalized URLs.
    
    This function processes a list of job records and removes duplicates by comparing
    normalized job URLs. When duplicates are found, only the first occurrence is
    retained, preserving the original order of unique records in the output.
    
    Args:
        job_records: List of job record dictionaries, each containing a 'link' field
        
    Returns:
        List of unique job records, preserving original order
        
    Deduplication Strategy:
        1. Create a set to track seen job URLs (normalized)
        2. Iterate through records in original order
        3. For each record, normalize the job URL
        4. If normalized URL not seen before:
           - Add to results list
           - Mark normalized URL as seen
        5. If normalized URL already seen:
           - Skip the record (duplicate)
        6. Return deduplicated list maintaining original order
        
    Example:
        >>> jobs = [
        ...     {'title': 'Engineer', 'link': 'https://in.indeed.com/viewjob?jk=123&from=serp'},
        ...     {'title': 'Developer', 'link': 'https://in.indeed.com/viewjob?jk=456'},
        ...     {'title': 'Engineer', 'link': 'https://in.indeed.com/viewjob?jk=123#apply'}
        ... ]
        >>> unique_jobs = deduplicate_jobs(jobs)
        >>> len(unique_jobs)
        2
        >>> unique_jobs[0]['title']
        'Engineer'
        >>> unique_jobs[1]['title']
        'Developer'
        
    Duplicate Detection:
        - URLs are normalized before comparison using normalize_url()
        - Different URL formats pointing to same job are detected:
          * Query parameter variations (jk=123&from=serp vs jk=123)
          * Fragment differences (jk=123#apply vs jk=123)
          * Case differences in domain (IN.Indeed.COM vs in.indeed.com)
          * Trailing slash differences (/viewjob/ vs /viewjob)
        
    Order Preservation:
        - First occurrence of each unique job is retained
        - Relative order of unique jobs matches original list
        - Later duplicates are silently skipped
        
    Note:
        - Requires 'link' field in each job record
        - Uses normalize_url() for URL standardization
        - Empty or missing 'link' fields are treated as unique (not deduplicated)
        - Invalid URLs that fail normalization are compared as-is
        - Function is idempotent: deduplicate(deduplicate(jobs)) == deduplicate(jobs)
        
    Requirements:
        - 5.1: Deduplicator shall identify duplicates by comparing job link URLs
        - 5.2: Deduplicator shall retain only the first occurrence when duplicates identified
        - 5.3: Deduplicator shall preserve original order of Job_Records during deduplication
        - 5.4: Deduplicator shall normalize job link URLs before comparison
        
    Validates:
        - Property 11: Deduplication by URL
          For any list of job records containing duplicate job links, the deduplicator
          should retain only the first occurrence of each unique job link.
        
        - Property 12: Order Preservation During Deduplication
          For any list of job records, deduplication should preserve the relative
          order of the unique records.
        
        - Property 13: URL Normalization for Deduplication
          For any two job URLs that differ only in query parameters, fragments,
          or trailing slashes, they should be considered duplicates after normalization.
    """
    # Set to track seen normalized URLs
    seen_urls = set()
    
    # List to store unique job records
    unique_jobs = []
    
    # Iterate through job records in original order
    for job_record in job_records:
        # Extract job link from record
        job_link = job_record.get('link')
        
        # Skip records without a link (shouldn't happen with valid extraction)
        if not job_link:
            logger.warning(f"Job record missing 'link' field: {job_record.get('title', 'Unknown')}")
            continue
        
        # Normalize the URL for comparison
        normalized_link = normalize_url(job_link)
        
        # Check if we've seen this normalized URL before
        if normalized_link not in seen_urls:
            # First occurrence - add to results and mark as seen
            unique_jobs.append(job_record)
            seen_urls.add(normalized_link)
        # else: duplicate - skip silently
    
    return unique_jobs



def generate_output_filename(base_name: str, extension: str) -> str:
    """
    Generates a unique filename with timestamp.
    
    This function creates a filename by combining a base name with a timestamp
    to ensure uniqueness across multiple scraping sessions. The timestamp format
    (YYYYMMDD_HHMMSS) provides both human readability and chronological sorting.
    
    Args:
        base_name: Base name for file (e.g., "indeed_jobs")
        extension: File extension without dot (e.g., "json", "csv")
        
    Returns:
        Filename with timestamp (e.g., "indeed_jobs_20241215_143022.json")
        
    Filename Format:
        {base_name}_{YYYYMMDD}_{HHMMSS}.{extension}
        
        Components:
        - base_name: User-provided base name for the file
        - YYYYMMDD: Date in year-month-day format (e.g., 20241215 for Dec 15, 2024)
        - HHMMSS: Time in hour-minute-second format (e.g., 143022 for 2:30:22 PM)
        - extension: File extension (e.g., json, csv)
        
    Example:
        >>> filename = generate_output_filename("indeed_jobs", "json")
        >>> filename
        'indeed_jobs_20241215_143022.json'
        
        >>> filename = generate_output_filename("results", "csv")
        >>> filename
        'results_20241215_143022.csv'
        
    Timestamp Behavior:
        - Uses current local time from datetime.now()
        - Timestamp has 1-second resolution
        - Files generated within the same second will have identical timestamps
        - For guaranteed uniqueness, ensure at least 1 second between calls
        
    Use Cases:
        - Generating unique output filenames for JSON exports
        - Generating unique output filenames for CSV exports
        - Preventing overwriting of previous scraping results
        - Creating chronologically sortable output files
        
    Note:
        - Extension should not include the leading dot
        - Base name can contain underscores or hyphens
        - Timestamp uses 24-hour format (00-23 for hours)
        - No validation is performed on base_name or extension
        - Function does not check if file already exists
        - Function does not create the file, only generates the name
        
    Requirements:
        - 6.7: Data_Exporter shall generate unique filenames using timestamps
          to prevent overwriting previous results
        
    Validates:
        - Property 16: Unique Filename Generation
          For any two export operations performed at different times (at least
          1 second apart), the generated filenames should be different.
    """
    from datetime import datetime
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Construct filename: base_name_YYYYMMDD_HHMMSS.extension
    filename = f"{base_name}_{timestamp}.{extension}"
    
    return filename


def export_to_json(job_records: list, output_path: str) -> None:
    """
    Exports job records to a JSON file.
    
    This function writes a list of job records to a JSON file with proper UTF-8
    encoding and indentation for readability. The output is formatted as a valid
    JSON array that can be easily parsed by other tools and applications.
    
    Args:
        job_records: List of job record dictionaries to export
        output_path: Path for output file (e.g., "output/indeed_jobs_20241215_143022.json")
        
    Returns:
        None
        
    JSON Format:
        The output is a JSON array containing job record objects:
        [
          {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Bangalore, Karnataka",
            "salary": "₹8,00,000 - ₹12,00,000 a year",
            "posted_date": "2 days ago",
            "link": "https://in.indeed.com/viewjob?jk=abc123",
            "description": "We are looking for a skilled software engineer..."
          },
          ...
        ]
        
    File Encoding:
        - UTF-8 encoding to support international characters (₹, special chars)
        - Indentation: 2 spaces for readability
        - Ensure ASCII: False (preserve Unicode characters)
        - Sort keys: False (preserve insertion order)
        
    Example:
        >>> jobs = [
        ...     {
        ...         'title': 'Software Engineer',
        ...         'company': 'Tech Corp',
        ...         'location': 'Bangalore',
        ...         'link': 'https://in.indeed.com/viewjob?jk=123',
        ...         'salary': '₹10,00,000 a year',
        ...         'posted_date': '2 days ago',
        ...         'description': 'Great opportunity...'
        ...     }
        ... ]
        >>> export_to_json(jobs, 'output/jobs.json')
        >>> # File created with proper JSON formatting
        
    Error Handling:
        - Creates output directory if it doesn't exist
        - Raises IOError if file cannot be written
        - Raises TypeError if job_records is not JSON-serializable
        
    Use Cases:
        - Exporting final deduplicated job records after scraping session
        - Saving intermediate results for session resumption
        - Creating checkpoint files with session state
        
    Note:
        - Function does not validate job record structure
        - Empty list will create valid JSON array: []
        - Existing file at output_path will be overwritten
        - Parent directory must exist or be created
        - Uses json.dump() for efficient writing
        
    Requirements:
        - 6.1: Data_Exporter shall write all unique Job_Records to a JSON file
          when a Session completes
        - 6.3: Data_Exporter shall format the JSON output as a valid JSON array
        - 6.5: Data_Exporter shall use UTF-8 encoding for both JSON and CSV files
        
    Validates:
        - Property 14: JSON Export Round-Trip
          For any list of job records, exporting to JSON and then parsing the
          JSON file should produce an equivalent list of records.
    """
    import json
    import os
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write job records to JSON file with UTF-8 encoding
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(
            job_records,
            f,
            indent=2,           # 2 spaces for readability
            ensure_ascii=False  # Preserve Unicode characters (₹, etc.)
        )
    
    logger.info(f"Exported {len(job_records)} job records to {output_path}")


def export_to_csv(job_records: list, output_path: str) -> None:
    """
    Exports job records to a CSV file with headers.
    
    This function writes a list of job records to a CSV file with proper UTF-8
    encoding (with BOM for Excel compatibility), headers, and appropriate quoting
    to handle special characters and commas in field values.
    
    Args:
        job_records: List of job record dictionaries to export
        output_path: Path for output file (e.g., "output/indeed_jobs_20241215_143022.csv")
        
    Returns:
        None
        
    CSV Format:
        The output CSV has the following structure:
        - Headers: title, company, location, salary, posted_date, link, description
        - Encoding: UTF-8 with BOM (Byte Order Mark) for Excel compatibility
        - Quoting: QUOTE_MINIMAL (only fields with special characters)
        - Escaping: Double quotes escaped as ""
        
        Example:
        title,company,location,salary,posted_date,link,description
        "Software Engineer","Tech Corp","Bangalore, Karnataka","₹8,00,000 - ₹12,00,000 a year","2 days ago","https://in.indeed.com/viewjob?jk=abc123","We are looking for a skilled software engineer..."
        
    Field Order:
        1. title - Job title
        2. company - Company name
        3. location - Job location
        4. salary - Salary information (may be empty)
        5. posted_date - When job was posted (may be empty)
        6. link - Absolute URL to job posting
        7. description - Job description snippet (may be empty)
        
    File Encoding:
        - UTF-8 with BOM (\ufeff) for Excel compatibility
        - BOM ensures Excel correctly interprets UTF-8 encoding
        - Supports international characters (₹, special chars)
        
    Quoting Strategy:
        - QUOTE_MINIMAL: Only quote fields containing special characters
        - Special characters: comma, quote, newline, carriage return
        - Double quotes in fields are escaped as ""
        - Example: Field with "quote" becomes ""quote"" (with doubled quotes)
        
    Example:
        >>> jobs = [
        ...     {
        ...         'title': 'Software Engineer',
        ...         'company': 'Tech Corp',
        ...         'location': 'Bangalore, Karnataka',
        ...         'link': 'https://in.indeed.com/viewjob?jk=123',
        ...         'salary': '₹10,00,000 a year',
        ...         'posted_date': '2 days ago',
        ...         'description': 'Great opportunity with "excellent" benefits'
        ...     }
        ... ]
        >>> export_to_csv(jobs, 'output/jobs.csv')
        >>> # File created with proper CSV formatting and Excel compatibility
        
    Error Handling:
        - Creates output directory if it doesn't exist
        - Raises IOError if file cannot be written
        - Handles missing optional fields (salary, posted_date, description) as empty strings
        
    Use Cases:
        - Exporting final deduplicated job records for Excel analysis
        - Creating CSV files for data import into databases
        - Generating reports for stakeholders who prefer spreadsheet format
        
    Note:
        - Function does not validate job record structure
        - Empty list will create CSV with headers only
        - Existing file at output_path will be overwritten
        - Parent directory must exist or be created
        - Uses csv.DictWriter for efficient writing
        - Optional fields default to empty string if missing
        
    Requirements:
        - 6.2: Data_Exporter shall write all unique Job_Records to a CSV file
          when a Session completes
        - 6.4: Data_Exporter shall include column headers in the CSV output
        - 6.5: Data_Exporter shall use UTF-8 encoding for both JSON and CSV files
        - 6.6: Data_Exporter shall handle special characters and commas in CSV
          fields using proper escaping
        
    Validates:
        - Property 15: CSV Export Round-Trip
          For any list of job records (including those with special characters
          and commas), exporting to CSV and then parsing the CSV file should
          produce an equivalent list of records.
    """
    import csv
    import os
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define CSV headers in the specified order
    fieldnames = ['title', 'company', 'location', 'salary', 'posted_date', 'link', 'description']
    
    # Write job records to CSV file with UTF-8 encoding and BOM
    with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            quoting=csv.QUOTE_MINIMAL,  # Only quote fields with special characters
            extrasaction='ignore'        # Ignore extra fields not in fieldnames
        )
        
        # Write header row
        writer.writeheader()
        
        # Write job records
        # Handle missing optional fields by providing empty string defaults
        for job in job_records:
            row = {
                'title': job.get('title', ''),
                'company': job.get('company', ''),
                'location': job.get('location', ''),
                'salary': job.get('salary', ''),
                'posted_date': job.get('posted_date', ''),
                'link': job.get('link', ''),
                'description': job.get('description', '')
            }
            writer.writerow(row)
    
    logger.info(f"Exported {len(job_records)} job records to {output_path}")


# ============================================================================
# Session Manager Component
# ============================================================================
# This section implements checkpoint and session resumption functionality
# to allow recovery from interrupted scraping sessions.
# ============================================================================

def save_checkpoint(completed_queries: list, checkpoint_path: str, total_jobs: int = 0) -> None:
    """
    Saves completed search queries to checkpoint file for session resumption.
    
    This function creates a checkpoint file containing the list of completed
    search queries, a timestamp, and the total number of jobs collected so far.
    This enables session resumption after interruptions by tracking which
    queries have already been processed.
    
    Args:
        completed_queries: List of search query strings that have been completed
        checkpoint_path: Path to the checkpoint file (typically in checkpoints/ directory)
        total_jobs: Total number of jobs collected so far (default: 0)
        
    Returns:
        None
        
    Side Effects:
        - Creates checkpoint directory if it doesn't exist
        - Writes checkpoint data to JSON file
        - Overwrites existing checkpoint file if present
        
    Checkpoint File Format:
        {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": [
                "software engineer Bangalore",
                "python developer Bangalore"
            ],
            "total_jobs_collected": 287
        }
    
    Example:
        >>> completed = ["software engineer Bangalore", "python developer Bangalore"]
        >>> save_checkpoint(completed, "checkpoints/session_checkpoint.json", 287)
        # Creates checkpoint file with timestamp and completed queries
        
    Use Cases:
        - Save progress after completing each search query
        - Enable session resumption after interruption
        - Track scraping progress across multiple runs
        
    Note:
        - Timestamp is in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
        - Checkpoint file is overwritten on each save (not appended)
        - Directory creation is handled automatically
        - Uses UTF-8 encoding for international characters in queries
        
    Requirements:
        - 14.1: Scraper shall save intermediate results after completing each
          Search_Query
        - 14.2: Scraper shall use a checkpoint file to track completed
          Search_Queries
          
    Validates:
        - Property 25: Checkpoint After Query Completion
          For any completed search query, the scraper should save intermediate
          results and update the checkpoint file.
    """
    import json
    import os
    from datetime import datetime
    
    # Ensure checkpoint directory exists
    checkpoint_dir = os.path.dirname(checkpoint_path)
    if checkpoint_dir and not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    
    # Create checkpoint data structure
    checkpoint_data = {
        'timestamp': datetime.now().isoformat(),
        'completed_queries': completed_queries,
        'total_jobs_collected': total_jobs
    }
    
    # Write checkpoint to JSON file
    with open(checkpoint_path, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Checkpoint saved: {len(completed_queries)} queries completed, {total_jobs} jobs collected")


def load_checkpoint(checkpoint_path: str) -> list:
    """
    Loads completed search queries from checkpoint file for session resumption.

    This function reads a checkpoint file to retrieve the list of search queries
    that have already been completed in a previous session. This enables the
    scraper to resume from where it left off after an interruption, avoiding
    redundant work.

    Args:
        checkpoint_path: Path to the checkpoint file (typically in checkpoints/ directory)

    Returns:
        List of completed search query strings. Returns empty list if:
        - Checkpoint file doesn't exist
        - Checkpoint file is invalid/corrupted
        - Checkpoint file doesn't contain 'completed_queries' field

    Side Effects:
        - Reads checkpoint file from disk
        - Logs info message about loaded checkpoint
        - Logs warning if checkpoint file doesn't exist or is invalid

    Checkpoint File Format (Expected):
        {
            "timestamp": "2024-12-15T14:30:22",
            "completed_queries": [
                "software engineer Bangalore",
                "python developer Bangalore"
            ],
            "total_jobs_collected": 287
        }

    Example:
        >>> completed = load_checkpoint("checkpoints/session_checkpoint.json")
        >>> print(completed)
        ['software engineer Bangalore', 'python developer Bangalore']

        >>> # If file doesn't exist
        >>> completed = load_checkpoint("checkpoints/nonexistent.json")
        >>> print(completed)
        []

    Use Cases:
        - Resume scraping session after interruption
        - Skip already-completed queries to avoid duplicate work
        - Determine which queries still need to be processed

    Note:
        - Returns empty list (not None) when file doesn't exist for easier handling
        - Gracefully handles missing or corrupted checkpoint files
        - Uses UTF-8 encoding to support international characters in queries
        - Logs appropriate messages for debugging and monitoring

    Requirements:
        - 14.4: When restarting after interruption, the Scraper shall read the
          checkpoint file to identify completed Search_Queries

    Validates:
        - Property 27: Session Resumption from Checkpoint
          For any session restart after interruption, the scraper should read
          the checkpoint file and skip completed queries.
    """
    import json
    import os

    # Check if checkpoint file exists
    if not os.path.exists(checkpoint_path):
        logger.info(f"No checkpoint file found at {checkpoint_path}, starting fresh session")
        return []

    try:
        # Read checkpoint file
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)

        # Extract completed queries list
        completed_queries = checkpoint_data.get('completed_queries', [])
        total_jobs = checkpoint_data.get('total_jobs_collected', 0)
        timestamp = checkpoint_data.get('timestamp', 'unknown')

        logger.info(f"Checkpoint loaded: {len(completed_queries)} queries completed, "
                   f"{total_jobs} jobs collected (saved at {timestamp})")

        return completed_queries

    except json.JSONDecodeError as e:
        logger.warning(f"Checkpoint file at {checkpoint_path} is corrupted: {e}. Starting fresh session.")
        return []
    except Exception as e:
        logger.warning(f"Error loading checkpoint from {checkpoint_path}: {e}. Starting fresh session.")
        return []


def save_intermediate_results(job_records: list, output_path: str) -> None:
    """
    Saves intermediate results after each query completion for session resumption.
    
    This function saves the current accumulated job records to a JSON file,
    enabling recovery of partial results if the scraping session is interrupted.
    The intermediate results file is updated after each search query completes,
    ensuring that progress is preserved even if the scraper crashes or is stopped.
    
    Args:
        job_records: Current accumulated list of job record dictionaries
        output_path: Path for intermediate results file (e.g., "output/intermediate_results.json")
        
    Returns:
        None
        
    Side Effects:
        - Creates output directory if it doesn't exist
        - Writes job records to JSON file
        - Overwrites existing intermediate results file if present
        
    JSON Format:
        The output is a JSON array containing job record objects:
        [
          {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Bangalore, Karnataka",
            "salary": "₹8,00,000 - ₹12,00,000 a year",
            "posted_date": "2 days ago",
            "link": "https://in.indeed.com/viewjob?jk=abc123",
            "description": "We are looking for a skilled software engineer..."
          },
          ...
        ]
        
    File Encoding:
        - UTF-8 encoding to support international characters (₹, special chars)
        - Indentation: 2 spaces for readability
        - Ensure ASCII: False (preserve Unicode characters)
        
    Example:
        >>> jobs = [
        ...     {
        ...         'title': 'Software Engineer',
        ...         'company': 'Tech Corp',
        ...         'location': 'Bangalore',
        ...         'link': 'https://in.indeed.com/viewjob?jk=123',
        ...         'salary': '₹10,00,000 a year',
        ...         'posted_date': '2 days ago',
        ...         'description': 'Great opportunity...'
        ...     }
        ... ]
        >>> save_intermediate_results(jobs, 'output/intermediate_results.json')
        # File created with current job records
        
    Error Handling:
        - Creates output directory if it doesn't exist
        - Raises IOError if file cannot be written
        - Raises TypeError if job_records is not JSON-serializable
        
    Use Cases:
        - Save progress after completing each search query
        - Enable recovery of partial results after interruption
        - Preserve accumulated job records across session restarts
        
    Note:
        - Function does not validate job record structure
        - Empty list will create valid JSON array: []
        - Existing file at output_path will be overwritten
        - Should be called after each search query completes
        - Works in conjunction with save_checkpoint() for full session resumption
        
    Requirements:
        - 14.1: Scraper shall save intermediate results after completing each
          Search_Query
        - 14.3: When a Session is interrupted, the Scraper shall preserve all
          Job_Records collected up to the interruption point
          
    Validates:
        - Property 25: Checkpoint After Query Completion
          For any completed search query, the scraper should save intermediate
          results and update the checkpoint file.
        - Property 26: Data Preservation on Interruption
          For any session interruption, all job records collected up to the
          interruption point should be preserved in the intermediate results file.
    """
    import json
    import os
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write job records to JSON file with UTF-8 encoding
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(
            job_records,
            f,
            indent=2,           # 2 spaces for readability
            ensure_ascii=False  # Preserve Unicode characters (₹, etc.)
        )
    
    logger.info(f"Saved intermediate results: {len(job_records)} job records to {output_path}")


def detect_captcha(page: Page) -> bool:
    """
    Detects CAPTCHA challenges on the current page.
    
    This function checks for CAPTCHA presence using two detection methods:
    1. Text content search: Searches page content for CAPTCHA-related keywords
    2. Element presence: Checks for common CAPTCHA element selectors
    
    The function uses CAPTCHA_SELECTORS and CAPTCHA_KEYWORDS from config.py
    to identify CAPTCHA challenges. If any keyword is found in the page content
    or any CAPTCHA element selector is present, the function returns True.
    
    Args:
        page: Playwright Page object with loaded content
        
    Returns:
        True if CAPTCHA detected, False otherwise
        
    Detection Methods:
        1. Keyword Search:
           - Searches page text content (case-insensitive)
           - Keywords from config.CAPTCHA_KEYWORDS: ["captcha", "robot", "verify"]
           - Matches partial words (e.g., "verify" matches "verify you're human")
           
        2. Element Selector Check:
           - Checks for presence of CAPTCHA elements using CSS selectors
           - Selectors from config.CAPTCHA_SELECTORS: ['#recaptcha', '.g-recaptcha', '#captcha']
           - Returns True if any selector matches an element on the page
           
    Example:
        >>> from playwright.sync_api import sync_playwright
        >>> with sync_playwright() as p:
        ...     browser = p.chromium.launch()
        ...     page = browser.new_page()
        ...     page.goto('https://example.com/captcha-page')
        ...     is_captcha = detect_captcha(page)
        ...     print(f"CAPTCHA detected: {is_captcha}")
        ...     browser.close()
        
    Use Cases:
        - Detect CAPTCHA challenges after page navigation
        - Skip pages with CAPTCHA to avoid blocking
        - Track consecutive CAPTCHA occurrences
        - Log warnings when CAPTCHA is encountered
        
    Error Handling:
        - Returns False if page content cannot be accessed
        - Returns False if selector queries fail
        - Does not raise exceptions
        
    Performance:
        - Text content search is case-insensitive (uses .lower())
        - Element queries use query_selector (stops at first match)
        - Short-circuits on first detection (returns immediately)
        
    Note:
        - Function does not attempt to solve CAPTCHAs
        - Detection is heuristic-based (may have false positives/negatives)
        - Should be called after page load completes
        - Works with both reCAPTCHA and custom CAPTCHA implementations
        
    Requirements:
        - 10.4: The Scraper shall detect CAPTCHA by searching for common
          CAPTCHA-related text patterns in page content
        - 10.5: The Scraper shall detect CAPTCHA by searching for common
          CAPTCHA-related element selectors
          
    Validates:
        - Property 22: CAPTCHA Detection by Text Patterns
          For any page containing CAPTCHA-related text patterns ("captcha",
          "robot", "verify"), the CAPTCHA detector should identify it as a
          CAPTCHA page.
        - Property 23: CAPTCHA Detection by Element Selectors
          For any page containing CAPTCHA-related element selectors (#captcha,
          .g-recaptcha, #recaptcha), the CAPTCHA detector should identify it
          as a CAPTCHA page.
    """
    try:
        # Method 1: Search page content for CAPTCHA keywords
        page_content = page.content().lower()
        
        for keyword in config.CAPTCHA_KEYWORDS:
            if keyword.lower() in page_content:
                logger.debug(f"CAPTCHA detected: keyword '{keyword}' found in page content")
                return True
        
        # Method 2: Check for CAPTCHA element selectors
        for selector in config.CAPTCHA_SELECTORS:
            element = page.query_selector(selector)
            if element:
                logger.debug(f"CAPTCHA detected: element with selector '{selector}' found on page")
                return True
        
        # No CAPTCHA indicators found
        return False
        
    except Exception as e:
        # If detection fails, assume no CAPTCHA (fail open)
        logger.warning(f"Error during CAPTCHA detection: {e}. Assuming no CAPTCHA.")
        return False
def handle_captcha_detection(query: str, page_num: int, consecutive_count: int = 0) -> int:
    """
    Handles CAPTCHA detection by logging warnings and tracking consecutive occurrences.

    This function is called when a CAPTCHA is detected on a page. It logs a warning
    message with the query and page number, tracks the number of consecutive CAPTCHA
    detections, and logs a critical warning if the threshold is exceeded.

    Args:
        query: Current search query string (e.g., "software engineer Bangalore")
        page_num: Current page number (0-indexed or 1-indexed depending on caller)
        consecutive_count: Number of consecutive CAPTCHAs detected so far (default: 0)

    Returns:
        Updated consecutive CAPTCHA count (incremented by 1)

    Behavior:
        1. Logs a warning message with query and page number
        2. Increments the consecutive CAPTCHA count
        3. If count >= CONSECUTIVE_CAPTCHA_THRESHOLD (3), logs critical warning
        4. Returns the updated count for caller to track

    Example:
        >>> consecutive = 0
        >>> consecutive = handle_captcha_detection("python developer", 2, consecutive)
        >>> print(consecutive)
        1
        >>> consecutive = handle_captcha_detection("python developer", 3, consecutive)
        >>> consecutive = handle_captcha_detection("python developer", 4, consecutive)
        # Critical warning logged after 3rd consecutive CAPTCHA

    Use Cases:
        - Log CAPTCHA encounters during scraping
        - Track consecutive CAPTCHA patterns
        - Alert operator when blocking is likely
        - Provide context for debugging rate limiting issues

    Logging Levels:
        - WARNING: Single CAPTCHA detection (includes query and page number)
        - CRITICAL: Multiple consecutive CAPTCHAs (>= threshold)

    Critical Warning Conditions:
        - Triggered when consecutive_count >= config.CONSECUTIVE_CAPTCHA_THRESHOLD (3)
        - Suggests potential blocking or rate limiting
        - Recommends increasing delays or stopping session

    Caller Responsibilities:
        - Pass the returned count to subsequent calls
        - Reset count to 0 when a page loads successfully without CAPTCHA
        - Skip the current page after CAPTCHA detection
        - Consider stopping session after critical warning

    Note:
        - Function does not skip pages or stop execution
        - Caller must handle page skipping and session termination
        - Count should be reset to 0 on successful page load
        - Function is stateless (relies on caller to maintain count)

    Requirements:
        - 10.1: When a CAPTCHA challenge is detected on a page, the Scraper
          shall log a warning message indicating CAPTCHA presence
        - 10.6: When multiple consecutive CAPTCHA challenges are detected,
          the Scraper shall log a critical warning about potential blocking

    Validates:
        - Property 24: Consecutive CAPTCHA Warning
          For any sequence of 3 or more consecutive CAPTCHA detections, the
          scraper should log a critical warning about potential blocking.
    """
    # Increment consecutive CAPTCHA count
    consecutive_count += 1

    # Log warning with query and page number
    logger.warning(
        f"CAPTCHA detected on page {page_num} of query '{query}' "
        f"(consecutive: {consecutive_count})"
    )

    # Check if threshold exceeded and log critical warning
    if consecutive_count >= config.CONSECUTIVE_CAPTCHA_THRESHOLD:
        logger.critical(
            f"CRITICAL: {consecutive_count} consecutive CAPTCHAs detected! "
            f"Potential blocking detected. Consider increasing delays or stopping session."
        )

    return consecutive_count





def handle_network_error(error: Exception, url: str, error_tracker: dict = None) -> dict:
    """
    Handles network errors by logging with context and tracking error rates.
    
    This function is called when a network error occurs during page navigation
    (e.g., timeout, connection refused, DNS failure). It logs the error with
    the URL and timestamp, tracks error counts per query, and logs a warning
    if the error rate exceeds the configured threshold (50%).
    
    Args:
        error: Exception object representing the network error
        url: URL that failed to load
        error_tracker: Dictionary tracking errors per query (optional)
                      Format: {'total_attempts': int, 'error_count': int, 'query': str}
                      If None, creates a new tracker
        
    Returns:
        Updated error_tracker dictionary with incremented counts
        
    Error Tracker Structure:
        {
            'query': str,           # Current search query
            'total_attempts': int,  # Total page navigation attempts
            'error_count': int,     # Number of failed attempts
            'error_rate': float     # Calculated error rate (0.0 to 1.0)
        }
        
    Behavior:
        1. Logs error with URL, error type, and timestamp
        2. Increments error count in tracker
        3. Calculates error rate (error_count / total_attempts)
        4. If error rate > ERROR_RATE_THRESHOLD (50%), logs warning
        5. Returns updated tracker for caller to maintain state
        
    Example:
        >>> from playwright.errors import TimeoutError
        >>> tracker = {'query': 'python developer', 'total_attempts': 4, 'error_count': 0}
        >>> try:
        ...     page.goto(url, timeout=60000)
        ... except TimeoutError as e:
        ...     tracker = handle_network_error(e, url, tracker)
        >>> print(tracker['error_count'])
        1
        >>> print(tracker['error_rate'])
        0.25
        
    Use Cases:
        - Handle page navigation timeouts
        - Handle connection failures
        - Handle DNS resolution errors
        - Track error patterns per query
        - Alert operator when error rate is high
        
    Logging:
        - ERROR level: Individual network error with URL and timestamp
        - WARNING level: High error rate (>50%) with query context
        
    Error Rate Calculation:
        - error_rate = error_count / total_attempts
        - Threshold from config.ERROR_RATE_THRESHOLD (default: 0.5 = 50%)
        - Warning logged when rate exceeds threshold
        
    Caller Responsibilities:
        - Initialize tracker before first call (or pass None)
        - Pass tracker to subsequent calls to maintain state
        - Increment total_attempts before each navigation attempt
        - Continue to next page/query after error (don't terminate session)
        
    Note:
        - Function does not terminate execution
        - Caller must handle page skipping and continuation
        - Tracker is query-specific (reset for each new query)
        - Timestamp is automatically generated using datetime.now()
        - Error rate warning helps identify potential blocking or network issues
        
    Requirements:
        - 9.1: When a network timeout occurs during page navigation, the Scraper
          shall log the error with the URL
        - 9.3: When a page fails to load after navigation, the Scraper shall
          log the error with the URL
          
    Validates:
        - Property 21: Error Logging with Context
          For any error (network timeout, page load failure), the scraper should
          log an error or warning message that includes contextual information (URL).
    """
    from datetime import datetime
    
    # Initialize tracker if not provided
    if error_tracker is None:
        error_tracker = {
            'query': 'unknown',
            'total_attempts': 1,
            'error_count': 0
        }
    
    # Increment error count
    error_tracker['error_count'] += 1
    
    # Calculate error rate
    error_rate = error_tracker['error_count'] / error_tracker['total_attempts']
    error_tracker['error_rate'] = error_rate
    
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Log error with URL and timestamp
    logger.error(
        f"[{timestamp}] Network error loading {url}: {type(error).__name__}: {str(error)}"
    )
    
    # Check if error rate exceeds threshold and log warning
    if error_rate > config.ERROR_RATE_THRESHOLD:
        logger.warning(
            f"High error rate detected for query '{error_tracker['query']}': "
            f"{error_tracker['error_count']}/{error_tracker['total_attempts']} "
            f"({error_rate:.1%}) - Potential network issues or blocking"
        )
    
    return error_tracker



def validate_selectors(page: Page) -> dict:
    """
    Validates that expected selectors are present on the current page.
    
    This function checks for the presence of key CSS selectors defined in config.py
    to detect when Indeed changes their page structure. It returns a dictionary
    mapping selector names to their presence status (True if found, False if not).
    Warnings are logged for any missing selectors along with the page URL to aid
    in debugging selector changes.
    
    Args:
        page: Playwright Page object with loaded search results
        
    Returns:
        Dictionary mapping selector names to presence status
        Format: {
            'job_card': bool,      # True if job card container found
            'title': bool,         # True if title selector found
            'company': bool,       # True if company selector found
            'location': bool,      # True if location selector found
            'link': bool,          # True if link selector found
            'salary': bool,        # True if salary selector found (optional)
            'posted': bool,        # True if posted date selector found (optional)
            'snippet': bool        # True if snippet selector found (optional)
        }
        
    Validation Strategy:
        1. For each selector type in config.SELECTORS, try all fallback selectors
        2. Mark as present (True) if ANY fallback selector matches an element
        3. Mark as absent (False) if ALL fallback selectors fail
        4. Log warning for missing selectors with page URL
        5. Return complete status dictionary
        
    Example:
        >>> page.goto("https://in.indeed.com/jobs?q=software+engineer")
        >>> status = validate_selectors(page)
        >>> print(status)
        {
            'job_card': True,
            'title': True,
            'company': True,
            'location': True,
            'link': True,
            'salary': False,  # Optional field, may not be present
            'posted': True,
            'snippet': True
        }
        >>> if not status['title']:
        ...     print("WARNING: Title selector failed - Indeed may have changed page structure")
        
    Use Cases:
        - Detect when Indeed changes their page structure
        - Validate selectors after page load
        - Track selector failure rates across pages
        - Alert operator when selectors need updating
        - Debug extraction issues
        
    Logging:
        - WARNING level: Missing selector with selector name and page URL
        - Includes all attempted selectors for debugging
        - Helps identify which selectors need updating
        
    Selector Categories:
        Required Selectors (should always be present):
        - job_card: Container for job listings
        - title: Job title
        - company: Company name
        - location: Job location
        - link: Job posting URL
        
        Optional Selectors (may not be present on all jobs):
        - salary: Salary information (not all jobs display salary)
        - posted: Posted date (may not always be visible)
        - snippet: Job description snippet
        
    Error Handling:
        - Returns False for selector if query_selector raises exception
        - Does not raise exceptions (fail gracefully)
        - Logs exceptions at debug level
        - Continues checking remaining selectors after errors
        
    Performance:
        - Uses query_selector (stops at first match per selector)
        - Short-circuits on first successful fallback
        - Minimal page interaction (read-only queries)
        
    Caller Responsibilities:
        - Call after page load completes
        - Check return value for missing required selectors
        - Track failure rates across multiple pages
        - Update selectors in config.py when failures occur
        - Consider stopping extraction if critical selectors missing
        
    Note:
        - Function does not modify page state
        - Function does not extract data (only validates presence)
        - Optional selectors may legitimately be absent
        - Required selector failures indicate page structure changes
        - Should be called before extract_jobs_from_page()
        
    Requirements:
        - 11.1: When a required selector fails to match any elements, the Scraper
          shall log a warning with the selector name
        - 11.2: When a required selector fails to match any elements, the Scraper
          shall log the current page URL for debugging
          
    Related Functions:
        - extract_single_job(): Uses these selectors for data extraction
        - extract_jobs_from_page(): Calls this for validation before extraction
    """
    # Get current page URL for logging
    current_url = page.url
    
    # Initialize status dictionary - all selectors start as False
    selector_status = {
        'job_card': False,
        'title': False,
        'company': False,
        'location': False,
        'link': False,
        'salary': False,
        'posted': False,
        'snippet': False
    }
    
    # Validate each selector type
    for selector_name, selector_list in config.SELECTORS.items():
        # Try each fallback selector until one succeeds
        found = False
        
        for selector in selector_list:
            try:
                # Check if selector matches any element on page
                element = page.query_selector(selector)
                if element:
                    # Selector found - mark as present and stop trying fallbacks
                    selector_status[selector_name] = True
                    found = True
                    logger.debug(f"Selector '{selector_name}' found using: {selector}")
                    break
            except Exception as e:
                # Log exception but continue trying other fallbacks
                logger.debug(f"Error checking selector '{selector}': {e}")
                continue
        
        # If no fallback selector worked, log warning
        if not found:
            logger.warning(
                f"Selector validation failed for '{selector_name}' on page: {current_url}\n"
                f"  Attempted selectors: {selector_list}\n"
                f"  This may indicate Indeed has changed their page structure."
            )
    
    # Log summary of validation results
    missing_selectors = [name for name, present in selector_status.items() if not present]
    if missing_selectors:
        logger.warning(
            f"Selector validation summary for {current_url}:\n"
            f"  Missing selectors: {', '.join(missing_selectors)}\n"
            f"  Present selectors: {', '.join([name for name, present in selector_status.items() if present])}"
        )
    else:
        logger.info(f"All selectors validated successfully on {current_url}")
    
    return selector_status



# ============================================================================
# Task 12: Search Query Executor
# ============================================================================

def execute_search_query(
    page: Page,
    query: str,
    max_pages: int = 4
) -> list:
    """
    Executes a single search query with pagination and anti-detection behavior.
    
    This function orchestrates the complete search query execution workflow:
    1. Constructs the search URL for the query
    2. Generates pagination URLs for max_pages
    3. For each page:
       - Navigates to the page with timeout
       - Applies anti-detection behavior (scrolling, mouse movement)
       - Detects and handles CAPTCHA challenges
       - Validates selectors (optional but recommended)
       - Extracts job records from the page
       - Handles network errors gracefully
       - Applies random delay before next page
    4. Returns all collected job records from all pages
    
    This function is the core orchestrator that integrates all prerequisite
    components: URL construction, pagination, anti-detection, extraction,
    and error handling.
    
    Args:
        page: Playwright Page object (should be from configured browser)
        query: Search query string (e.g., "software engineer Bangalore")
        max_pages: Maximum number of pages to scrape (default 4)
        
    Returns:
        List of job record dictionaries extracted from all pages
        Format: [
            {
                'title': str,
                'company': str,
                'location': str,
                'link': str,
                'salary': str | None,
                'posted_date': str | None,
                'description': str | None
            },
            ...
        ]
        
    Workflow:
        1. Build search URL using construct_search_url()
        2. Generate pagination URLs using get_pagination_urls()
        3. Initialize tracking variables:
           - all_jobs: List to accumulate job records
           - consecutive_captchas: Counter for CAPTCHA tracking
           - error_tracker: Dictionary for error rate tracking
        4. For each pagination URL:
           a. Increment total_attempts for error tracking
           b. Try to navigate to URL with PAGE_LOAD_TIMEOUT
           c. If navigation fails:
              - Call handle_network_error() to log and track
              - Continue to next page
           d. If navigation succeeds:
              - Check for CAPTCHA using detect_captcha()
              - If CAPTCHA detected:
                * Call handle_captcha_detection() to log and track
                * Skip page and continue to next
              - If no CAPTCHA:
                * Reset consecutive_captchas to 0
                * Apply anti-detection behavior (scroll, mouse movement)
                * Optionally validate selectors
                * Extract jobs using extract_jobs_from_page()
                * Add extracted jobs to all_jobs list
                * Log progress (page number, jobs extracted)
           e. Apply random delay before next page (except last page)
        5. Return all_jobs list
        
    Example:
        >>> from playwright.sync_api import sync_playwright
        >>> with sync_playwright() as p:
        ...     browser = create_browser_profile(p)
        ...     page = browser.new_page()
        ...     jobs = execute_search_query(page, "python developer Bangalore", max_pages=4)
        ...     print(f"Extracted {len(jobs)} jobs")
        ...     browser.close()
        
    Error Handling:
        - Network timeouts: Logged and tracked, page skipped, execution continues
        - CAPTCHA challenges: Logged and tracked, page skipped, execution continues
        - Selector failures: Logged but extraction attempted, execution continues
        - Extraction errors: Logged, page skipped, execution continues
        - All errors are non-fatal - function completes and returns partial results
        
    Progress Logging:
        - INFO: Query started with query string
        - INFO: Page navigation (page number, URL)
        - INFO: Jobs extracted (page number, count)
        - WARNING: CAPTCHA detected (page number, consecutive count)
        - WARNING: High error rate (error count, total attempts, percentage)
        - ERROR: Network failures (URL, error type)
        - INFO: Query completed (total jobs extracted)
        
    Anti-Detection Features:
        - Random delays between pages (8-18 seconds)
        - Human-like scrolling with variable speed
        - Random mouse movements
        - Resource blocking (images, fonts, trackers)
        - Timeout handling to avoid hanging
        
    Performance:
        - Typical execution time: 2-4 minutes per query (4 pages)
        - Expected jobs per query: 125-250 (after deduplication)
        - Memory usage: Minimal (streaming extraction, no page caching)
        
    Requirements:
        - 2.1: Execute searches for predefined search queries in sequence
        - 2.2: Append "&sort=date" parameter to search URL
        - 2.3: Navigate through pages using start parameters 0, 50, 100, 150
        - 2.4: Construct search URLs targeting in.indeed.com domain
        - 2.5: Extract job records from minimum 3 and maximum 4 pages
        - 3.1: Wait random duration between 8-18 seconds between page navigations
        - 3.2: Wait random duration between 8-18 seconds between actions
        - 9.2: When network timeout occurs, continue to next page or search
        - 9.4: When page fails to load, continue to next page or search
        - 9.5: Set page load timeout of 60 seconds for navigation operations
        - 9.6: When network errors occur, do not terminate entire session
        - 10.2: When CAPTCHA detected, skip current page
        - 10.3: When CAPTCHA detected, continue to next page or search
        
    Validates:
        - Property 20: Error Resilience
          For any network error, page load failure, or CAPTCHA detection, the
          scraper should log the error and continue to the next page or query
          without terminating the session.
        - Property 21: Error Logging with Context
          For any error, the scraper should log an error or warning message
          that includes contextual information (URL, query, page number).
          
    Related Functions:
        - construct_search_url(): Builds search URL from query
        - get_pagination_urls(): Generates pagination URLs
        - apply_anti_detection_behavior(): Applies scrolling and mouse movements
        - detect_captcha(): Checks for CAPTCHA challenges
        - handle_captcha_detection(): Logs CAPTCHA and tracks consecutive count
        - handle_network_error(): Logs network errors and tracks error rate
        - validate_selectors(): Validates selector presence (optional)
        - extract_jobs_from_page(): Extracts job records from page
        - random_delay(): Applies random delay between pages
        
    Note:
        - Function is designed to be called by main orchestrator (Task 13.1)
        - Function does not perform deduplication (handled by orchestrator)
        - Function does not save results (handled by orchestrator)
        - Function maintains state only within single query execution
        - Caller should handle browser lifecycle and session management
    """
    from playwright.sync_api import TimeoutError, Error as PlaywrightError
    
    # Log query start
    logger.info(f"Starting search query: '{query}'")
    
    # Step 1: Construct search URL
    base_url = construct_search_url(query)
    logger.debug(f"Base search URL: {base_url}")
    
    # Step 2: Generate pagination URLs
    pagination_urls = get_pagination_urls(base_url, max_pages)
    logger.info(f"Generated {len(pagination_urls)} pagination URLs for query '{query}'")
    
    # Step 3: Initialize tracking variables
    all_jobs = []  # Accumulate all job records
    consecutive_captchas = 0  # Track consecutive CAPTCHA detections
    error_tracker = {
        'query': query,
        'total_attempts': 0,
        'error_count': 0
    }
    
    # Step 4: Iterate through pagination URLs
    for page_num, url in enumerate(pagination_urls, start=1):
        logger.info(f"Processing page {page_num}/{len(pagination_urls)} for query '{query}'")
        logger.info(f"Navigating to: {url}")
        
        # Increment total attempts for error tracking
        error_tracker['total_attempts'] += 1
        
        # Step 4a: Try to navigate to page
        try:
            page.goto(url, timeout=config.PAGE_LOAD_TIMEOUT)
            logger.debug(f"Successfully loaded page {page_num}")
            
        except (TimeoutError, PlaywrightError) as e:
            # Step 4c: Handle network error
            logger.error(f"Failed to load page {page_num} for query '{query}'")
            error_tracker = handle_network_error(e, url, error_tracker)
            # Continue to next page
            continue
        
        # Step 4d: Check for CAPTCHA
        if detect_captcha(page):
            # CAPTCHA detected - log, track, and skip page
            consecutive_captchas = handle_captcha_detection(query, page_num, consecutive_captchas)
            logger.info(f"Skipping page {page_num} due to CAPTCHA")
            # Continue to next page
            continue
        else:
            # No CAPTCHA - reset consecutive counter
            consecutive_captchas = 0
            logger.debug(f"No CAPTCHA detected on page {page_num}")
        
        # Step 4d: Apply anti-detection behavior
        try:
            logger.debug(f"Applying anti-detection behavior on page {page_num}")
            apply_anti_detection_behavior(page)
            logger.debug(f"Anti-detection behavior completed on page {page_num}")
            
        except Exception as e:
            logger.warning(f"Error during anti-detection behavior on page {page_num}: {e}")
            # Continue with extraction even if anti-detection fails
        
        # Step 4d: Optionally validate selectors
        try:
            selector_status = validate_selectors(page)
            # Check if critical selectors are missing
            critical_selectors = ['job_card', 'title', 'company', 'location', 'link']
            missing_critical = [s for s in critical_selectors if not selector_status.get(s, False)]
            
            if missing_critical:
                logger.warning(
                    f"Critical selectors missing on page {page_num}: {', '.join(missing_critical)}"
                )
                # Continue with extraction anyway - extract_jobs_from_page will handle missing selectors
                
        except Exception as e:
            logger.warning(f"Error during selector validation on page {page_num}: {e}")
            # Continue with extraction even if validation fails
        
        # Step 4d: Extract jobs from page
        try:
            logger.debug(f"Extracting jobs from page {page_num}")
            jobs = extract_jobs_from_page(page)
            
            # Add extracted jobs to accumulator
            all_jobs.extend(jobs)
            
            # Log progress
            logger.info(f"Extracted {len(jobs)} jobs from page {page_num} (total so far: {len(all_jobs)})")
            
        except Exception as e:
            logger.error(f"Error extracting jobs from page {page_num}: {e}")
            # Continue to next page even if extraction fails
        
        # Step 4e: Apply random delay before next page (except last page)
        if page_num < len(pagination_urls):
            logger.debug(f"Applying random delay before next page")
            random_delay(config.MIN_DELAY, config.MAX_DELAY)
    
    # Step 5: Log completion and return results
    logger.info(f"Completed search query '{query}': extracted {len(all_jobs)} total jobs")
    
    # Log error summary if there were errors
    if error_tracker['error_count'] > 0:
        error_rate = error_tracker['error_count'] / error_tracker['total_attempts']
        logger.info(
            f"Error summary for query '{query}': "
            f"{error_tracker['error_count']}/{error_tracker['total_attempts']} pages failed "
            f"({error_rate:.1%} error rate)"
        )
    
    return all_jobs


# ============================================================================
# Task 13.1: Main Orchestrator
# ============================================================================

def main():
    """
    Main orchestrator function that coordinates the entire scraping workflow.
    
    This function serves as the entry point for the Indeed Job Scraper and
    orchestrates all components to execute the complete scraping workflow:
    
    Workflow:
        1. Initialize Playwright and create browser profile
        2. Load checkpoint to identify completed queries (for resumption)
        3. Load intermediate results if resuming from interruption
        4. Iterate through search queries (skip completed ones)
        5. For each query:
           - Execute search using execute_search_query()
           - Save intermediate results after completion
           - Update checkpoint after completion
        6. Deduplicate all collected job records
        7. Export to JSON and CSV with unique filenames
        8. Print progress messages and statistics
        9. Ensure browser and Playwright cleanup in finally block
    
    Progress Messages:
        - Current query being processed
        - Page number and URL during pagination
        - Jobs extracted per page
        - Total jobs collected so far
        - Unique count after deduplication
        - Final statistics (total collected, unique count, output files)
    
    Error Handling:
        - Uses try-finally block to ensure resource cleanup
        - All errors during scraping are handled by component functions
        - Critical errors are logged but don't prevent cleanup
        - Browser and Playwright are always closed, even on error
    
    Session Resumability:
        - Checks for existing checkpoint file on startup
        - Loads completed queries from checkpoint
        - Loads intermediate results from previous run
        - Skips completed queries and continues from interruption point
        - Merges new results with previous partial results
        - Updates checkpoint after each query completion
    
    Output:
        - JSON file: output/indeed_jobs_YYYYMMDD_HHMMSS.json
        - CSV file: output/indeed_jobs_YYYYMMDD_HHMMSS.csv
        - Checkpoint file: checkpoints/session_checkpoint.json
        - Intermediate results: output/intermediate_results.json
    
    Requirements Validated:
        - 7.1: Print current search term to console
        - 7.2: Print current page number and URL to console
        - 7.3: Print count of jobs extracted to console
        - 7.4: Print total count of job records collected to console
        - 7.5: Print count of unique job records after deduplication
        - 8.3: Complete session and report actual volume collected
        - 8.4: Distribute extraction across all eight search queries
        - 12.1: Separate browser configuration logic into dedicated function
        - 12.2: Separate anti-detection behavior into dedicated functions
        - 12.3: Separate data extraction logic into dedicated function
        - 12.4: Separate deduplication logic into dedicated function
        - 12.5: Separate data export logic into dedicated functions
        - 14.4: Read checkpoint file to identify completed queries
        - 14.5: Skip search queries that were already completed
        - 14.6: Merge results from resumed sessions with previous partial results
        - 15.1: Close browser context when session completes normally
        - 15.2: Close Playwright instance when session completes normally
        - 15.3: Close browser context before exiting on error
        - 15.4: Close Playwright instance before exiting on error
        - 15.5: Use try-finally blocks to ensure cleanup code executes
        - 16.4: Reuse single browser context across all search queries
        - 16.5: Limit concurrent page operations to one at a time
    
    Example:
        >>> python scraper.py
        [INFO] Starting Indeed Job Scraper
        [INFO] Initializing Playwright and browser profile
        [INFO] Loading checkpoint from checkpoints/session_checkpoint.json
        [INFO] Found 2 completed queries, resuming from interruption
        [INFO] Loading intermediate results from output/intermediate_results.json
        [INFO] Loaded 287 jobs from previous run
        [INFO] Processing query 3/8: data analyst Bangalore
        [INFO] Starting search query: 'data analyst Bangalore'
        [INFO] Processing page 1/4 for query 'data analyst Bangalore'
        [INFO] Extracted 45 jobs from page 1 (total so far: 332)
        ...
        [INFO] Completed all 8 search queries
        [INFO] Total jobs collected: 1847
        [INFO] Deduplicating job records...
        [INFO] Unique jobs after deduplication: 1523
        [INFO] Exporting to JSON: output/indeed_jobs_20241215_143022.json
        [INFO] Exporting to CSV: output/indeed_jobs_20241215_143022.csv
        [INFO] Scraping completed successfully!
        [INFO] Final Statistics:
        [INFO]   - Total jobs collected: 1847
        [INFO]   - Unique jobs: 1523
        [INFO]   - Deduplication rate: 17.5%
        [INFO]   - JSON output: output/indeed_jobs_20241215_143022.json
        [INFO]   - CSV output: output/indeed_jobs_20241215_143022.csv
    
    Note:
        - This function is designed to be called when script is run directly
        - All component functions are implemented in previous tasks
        - Function ensures proper resource cleanup even on errors
        - Progress messages are printed to console for monitoring
        - Checkpoint and intermediate results enable session resumption
    """
    import os
    from pathlib import Path
    
    # Initialize variables for cleanup
    playwright = None
    browser = None
    page = None
    
    try:
        # ====================================================================
        # Step 1: Initialize Playwright and Browser Profile
        # ====================================================================
        logger.info("=" * 70)
        logger.info("Starting Indeed Job Scraper")
        logger.info("=" * 70)
        logger.info("Initializing Playwright and browser profile...")
        
        playwright = sync_playwright().start()
        browser = create_browser_profile(playwright)
        page = browser.new_page()
        
        logger.info("Browser profile created successfully")
        
        # ====================================================================
        # Step 2: Load Checkpoint (for session resumption)
        # ====================================================================
        checkpoint_path = os.path.join(config.CHECKPOINT_DIR, config.CHECKPOINT_FILENAME)
        logger.info(f"Loading checkpoint from {checkpoint_path}")
        
        # Create checkpoint directory if it doesn't exist
        Path(config.CHECKPOINT_DIR).mkdir(parents=True, exist_ok=True)
        
        completed_queries = load_checkpoint(checkpoint_path)
        
        if completed_queries:
            logger.info(f"Found {len(completed_queries)} completed queries, resuming from interruption")
            logger.info(f"Completed queries: {completed_queries}")
        else:
            logger.info("No checkpoint found, starting fresh session")
        
        # ====================================================================
        # Step 3: Load Intermediate Results (if resuming)
        # ====================================================================
        intermediate_path = os.path.join(config.OUTPUT_DIR, config.INTERMEDIATE_RESULTS_FILENAME)
        all_jobs = []
        
        if completed_queries and os.path.exists(intermediate_path):
            logger.info(f"Loading intermediate results from {intermediate_path}")
            try:
                import json
                with open(intermediate_path, 'r', encoding='utf-8') as f:
                    all_jobs = json.load(f)
                logger.info(f"Loaded {len(all_jobs)} jobs from previous run")
            except Exception as e:
                logger.warning(f"Failed to load intermediate results: {e}")
                logger.info("Starting with empty job list")
                all_jobs = []
        else:
            logger.info("No intermediate results found, starting with empty job list")
        
        # Create output directory if it doesn't exist
        Path(config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        
        # ====================================================================
        # Step 4: Iterate Through Search Queries
        # ====================================================================
        logger.info("")
        logger.info("=" * 70)
        logger.info(f"Processing {len(config.SEARCH_QUERIES)} search queries")
        logger.info("=" * 70)
        
        # Filter out completed queries
        remaining_queries = [q for q in config.SEARCH_QUERIES if q not in completed_queries]
        
        if not remaining_queries:
            logger.info("All queries already completed!")
        else:
            logger.info(f"Remaining queries to process: {len(remaining_queries)}")
        
        for idx, query in enumerate(remaining_queries, start=1):
            total_idx = config.SEARCH_QUERIES.index(query) + 1
            logger.info("")
            logger.info("-" * 70)
            logger.info(f"Processing query {total_idx}/{len(config.SEARCH_QUERIES)}: {query}")
            logger.info("-" * 70)
            
            # ================================================================
            # Step 5a: Execute Search Query
            # ================================================================
            try:
                jobs = execute_search_query(page, query, max_pages=config.MAX_PAGES)
                
                # Add jobs to accumulator
                all_jobs.extend(jobs)
                
                logger.info(f"Query '{query}' completed: extracted {len(jobs)} jobs")
                logger.info(f"Total jobs collected so far: {len(all_jobs)}")
                
            except Exception as e:
                logger.error(f"Error executing query '{query}': {e}")
                logger.info("Continuing to next query...")
                # Continue to next query even if this one fails
            
            # ================================================================
            # Step 5b: Save Intermediate Results
            # ================================================================
            try:
                logger.info(f"Saving intermediate results to {intermediate_path}")
                save_intermediate_results(all_jobs, intermediate_path)
                logger.info("Intermediate results saved successfully")
            except Exception as e:
                logger.warning(f"Failed to save intermediate results: {e}")
            
            # ================================================================
            # Step 5c: Update Checkpoint
            # ================================================================
            try:
                completed_queries.append(query)
                logger.info(f"Updating checkpoint: {len(completed_queries)}/{len(config.SEARCH_QUERIES)} queries completed")
                save_checkpoint(completed_queries, checkpoint_path, total_jobs=len(all_jobs))
                logger.info("Checkpoint updated successfully")
            except Exception as e:
                logger.warning(f"Failed to update checkpoint: {e}")
        
        # ====================================================================
        # Step 6: Deduplicate Job Records
        # ====================================================================
        logger.info("")
        logger.info("=" * 70)
        logger.info("Deduplication Phase")
        logger.info("=" * 70)
        logger.info(f"Total jobs collected: {len(all_jobs)}")
        logger.info("Deduplicating job records...")
        
        unique_jobs = deduplicate_jobs(all_jobs)
        
        duplicates_removed = len(all_jobs) - len(unique_jobs)
        dedup_rate = (duplicates_removed / len(all_jobs) * 100) if all_jobs else 0
        
        logger.info(f"Unique jobs after deduplication: {len(unique_jobs)}")
        logger.info(f"Duplicates removed: {duplicates_removed} ({dedup_rate:.1f}%)")
        
        # ====================================================================
        # Step 7: Export to JSON and CSV
        # ====================================================================
        logger.info("")
        logger.info("=" * 70)
        logger.info("Export Phase")
        logger.info("=" * 70)
        
        # Generate unique filenames with timestamps
        json_filename = generate_output_filename("indeed_jobs", "json")
        csv_filename = generate_output_filename("indeed_jobs", "csv")
        
        json_path = os.path.join(config.OUTPUT_DIR, json_filename)
        csv_path = os.path.join(config.OUTPUT_DIR, csv_filename)
        
        # Export to JSON
        logger.info(f"Exporting to JSON: {json_path}")
        try:
            export_to_json(unique_jobs, json_path)
            logger.info("JSON export completed successfully")
        except Exception as e:
            logger.error(f"Failed to export JSON: {e}")
        
        # Export to CSV
        logger.info(f"Exporting to CSV: {csv_path}")
        try:
            export_to_csv(unique_jobs, csv_path)
            logger.info("CSV export completed successfully")
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
        
        # ====================================================================
        # Step 8: Print Final Statistics
        # ====================================================================
        logger.info("")
        logger.info("=" * 70)
        logger.info("Scraping Completed Successfully!")
        logger.info("=" * 70)
        logger.info("")
        logger.info("Final Statistics:")
        logger.info(f"  - Total jobs collected: {len(all_jobs)}")
        logger.info(f"  - Unique jobs: {len(unique_jobs)}")
        logger.info(f"  - Duplicates removed: {duplicates_removed} ({dedup_rate:.1f}%)")
        logger.info(f"  - Queries processed: {len(config.SEARCH_QUERIES)}")
        logger.info(f"  - JSON output: {json_path}")
        logger.info(f"  - CSV output: {csv_path}")
        logger.info("")
        logger.info("=" * 70)
        
        # Clean up checkpoint and intermediate results after successful completion
        try:
            if os.path.exists(checkpoint_path):
                os.remove(checkpoint_path)
                logger.info("Checkpoint file removed (session completed)")
            if os.path.exists(intermediate_path):
                os.remove(intermediate_path)
                logger.info("Intermediate results file removed (session completed)")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary files: {e}")
        
    except Exception as e:
        # Log critical error but ensure cleanup happens
        logger.error("=" * 70)
        logger.error("CRITICAL ERROR")
        logger.error("=" * 70)
        logger.error(f"An unexpected error occurred: {e}")
        logger.error("The scraper will now shut down and clean up resources")
        logger.error("=" * 70)
        
        # Re-raise to ensure proper error handling
        raise
        
    finally:
        # ====================================================================
        # Step 9: Resource Cleanup (ALWAYS EXECUTES)
        # ====================================================================
        logger.info("")
        logger.info("Cleaning up resources...")
        
        # Close page
        if page:
            try:
                page.close()
                logger.info("Page closed successfully")
            except Exception as e:
                logger.warning(f"Error closing page: {e}")
        
        # Close browser context
        if browser:
            try:
                browser.close()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
        
        # Stop Playwright
        if playwright:
            try:
                playwright.stop()
                logger.info("Playwright stopped successfully")
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
        
        logger.info("Resource cleanup completed")
        logger.info("=" * 70)


# ============================================================================
# Script Entry Point
# ============================================================================

if __name__ == '__main__':
    """
    Entry point when script is run directly.
    
    Usage:
        python scraper.py
    
    This will execute the main() function which orchestrates the entire
    scraping workflow from initialization to cleanup.
    """
    main()
