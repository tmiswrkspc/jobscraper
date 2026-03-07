"""
Validation tests for Task 6.1: Create single job extraction function

This test file validates the extract_single_job() function implementation
to ensure it correctly extracts job data using fallback selectors, validates
required fields, normalizes text, and converts relative URLs to absolute URLs.
"""

import pytest
from playwright.sync_api import sync_playwright
from scraper import extract_single_job, normalize_text, is_valid_url


def test_normalize_text():
    """Test text normalization function."""
    # Test trimming whitespace
    assert normalize_text("  Software Engineer  ") == "Software Engineer"
    
    # Test collapsing multiple spaces
    assert normalize_text("Senior   Software    Engineer") == "Senior Software Engineer"
    
    # Test handling tabs and newlines
    assert normalize_text("Software\nEngineer\t-\tRemote") == "Software Engineer - Remote"
    
    # Test empty string
    assert normalize_text("") == ""
    assert normalize_text("   ") == ""
    
    # Test None
    assert normalize_text(None) == ""
    
    print("✓ Text normalization tests passed")


def test_is_valid_url():
    """Test URL validation function."""
    # Valid URLs
    assert is_valid_url("https://in.indeed.com/viewjob?jk=abc123") == True
    assert is_valid_url("http://in.indeed.com/viewjob?jk=abc123") == True
    assert is_valid_url("https://example.com/path") == True
    
    # Invalid URLs
    assert is_valid_url("/viewjob?jk=abc123") == False  # Relative URL
    assert is_valid_url("") == False  # Empty string
    assert is_valid_url(None) == False  # None
    assert is_valid_url("not-a-url") == False  # No protocol
    assert is_valid_url("http://") == False  # Too short
    
    print("✓ URL validation tests passed")


def test_extract_single_job_with_mock_html():
    """Test extract_single_job with mock HTML structure."""
    
    # Create a mock HTML page with a job card
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Indeed Jobs</title></head>
    <body>
        <div class="job_seen_beacon">
            <h2 class="jobTitle">
                <span>Senior Software Engineer</span>
            </h2>
            <span data-testid="company-name">Tech Corp India</span>
            <div data-testid="text-location">Bangalore, Karnataka</div>
            <div data-testid="salaryOnly">₹15,00,000 - ₹25,00,000 a year</div>
            <span data-testid="myJobsStateDate">Posted 2 days ago</span>
            <a class="jcs-JobTitle" href="/viewjob?jk=test123">View Job</a>
            <div class="job-snippet">
                We are looking for an experienced software engineer with 5+ years of experience.
            </div>
        </div>
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        # Find the job card element
        job_card = page.query_selector('div.job_seen_beacon')
        
        # Extract job data
        job = extract_single_job(job_card)
        
        # Validate extraction
        assert job is not None, "Job extraction should not return None"
        assert job['title'] == "Senior Software Engineer"
        assert job['company'] == "Tech Corp India"
        assert job['location'] == "Bangalore, Karnataka"
        assert job['salary'] == "₹15,00,000 - ₹25,00,000 a year"
        assert job['posted_date'] == "Posted 2 days ago"
        assert job['description'] == "We are looking for an experienced software engineer with 5+ years of experience."
        
        # Validate URL conversion to absolute
        assert job['link'].startswith('https://in.indeed.com/')
        assert 'test123' in job['link']
        
        browser.close()
        
    print("✓ Extract single job with complete data passed")


def test_extract_single_job_missing_optional_fields():
    """Test extract_single_job with missing optional fields (salary, posted_date, description)."""
    
    # Create a mock HTML page with only required fields
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Indeed Jobs</title></head>
    <body>
        <div class="job_seen_beacon">
            <h2 class="jobTitle">
                <span>Python Developer</span>
            </h2>
            <span data-testid="company-name">Startup Inc</span>
            <div data-testid="text-location">Remote</div>
            <a class="jcs-JobTitle" href="/viewjob?jk=test456">View Job</a>
        </div>
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        # Find the job card element
        job_card = page.query_selector('div.job_seen_beacon')
        
        # Extract job data
        job = extract_single_job(job_card)
        
        # Validate extraction
        assert job is not None, "Job extraction should succeed with only required fields"
        assert job['title'] == "Python Developer"
        assert job['company'] == "Startup Inc"
        assert job['location'] == "Remote"
        assert job['link'].startswith('https://in.indeed.com/')
        
        # Optional fields should be None
        assert job['salary'] is None
        assert job['posted_date'] is None
        assert job['description'] is None
        
        browser.close()
        
    print("✓ Extract single job with missing optional fields passed")


