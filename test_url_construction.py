"""
Unit tests for URL construction function (Task 4.1).

Tests the construct_search_url() function to ensure it properly builds
Indeed India search URLs with encoded queries and sort parameters.
"""

import sys
import urllib.parse
from scraper import construct_search_url


def test_basic_query():
    """Test URL construction with a basic query."""
    url = construct_search_url("software engineer Bangalore")
    
    # Verify domain
    assert "in.indeed.com" in url, "URL should contain in.indeed.com domain"
    
    # Verify sort parameter
    assert "sort=date" in url, "URL should contain sort=date parameter"
    
    # Verify query is encoded
    assert "software" in url, "URL should contain query terms"
    assert "engineer" in url, "URL should contain query terms"
    assert "Bangalore" in url, "URL should contain query terms"
    
    # Verify proper URL structure
    assert url.startswith("https://in.indeed.com/jobs?q="), "URL should have correct structure"
    
    print("✓ Basic query test passed")


def test_query_encoding():
    """Test that special characters are properly encoded."""
    url = construct_search_url("C++ developer")
    
    # Verify the + is encoded (should be %2B)
    assert "%2B" in url or "C%2B%2B" in url, "Special characters should be encoded"
    
    # Verify domain and sort
    assert "in.indeed.com" in url
    assert "sort=date" in url
    
    print("✓ Query encoding test passed")


def test_spaces_encoded():
    """Test that spaces are properly encoded as + signs."""
    url = construct_search_url("python developer")
    
    # Spaces should be encoded as + in query string
    assert "python+developer" in url or "python%20developer" in url, "Spaces should be encoded"
    
    print("✓ Space encoding test passed")


def test_multiple_words():
    """Test URL construction with multiple word query."""
    url = construct_search_url("remote software engineer India")
    
    assert "in.indeed.com" in url
    assert "sort=date" in url
    assert "remote" in url
    assert "software" in url
    assert "engineer" in url
    assert "India" in url
    
    print("✓ Multiple words test passed")


def test_url_structure():
    """Test that URL has correct structure and components."""
    query = "data scientist Bangalore"
    url = construct_search_url(query)
    
    # Parse the URL to verify structure
    parsed = urllib.parse.urlparse(url)
    
    # Verify scheme
    assert parsed.scheme == "https", "URL should use HTTPS"
    
    # Verify domain
    assert parsed.netloc == "in.indeed.com", "URL should target in.indeed.com"
    
    # Verify path
    assert parsed.path == "/jobs", "URL should have /jobs path"
    
    # Verify query parameters
    params = urllib.parse.parse_qs(parsed.query)
    assert "q" in params, "URL should have q parameter"
    assert "sort" in params, "URL should have sort parameter"
    assert params["sort"][0] == "date", "Sort parameter should be 'date'"
    
    print("✓ URL structure test passed")


def test_all_predefined_queries():
    """Test URL construction for all predefined search queries."""
    from config import SEARCH_QUERIES
    
    for query in SEARCH_QUERIES:
        url = construct_search_url(query)
        
        # Verify all required components
        assert "in.indeed.com" in url, f"Failed for query: {query}"
        assert "sort=date" in url, f"Failed for query: {query}"
        assert url.startswith("https://"), f"Failed for query: {query}"
        
    print(f"✓ All {len(SEARCH_QUERIES)} predefined queries test passed")


if __name__ == "__main__":
    print("Running URL construction tests for Task 4.1...\n")
    
    try:
        test_basic_query()
        test_query_encoding()
        test_spaces_encoded()
        test_multiple_words()
        test_url_structure()
        test_all_predefined_queries()
        
        print("\n" + "="*60)
        print("✓ All tests passed! Task 4.1 implementation is correct.")
        print("="*60)
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
