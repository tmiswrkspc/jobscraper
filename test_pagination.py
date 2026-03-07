"""
Unit tests for pagination URL generator function.

Tests Task 4.2: Create pagination URL generator function
Validates Requirements 2.3, 2.5
"""

import pytest
from scraper import construct_search_url, get_pagination_urls


def test_pagination_urls_count():
    """Test that get_pagination_urls generates exactly 4 URLs."""
    base_url = construct_search_url("software engineer Bangalore")
    urls = get_pagination_urls(base_url, max_pages=4)
    
    assert len(urls) == 4, f"Expected 4 URLs, got {len(urls)}"


def test_pagination_start_parameters():
    """Test that pagination URLs have correct start parameters [0, 50, 100, 150]."""
    base_url = construct_search_url("python developer")
    urls = get_pagination_urls(base_url, max_pages=4)
    
    # Extract start parameters from URLs
    import re
    start_params = []
    for url in urls:
        match = re.search(r'start=(\d+)', url)
        assert match, f"URL missing start parameter: {url}"
        start_params.append(int(match.group(1)))
    
    expected_starts = [0, 50, 100, 150]
    assert start_params == expected_starts, f"Expected {expected_starts}, got {start_params}"


def test_pagination_preserves_base_url():
    """Test that pagination URLs preserve the base query and sort parameters."""
    query = "data analyst Bangalore"
    base_url = construct_search_url(query)
    urls = get_pagination_urls(base_url, max_pages=4)
    
    # All URLs should contain the base URL components
    for url in urls:
        assert "in.indeed.com" in url, f"URL missing domain: {url}"
        assert "q=data+analyst+Bangalore" in url, f"URL missing query: {url}"
        assert "sort=date" in url, f"URL missing sort parameter: {url}"


def test_pagination_with_different_queries():
    """Test pagination with various search queries."""
    test_queries = [
        "software engineer Bangalore",
        "python developer",
        "remote software engineer India",
        "data scientist Bangalore"
    ]
    
    for query in test_queries:
        base_url = construct_search_url(query)
        urls = get_pagination_urls(base_url, max_pages=4)
        
        assert len(urls) == 4, f"Query '{query}' generated {len(urls)} URLs instead of 4"
        
        # Verify all URLs are unique
        assert len(set(urls)) == 4, f"Query '{query}' generated duplicate URLs"


def test_pagination_max_pages_parameter():
    """Test that max_pages parameter correctly limits the number of URLs."""
    base_url = construct_search_url("java developer")
    
    # Test with different max_pages values
    for max_pages in [1, 2, 3, 4]:
        urls = get_pagination_urls(base_url, max_pages=max_pages)
        assert len(urls) == max_pages, f"max_pages={max_pages} generated {len(urls)} URLs"


def test_pagination_url_format():
    """Test that generated URLs have correct format."""
    base_url = construct_search_url("frontend developer")
    urls = get_pagination_urls(base_url, max_pages=4)
    
    for i, url in enumerate(urls):
        # Check URL starts with https
        assert url.startswith("https://"), f"URL {i+1} doesn't start with https: {url}"
        
        # Check URL contains all required parameters
        assert "?" in url, f"URL {i+1} missing query parameters: {url}"
        assert "&" in url, f"URL {i+1} missing parameter separator: {url}"
        
        # Check URL has start parameter
        assert "start=" in url, f"URL {i+1} missing start parameter: {url}"


def test_pagination_urls_are_strings():
    """Test that all returned URLs are strings."""
    base_url = construct_search_url("full stack developer")
    urls = get_pagination_urls(base_url, max_pages=4)
    
    assert isinstance(urls, list), "get_pagination_urls should return a list"
    
    for i, url in enumerate(urls):
        assert isinstance(url, str), f"URL {i+1} is not a string: {type(url)}"


def test_pagination_with_special_characters():
    """Test pagination with queries containing special characters."""
    # Test with query that has special characters
    query = "C++ developer & Java expert"
    base_url = construct_search_url(query)
    urls = get_pagination_urls(base_url, max_pages=4)
    
    assert len(urls) == 4, "Special character query should generate 4 URLs"
    
    # All URLs should be properly formatted
    for url in urls:
        assert url.startswith("https://"), f"URL with special chars malformed: {url}"
        assert "start=" in url, f"URL with special chars missing start: {url}"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
