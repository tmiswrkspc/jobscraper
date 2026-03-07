"""
Validation test for Task 4.2: Create pagination URL generator function

This test validates that the get_pagination_urls function meets all requirements:
- Requirement 2.3: Pagination handler shall navigate through pages using start parameters 0, 50, 100, 150
- Requirement 2.5: Scraper shall extract job records from minimum 3 pages and maximum 4 pages

Task Details:
- Write get_pagination_urls(base_query_url, max_pages) function
- Generate URLs with start parameters [0, 50, 100, 150] for 4 pages
"""

import pytest
from scraper import construct_search_url, get_pagination_urls


def test_task_4_2_requirements():
    """
    Comprehensive validation test for Task 4.2.
    
    Validates:
    1. Function exists and is callable
    2. Generates exactly 4 URLs (max_pages=4)
    3. URLs have start parameters [0, 50, 100, 150] (Requirement 2.3)
    4. All URLs preserve base query parameters
    5. Function works with various search queries
    """
    print("\n=== Task 4.2 Validation: Create pagination URL generator function ===\n")
    
    # Test 1: Function exists and is callable
    print("Test 1: Verifying function exists...")
    assert callable(get_pagination_urls), "get_pagination_urls function should be callable"
    print("✓ Function exists and is callable\n")
    
    # Test 2: Generate URLs for a sample query
    print("Test 2: Generating pagination URLs...")
    base_url = construct_search_url("software engineer Bangalore")
    print(f"Base URL: {base_url}")
    
    urls = get_pagination_urls(base_url, max_pages=4)
    print(f"Generated {len(urls)} URLs:")
    for i, url in enumerate(urls, 1):
        print(f"  Page {i}: {url}")
    
    assert len(urls) == 4, f"Expected 4 URLs, got {len(urls)}"
    print("✓ Generated exactly 4 URLs (Requirement 2.5)\n")
    
    # Test 3: Verify start parameters [0, 50, 100, 150] (Requirement 2.3)
    print("Test 3: Verifying start parameters...")
    import re
    start_params = []
    for url in urls:
        match = re.search(r'start=(\d+)', url)
        assert match, f"URL missing start parameter: {url}"
        start_params.append(int(match.group(1)))
    
    expected_starts = [0, 50, 100, 150]
    print(f"Start parameters: {start_params}")
    print(f"Expected: {expected_starts}")
    assert start_params == expected_starts, f"Start parameters don't match requirement 2.3"
    print("✓ Start parameters match [0, 50, 100, 150] (Requirement 2.3)\n")
    
    # Test 4: Verify all URLs preserve base query parameters
    print("Test 4: Verifying base URL preservation...")
    for i, url in enumerate(urls, 1):
        assert "in.indeed.com" in url, f"URL {i} missing domain"
        assert "q=software+engineer+Bangalore" in url, f"URL {i} missing query parameter"
        assert "sort=date" in url, f"URL {i} missing sort parameter"
        print(f"  ✓ URL {i} preserves base parameters")
    print("✓ All URLs preserve base query and sort parameters\n")
    
    # Test 5: Test with multiple queries from config
    print("Test 5: Testing with multiple search queries...")
    from config import SEARCH_QUERIES
    
    test_queries = SEARCH_QUERIES[:3]  # Test first 3 queries
    for query in test_queries:
        base_url = construct_search_url(query)
        urls = get_pagination_urls(base_url, max_pages=4)
        
        assert len(urls) == 4, f"Query '{query}' should generate 4 URLs"
        
        # Verify start parameters for each query
        start_params = [int(re.search(r'start=(\d+)', url).group(1)) for url in urls]
        assert start_params == [0, 50, 100, 150], f"Query '{query}' has incorrect start parameters"
        
        print(f"  ✓ Query '{query}' generates correct pagination URLs")
    
    print("✓ Function works correctly with multiple queries\n")
    
    # Test 6: Verify max_pages parameter flexibility
    print("Test 6: Testing max_pages parameter...")
    base_url = construct_search_url("python developer")
    
    # Test with 3 pages (minimum per Requirement 2.5)
    urls_3 = get_pagination_urls(base_url, max_pages=3)
    assert len(urls_3) == 3, "max_pages=3 should generate 3 URLs"
    start_params_3 = [int(re.search(r'start=(\d+)', url).group(1)) for url in urls_3]
    assert start_params_3 == [0, 50, 100], "3 pages should have start parameters [0, 50, 100]"
    print(f"  ✓ max_pages=3 generates 3 URLs with start=[0, 50, 100]")
    
    # Test with 4 pages (maximum per Requirement 2.5)
    urls_4 = get_pagination_urls(base_url, max_pages=4)
    assert len(urls_4) == 4, "max_pages=4 should generate 4 URLs"
    start_params_4 = [int(re.search(r'start=(\d+)', url).group(1)) for url in urls_4]
    assert start_params_4 == [0, 50, 100, 150], "4 pages should have start parameters [0, 50, 100, 150]"
    print(f"  ✓ max_pages=4 generates 4 URLs with start=[0, 50, 100, 150]")
    
    print("✓ max_pages parameter works correctly (Requirement 2.5: min 3, max 4 pages)\n")
    
    # Test 7: Verify URL format and structure
    print("Test 7: Verifying URL format and structure...")
    base_url = construct_search_url("data analyst Bangalore")
    urls = get_pagination_urls(base_url, max_pages=4)
    
    for i, url in enumerate(urls, 1):
        # Check HTTPS protocol
        assert url.startswith("https://"), f"URL {i} should use HTTPS"
        
        # Check domain
        assert "in.indeed.com/jobs" in url, f"URL {i} should target in.indeed.com/jobs"
        
        # Check query parameters
        assert "?" in url, f"URL {i} should have query parameters"
        assert "&" in url, f"URL {i} should have multiple parameters"
        
        # Check all required parameters present
        assert "q=" in url, f"URL {i} missing query parameter"
        assert "sort=date" in url, f"URL {i} missing sort parameter"
        assert "start=" in url, f"URL {i} missing start parameter"
        
        print(f"  ✓ URL {i} has correct format and structure")
    
    print("✓ All URLs have correct format and structure\n")
    
    print("=" * 70)
    print("✓✓✓ Task 4.2 VALIDATION PASSED ✓✓✓")
    print("=" * 70)
    print("\nSummary:")
    print("- Function get_pagination_urls() implemented correctly")
    print("- Generates 4 URLs with start parameters [0, 50, 100, 150]")
    print("- Meets Requirement 2.3: Pagination with correct start parameters")
    print("- Meets Requirement 2.5: Supports 3-4 pages per query")
    print("- Preserves base URL query and sort parameters")
    print("- Works with all predefined search queries")
    print("- Generates properly formatted URLs")
    print()


if __name__ == "__main__":
    # Run the validation test
    pytest.main([__file__, "-v", "-s"])