def test_extract_single_job_missing_required_field():
    """Test extract_single_job returns None when required field is missing."""
    
    # Create a mock HTML page missing company name (required field)
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Indeed Jobs</title></head>
    <body>
        <div class="job_seen_beacon">
            <h2 class="jobTitle">
                <span>Data Analyst</span>
            </h2>
            <div data-testid="text-location">Mumbai, Maharashtra</div>
            <a class="jcs-JobTitle" href="/viewjob?jk=test789">View Job</a>
        </div>
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        # Find the job card element
        job_card = page.query_selector('div.job_seen_beacon')
        
        # Extract job data
        job = extract_single_job(job_card)
        
        # Should return None because company is missing
        assert job is None, "Job extraction should return None when required field is missing"
        
        browser.close()
        
    print("✓ Extract single job with missing required field returns None")


def test_extract_single_job_with_whitespace_normalization():
    """Test that extracted text is properly normalized."""
    
    # Create a mock HTML page with excessive whitespace
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Indeed Jobs</title></head>
    <body>
        <div class="job_seen_beacon">
            <h2 class="jobTitle">
                <span>  Senior    Full Stack    Developer  </span>
            </h2>
            <span data-testid="company-name">  Tech   Solutions   Ltd  </span>
            <div data-testid="text-location">  Bangalore,   Karnataka  </div>
            <a class="jcs-JobTitle" href="/viewjob?jk=test999">View Job</a>
        </div>
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        # Find the job card element
        job_card = page.query_selector('div.job_seen_beacon')
        
        # Extract job data
        job = extract_single_job(job_card)
        
        # Validate normalization
        assert job is not None
        assert job['title'] == "Senior Full Stack Developer"  # Multiple spaces collapsed
        assert job['company'] == "Tech Solutions Ltd"  # Multiple spaces collapsed
        assert job['location'] == "Bangalore, Karnataka"  # Multiple spaces collapsed
        
        browser.close()
        
    print("✓ Text normalization in extraction passed")


def test_extract_single_job_with_fallback_selectors():
    """Test that fallback selectors work when primary selectors fail."""
    
    # Create a mock HTML page using fallback selectors
    html_content = """
    <!DOCTYPE html>
    <html>
    <head><title>Indeed Jobs</title></head>
    <body>
        <div class="cardOutline">
            <h2 class="jobTitle">Frontend Developer</h2>
            <span class="companyName">Web Agency</span>
            <div class="companyLocation">Pune, Maharashtra</div>
            <div class="salary-snippet">₹6,00,000 - ₹10,00,000 a year</div>
            <span class="date">30+ days ago</span>
            <h2><a href="/rc/clk?jk=fallback123">View Job</a></h2>
            <div data-testid="job-snippet">Looking for a creative frontend developer.</div>
        </div>
    </body>
    </html>
    """
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_content)
        
        # Find the job card element using fallback container selector
        job_card = page.query_selector('div.cardOutline')
        
        # Extract job data
        job = extract_single_job(job_card)
        
        # Validate extraction using fallback selectors
        assert job is not None, "Job extraction should work with fallback selectors"
        assert job['title'] == "Frontend Developer"
        assert job['company'] == "Web Agency"
        assert job['location'] == "Pune, Maharashtra"
        assert job['salary'] == "₹6,00,000 - ₹10,00,000 a year"
        assert job['posted_date'] == "30+ days ago"
        assert job['description'] == "Looking for a creative frontend developer."
        assert job['link'].startswith('https://in.indeed.com/')
        
        browser.close()
        
    print("✓ Fallback selector extraction passed")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Task 6.1 Validation Tests: extract_single_job()")
    print("="*70 + "\n")
    
    # Run all tests
    test_normalize_text()
    test_is_valid_url()
    test_extract_single_job_with_mock_html()
    test_extract_single_job_missing_optional_fields()
    test_extract_single_job_missing_required_field()
    test_extract_single_job_with_whitespace_normalization()
    test_extract_single_job_with_fallback_selectors()
    
    print("\n" + "="*70)
    print("✓ All Task 6.1 validation tests passed!")
    print("="*70 + "\n")
