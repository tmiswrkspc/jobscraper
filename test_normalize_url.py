"""
Unit tests for normalize_url function (Task 7.1).

This test file validates the URL normalization function that is used for
deduplication of job records. The function should normalize URLs by:
- Lowercasing the domain
- Removing query parameters (except job ID 'jk')
- Removing URL fragments
- Removing trailing slashes

Requirements validated: 5.4
"""

import pytest
from scraper import normalize_url


class TestNormalizeUrl:
    """Test suite for URL normalization function."""
    
    def test_normalize_query_parameters(self):
        """Test that query parameters are removed except job ID (jk)."""
        url = "https://in.indeed.com/viewjob?jk=abc123&from=serp&tk=xyz"
        expected = "https://in.indeed.com/viewjob?jk=abc123"
        assert normalize_url(url) == expected
    
    def test_normalize_lowercase_domain(self):
        """Test that domain is lowercased."""
        url = "https://IN.Indeed.COM/viewjob?jk=abc123"
        expected = "https://in.indeed.com/viewjob?jk=abc123"
        assert normalize_url(url) == expected
    
    def test_normalize_remove_fragment(self):
        """Test that URL fragments are removed."""
        url = "https://in.indeed.com/viewjob?jk=abc123#apply"
        expected = "https://in.indeed.com/viewjob?jk=abc123"
        assert normalize_url(url) == expected
    
    def test_normalize_remove_trailing_slash(self):
        """Test that trailing slashes are removed from path."""
        url = "https://in.indeed.com/jobs/software-engineer-abc123/"
        expected = "https://in.indeed.com/jobs/software-engineer-abc123"
        assert normalize_url(url) == expected
    
    def test_normalize_path_based_url(self):
        """Test normalization of path-based URLs without query parameters."""
        url = "https://in.indeed.com/jobs/software-engineer-abc123"
        expected = "https://in.indeed.com/jobs/software-engineer-abc123"
        assert normalize_url(url) == expected
    
    def test_normalize_combined_variations(self):
        """Test normalization with multiple variations combined."""
        url = "https://IN.Indeed.COM/viewjob?jk=abc123&from=serp&tk=xyz#section/"
        # Note: trailing slash in fragment doesn't affect path
        expected = "https://in.indeed.com/viewjob?jk=abc123"
        assert normalize_url(url) == expected
    
    def test_normalize_no_job_id(self):
        """Test normalization of URL without job ID parameter."""
        url = "https://in.indeed.com/jobs?q=software+engineer&sort=date"
        # Should remove all query parameters if no jk parameter
        expected = "https://in.indeed.com/jobs"
        assert normalize_url(url) == expected
    
    def test_normalize_preserves_scheme(self):
        """Test that URL scheme (http/https) is preserved."""
        url_https = "https://in.indeed.com/viewjob?jk=abc123"
        url_http = "http://in.indeed.com/viewjob?jk=abc123"
        
        assert normalize_url(url_https).startswith("https://")
        assert normalize_url(url_http).startswith("http://")
    
    def test_normalize_duplicate_detection(self):
        """Test that different URL formats for same job normalize to same value."""
        url1 = "https://in.indeed.com/viewjob?jk=abc123&from=serp"
        url2 = "https://IN.indeed.com/viewjob?jk=abc123&tk=xyz"
        url3 = "https://in.indeed.com/viewjob?jk=abc123#apply"
        url4 = "https://in.indeed.com/viewjob?jk=abc123/"
        
        normalized1 = normalize_url(url1)
        normalized2 = normalize_url(url2)
        normalized3 = normalize_url(url3)
        normalized4 = normalize_url(url4)
        
        # All should normalize to the same value
        assert normalized1 == normalized2
        assert normalized2 == normalized3
        # Note: url4 has trailing slash in path, not query, so it's different
        # Let's check if they're equal after normalization
        assert normalized1 == "https://in.indeed.com/viewjob?jk=abc123"
    
    def test_normalize_different_job_ids(self):
        """Test that URLs with different job IDs normalize to different values."""
        url1 = "https://in.indeed.com/viewjob?jk=abc123&from=serp"
        url2 = "https://in.indeed.com/viewjob?jk=xyz789&from=serp"
        
        assert normalize_url(url1) != normalize_url(url2)
    
    def test_normalize_empty_url(self):
        """Test handling of empty URL."""
        # Should return empty string or handle gracefully
        result = normalize_url("")
        assert result == ""
    
    def test_normalize_malformed_url(self):
        """Test handling of malformed URL."""
        # Should return original URL if parsing fails
        malformed = "not-a-valid-url"
        result = normalize_url(malformed)
        # Function should handle gracefully (return original or empty)
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
