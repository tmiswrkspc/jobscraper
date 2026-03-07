"""
Validation tests for Task 7.1: Create URL normalization function.

This test file validates that the normalize_url function correctly implements
the normalization strategy specified in the design document:
1. Parse URL into components
2. Lowercase the domain
3. Remove query parameters (except job ID if in query)
4. Remove URL fragments
5. Remove trailing slashes
6. Extract job ID from path or query for comparison

Requirements validated: 5.4
Property validated: Property 13 - URL Normalization for Deduplication
"""

import pytest
from scraper import normalize_url


class TestTask71NormalizeUrl:
    """Validation tests for Task 7.1 - URL normalization function."""
    
    def test_real_indeed_url_patterns(self):
        """Test with realistic Indeed URL patterns."""
        # Common Indeed URL format with job key
        url1 = "https://in.indeed.com/viewjob?jk=a1b2c3d4e5f6&from=serp&vjs=3"
        url2 = "https://in.indeed.com/viewjob?jk=a1b2c3d4e5f6&tk=1234567890"
        url3 = "https://in.indeed.com/viewjob?jk=a1b2c3d4e5f6"
        
        # All should normalize to the same value
        normalized1 = normalize_url(url1)
        normalized2 = normalize_url(url2)
        normalized3 = normalize_url(url3)
        
        assert normalized1 == normalized2 == normalized3
        assert normalized1 == "https://in.indeed.com/viewjob?jk=a1b2c3d4e5f6"
    
    def test_normalization_step_1_parse_url(self):
        """Validate Step 1: Parse URL into components."""
        url = "https://in.indeed.com/viewjob?jk=abc123&from=serp#apply"
        result = normalize_url(url)
        
        # Should successfully parse and return a valid URL
        assert result.startswith("https://")
        assert "in.indeed.com" in result
    
    def test_normalization_step_2_lowercase_domain(self):
        """Validate Step 2: Lowercase the domain."""
        url_mixed = "https://IN.Indeed.COM/viewjob?jk=abc123"
        url_lower = "https://in.indeed.com/viewjob?jk=abc123"
        
        # Both should normalize to the same lowercased domain
        assert normalize_url(url_mixed) == normalize_url(url_lower)
        assert "in.indeed.com" in normalize_url(url_mixed)
        assert "IN.Indeed.COM" not in normalize_url(url_mixed)
    
    def test_normalization_step_3_remove_query_params_except_jk(self):
        """Validate Step 3: Remove query parameters (except job ID)."""
        url = "https://in.indeed.com/viewjob?jk=abc123&from=serp&tk=xyz&vjs=3"
        result = normalize_url(url)
        
        # Should keep only jk parameter
        assert "jk=abc123" in result
        assert "from=" not in result
        assert "tk=" not in result
        assert "vjs=" not in result
    
    def test_normalization_step_4_remove_fragments(self):
        """Validate Step 4: Remove URL fragments."""
        url = "https://in.indeed.com/viewjob?jk=abc123#apply"
        result = normalize_url(url)
        
        # Fragment should be removed
        assert "#apply" not in result
        assert "#" not in result
    
    def test_normalization_step_5_remove_trailing_slashes(self):
        """Validate Step 5: Remove trailing slashes."""
        url_with_slash = "https://in.indeed.com/jobs/software-engineer-abc123/"
        url_without_slash = "https://in.indeed.com/jobs/software-engineer-abc123"
        
        # Both should normalize to the same value without trailing slash
        result_with = normalize_url(url_with_slash)
        result_without = normalize_url(url_without_slash)
        
        assert result_with == result_without
        assert not result_with.endswith("/")
    
    def test_normalization_step_6_extract_job_id(self):
        """Validate Step 6: Extract job ID from query for comparison."""
        # URLs with same job ID but different other parameters
        url1 = "https://in.indeed.com/viewjob?jk=job123&from=serp"
        url2 = "https://in.indeed.com/viewjob?jk=job123&tk=different"
        url3 = "https://in.indeed.com/viewjob?jk=job123"
        
        # All should normalize to same value (same job ID)
        assert normalize_url(url1) == normalize_url(url2) == normalize_url(url3)
        
        # URLs with different job IDs should normalize to different values
        url_different = "https://in.indeed.com/viewjob?jk=job456&from=serp"
        assert normalize_url(url1) != normalize_url(url_different)
    
    def test_property_13_url_normalization_for_deduplication(self):
        """
        Validate Property 13: URL Normalization for Deduplication
        
        For any two job URLs that differ only in query parameters, fragments,
        or trailing slashes, they should be considered duplicates after normalization.
        """
        base_job_id = "abc123def456"
        
        # Create variations of the same job URL
        variations = [
            f"https://in.indeed.com/viewjob?jk={base_job_id}",
            f"https://in.indeed.com/viewjob?jk={base_job_id}&from=serp",
            f"https://in.indeed.com/viewjob?jk={base_job_id}&tk=xyz&vjs=3",
            f"https://IN.indeed.COM/viewjob?jk={base_job_id}",
            f"https://in.indeed.com/viewjob?jk={base_job_id}#apply",
            f"https://in.indeed.com/viewjob?jk={base_job_id}&from=serp#section",
        ]
        
        # All variations should normalize to the same value
        normalized_values = [normalize_url(url) for url in variations]
        
        # Check that all normalized values are identical
        first_normalized = normalized_values[0]
        for normalized in normalized_values:
            assert normalized == first_normalized, \
                f"URL normalization failed: {normalized} != {first_normalized}"
        
        # Verify the normalized format
        assert first_normalized == f"https://in.indeed.com/viewjob?jk={base_job_id}"
    
    def test_requirement_5_4_normalize_before_comparison(self):
        """
        Validate Requirement 5.4: Deduplicator shall normalize job link URLs
        before comparison to handle URL variations.
        """
        # Simulate job records with URL variations
        job_urls = [
            "https://in.indeed.com/viewjob?jk=job1&from=serp",
            "https://IN.Indeed.COM/viewjob?jk=job1",  # Same job, different case
            "https://in.indeed.com/viewjob?jk=job2&tk=xyz",
            "https://in.indeed.com/viewjob?jk=job2#apply",  # Same job, with fragment
            "https://in.indeed.com/viewjob?jk=job3",
        ]
        
        # Normalize all URLs
        normalized = [normalize_url(url) for url in job_urls]
        
        # Check that duplicates are detected
        assert normalized[0] == normalized[1]  # job1 variations
        assert normalized[2] == normalized[3]  # job2 variations
        assert normalized[4] != normalized[0]  # job3 is different
        
        # Count unique normalized URLs
        unique_normalized = set(normalized)
        assert len(unique_normalized) == 3  # Should have 3 unique jobs
    
    def test_edge_case_no_job_id_parameter(self):
        """Test URLs without job ID parameter (e.g., search results page)."""
        search_url = "https://in.indeed.com/jobs?q=software+engineer&sort=date"
        result = normalize_url(search_url)
        
        # Should remove all query parameters if no jk parameter
        assert "q=" not in result
        assert "sort=" not in result
        assert result == "https://in.indeed.com/jobs"
    
    def test_edge_case_multiple_trailing_slashes(self):
        """Test URL with multiple trailing slashes."""
        url = "https://in.indeed.com/jobs/software-engineer///"
        result = normalize_url(url)
        
        # Should remove all trailing slashes
        assert not result.endswith("/")
        assert result == "https://in.indeed.com/jobs/software-engineer"
    
    def test_edge_case_empty_query_string(self):
        """Test URL with empty query string."""
        url = "https://in.indeed.com/viewjob?"
        result = normalize_url(url)
        
        # Should handle gracefully
        assert isinstance(result, str)
        assert "in.indeed.com" in result
    
    def test_error_handling_malformed_url(self):
        """Test that malformed URLs are handled gracefully."""
        malformed_urls = [
            "not-a-url",
            "htp://broken-protocol.com",
            "",
            "://no-scheme.com",
        ]
        
        for url in malformed_urls:
            result = normalize_url(url)
            # Should return a string without crashing
            assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
