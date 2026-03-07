"""
Validation tests for Task 7.2: Create deduplication function

This test suite validates the deduplicate_jobs() function implementation
against the requirements and design specifications.

Requirements Validated:
- 5.1: Deduplicator shall identify duplicates by comparing job link URLs
- 5.2: Deduplicator shall retain only the first occurrence when duplicates identified
- 5.3: Deduplicator shall preserve original order of Job_Records during deduplication
- 5.4: Deduplicator shall normalize job link URLs before comparison

Properties Validated:
- Property 11: Deduplication by URL
- Property 12: Order Preservation During Deduplication
- Property 13: URL Normalization for Deduplication
"""

import pytest
from scraper import deduplicate_jobs, normalize_url


class TestTask72DeduplicateJobs:
    """Test suite for deduplicate_jobs function (Task 7.2)"""
    
    def test_basic_deduplication_exact_duplicates(self):
        """Test deduplication with exact duplicate URLs"""
        jobs = [
            {'title': 'Engineer 1', 'company': 'Company A', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Engineer 2', 'company': 'Company B', 'link': 'https://in.indeed.com/viewjob?jk=456'},
            {'title': 'Engineer 1 Duplicate', 'company': 'Company A', 'link': 'https://in.indeed.com/viewjob?jk=123'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 2 unique jobs (first and second)
        assert len(result) == 2
        assert result[0]['title'] == 'Engineer 1'
        assert result[1]['title'] == 'Engineer 2'
    
    def test_deduplication_with_query_parameter_variations(self):
        """Test deduplication with URLs differing only in query parameters"""
        jobs = [
            {'title': 'Engineer 1', 'link': 'https://in.indeed.com/viewjob?jk=123&from=serp'},
            {'title': 'Engineer 2', 'link': 'https://in.indeed.com/viewjob?jk=456'},
            {'title': 'Engineer 1 Dup', 'link': 'https://in.indeed.com/viewjob?jk=123&tk=xyz'},
            {'title': 'Engineer 3', 'link': 'https://in.indeed.com/viewjob?jk=789'},
            {'title': 'Engineer 2 Dup', 'link': 'https://in.indeed.com/viewjob?jk=456&from=serp&tk=abc'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 3 unique jobs (jk=123, jk=456, jk=789)
        assert len(result) == 3
        assert result[0]['title'] == 'Engineer 1'
        assert result[1]['title'] == 'Engineer 2'
        assert result[2]['title'] == 'Engineer 3'
    
    def test_deduplication_with_fragments(self):
        """Test deduplication with URLs differing only in fragments"""
        jobs = [
            {'title': 'Engineer 1', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Engineer 1 Dup', 'link': 'https://in.indeed.com/viewjob?jk=123#apply'},
            {'title': 'Engineer 2', 'link': 'https://in.indeed.com/viewjob?jk=456#section'},
            {'title': 'Engineer 2 Dup', 'link': 'https://in.indeed.com/viewjob?jk=456'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 2 unique jobs
        assert len(result) == 2
        assert result[0]['title'] == 'Engineer 1'
        assert result[1]['title'] == 'Engineer 2'
    
    def test_deduplication_with_trailing_slashes(self):
        """Test deduplication with URLs differing only in trailing slashes"""
        jobs = [
            {'title': 'Engineer 1', 'link': 'https://in.indeed.com/jobs/software-engineer-123'},
            {'title': 'Engineer 1 Dup', 'link': 'https://in.indeed.com/jobs/software-engineer-123/'},
            {'title': 'Engineer 2', 'link': 'https://in.indeed.com/jobs/python-developer-456/'},
            {'title': 'Engineer 2 Dup', 'link': 'https://in.indeed.com/jobs/python-developer-456'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 2 unique jobs
        assert len(result) == 2
        assert result[0]['title'] == 'Engineer 1'
        assert result[1]['title'] == 'Engineer 2'
    
    def test_deduplication_with_case_differences(self):
        """Test deduplication with URLs differing only in domain case"""
        jobs = [
            {'title': 'Engineer 1', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Engineer 1 Dup', 'link': 'https://IN.Indeed.COM/viewjob?jk=123'},
            {'title': 'Engineer 2', 'link': 'https://In.Indeed.Com/viewjob?jk=456'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 2 unique jobs (case-insensitive domain comparison)
        assert len(result) == 2
        assert result[0]['title'] == 'Engineer 1'
        assert result[1]['title'] == 'Engineer 2'
    
    def test_order_preservation(self):
        """Test that original order is preserved for unique records"""
        jobs = [
            {'title': 'Job A', 'link': 'https://in.indeed.com/viewjob?jk=111'},
            {'title': 'Job B', 'link': 'https://in.indeed.com/viewjob?jk=222'},
            {'title': 'Job C', 'link': 'https://in.indeed.com/viewjob?jk=333'},
            {'title': 'Job B Dup', 'link': 'https://in.indeed.com/viewjob?jk=222&from=serp'},
            {'title': 'Job D', 'link': 'https://in.indeed.com/viewjob?jk=444'},
            {'title': 'Job A Dup', 'link': 'https://in.indeed.com/viewjob?jk=111#apply'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 4 unique jobs in order: A, B, C, D
        assert len(result) == 4
        assert result[0]['title'] == 'Job A'
        assert result[1]['title'] == 'Job B'
        assert result[2]['title'] == 'Job C'
        assert result[3]['title'] == 'Job D'
    
    def test_first_occurrence_retained(self):
        """Test that first occurrence is retained when duplicates found"""
        jobs = [
            {'title': 'First', 'company': 'Company A', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Second', 'company': 'Company B', 'link': 'https://in.indeed.com/viewjob?jk=123&from=serp'},
            {'title': 'Third', 'company': 'Company C', 'link': 'https://in.indeed.com/viewjob?jk=123#apply'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 1 job, and it should be the first one
        assert len(result) == 1
        assert result[0]['title'] == 'First'
        assert result[0]['company'] == 'Company A'
    
    def test_empty_list(self):
        """Test deduplication with empty list"""
        jobs = []
        result = deduplicate_jobs(jobs)
        assert len(result) == 0
        assert result == []
    
    def test_single_job(self):
        """Test deduplication with single job"""
        jobs = [
            {'title': 'Engineer', 'link': 'https://in.indeed.com/viewjob?jk=123'}
        ]
        result = deduplicate_jobs(jobs)
        assert len(result) == 1
        assert result[0]['title'] == 'Engineer'
    
    def test_all_unique_jobs(self):
        """Test deduplication when all jobs are unique"""
        jobs = [
            {'title': 'Job 1', 'link': 'https://in.indeed.com/viewjob?jk=111'},
            {'title': 'Job 2', 'link': 'https://in.indeed.com/viewjob?jk=222'},
            {'title': 'Job 3', 'link': 'https://in.indeed.com/viewjob?jk=333'},
            {'title': 'Job 4', 'link': 'https://in.indeed.com/viewjob?jk=444'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # All jobs should be retained
        assert len(result) == 4
        assert result == jobs
    
    def test_all_duplicate_jobs(self):
        """Test deduplication when all jobs are duplicates"""
        jobs = [
            {'title': 'Job 1', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Job 2', 'link': 'https://in.indeed.com/viewjob?jk=123&from=serp'},
            {'title': 'Job 3', 'link': 'https://in.indeed.com/viewjob?jk=123#apply'},
            {'title': 'Job 4', 'link': 'https://in.indeed.com/viewjob?jk=123&tk=xyz'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Only first job should be retained
        assert len(result) == 1
        assert result[0]['title'] == 'Job 1'
    
    def test_complex_mixed_duplicates(self):
        """Test deduplication with complex mix of duplicates and unique jobs"""
        jobs = [
            {'title': 'A1', 'link': 'https://in.indeed.com/viewjob?jk=111'},
            {'title': 'B1', 'link': 'https://in.indeed.com/viewjob?jk=222&from=serp'},
            {'title': 'C1', 'link': 'https://in.indeed.com/viewjob?jk=333'},
            {'title': 'A2', 'link': 'https://in.indeed.com/viewjob?jk=111#apply'},  # Dup of A1
            {'title': 'D1', 'link': 'https://in.indeed.com/viewjob?jk=444'},
            {'title': 'B2', 'link': 'https://in.indeed.com/viewjob?jk=222'},  # Dup of B1
            {'title': 'E1', 'link': 'https://in.indeed.com/viewjob?jk=555'},
            {'title': 'C2', 'link': 'https://in.indeed.com/viewjob?jk=333&tk=xyz'},  # Dup of C1
            {'title': 'D2', 'link': 'https://in.indeed.com/viewjob?jk=444&from=serp'},  # Dup of D1
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should have 5 unique jobs: A1, B1, C1, D1, E1
        assert len(result) == 5
        assert result[0]['title'] == 'A1'
        assert result[1]['title'] == 'B1'
        assert result[2]['title'] == 'C1'
        assert result[3]['title'] == 'D1'
        assert result[4]['title'] == 'E1'
    
    def test_idempotency(self):
        """Test that deduplication is idempotent (applying twice gives same result)"""
        jobs = [
            {'title': 'Job 1', 'link': 'https://in.indeed.com/viewjob?jk=111'},
            {'title': 'Job 2', 'link': 'https://in.indeed.com/viewjob?jk=222'},
            {'title': 'Job 1 Dup', 'link': 'https://in.indeed.com/viewjob?jk=111&from=serp'},
        ]
        
        result1 = deduplicate_jobs(jobs)
        result2 = deduplicate_jobs(result1)
        
        # Applying deduplication twice should give same result
        assert len(result1) == len(result2)
        assert result1 == result2
    
    def test_property_11_deduplication_by_url(self):
        """
        Property 11: Deduplication by URL
        
        For any list of job records containing duplicate job links, the deduplicator
        should retain only the first occurrence of each unique job link.
        """
        jobs = [
            {'title': 'First Occurrence', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Unique Job', 'link': 'https://in.indeed.com/viewjob?jk=456'},
            {'title': 'Duplicate of First', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Another Unique', 'link': 'https://in.indeed.com/viewjob?jk=789'},
            {'title': 'Duplicate of Unique', 'link': 'https://in.indeed.com/viewjob?jk=456'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Should retain only first occurrence of each unique link
        assert len(result) == 3
        assert result[0]['title'] == 'First Occurrence'
        assert result[1]['title'] == 'Unique Job'
        assert result[2]['title'] == 'Another Unique'
    
    def test_property_12_order_preservation(self):
        """
        Property 12: Order Preservation During Deduplication
        
        For any list of job records, deduplication should preserve the relative
        order of the unique records.
        """
        jobs = [
            {'title': 'Z Job', 'link': 'https://in.indeed.com/viewjob?jk=999'},
            {'title': 'A Job', 'link': 'https://in.indeed.com/viewjob?jk=111'},
            {'title': 'M Job', 'link': 'https://in.indeed.com/viewjob?jk=555'},
            {'title': 'Z Dup', 'link': 'https://in.indeed.com/viewjob?jk=999'},
            {'title': 'B Job', 'link': 'https://in.indeed.com/viewjob?jk=222'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Order should be preserved: Z, A, M, B (not alphabetically sorted)
        assert len(result) == 4
        assert result[0]['title'] == 'Z Job'
        assert result[1]['title'] == 'A Job'
        assert result[2]['title'] == 'M Job'
        assert result[3]['title'] == 'B Job'
    
    def test_property_13_url_normalization(self):
        """
        Property 13: URL Normalization for Deduplication
        
        For any two job URLs that differ only in query parameters, fragments,
        or trailing slashes, they should be considered duplicates after normalization.
        """
        # Test query parameter variations
        jobs_query = [
            {'title': 'Original', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'With extra params', 'link': 'https://in.indeed.com/viewjob?jk=123&from=serp&tk=xyz'},
        ]
        result_query = deduplicate_jobs(jobs_query)
        assert len(result_query) == 1
        
        # Test fragment variations
        jobs_fragment = [
            {'title': 'Original', 'link': 'https://in.indeed.com/viewjob?jk=456'},
            {'title': 'With fragment', 'link': 'https://in.indeed.com/viewjob?jk=456#apply'},
        ]
        result_fragment = deduplicate_jobs(jobs_fragment)
        assert len(result_fragment) == 1
        
        # Test trailing slash variations
        jobs_slash = [
            {'title': 'Original', 'link': 'https://in.indeed.com/jobs/engineer-789'},
            {'title': 'With slash', 'link': 'https://in.indeed.com/jobs/engineer-789/'},
        ]
        result_slash = deduplicate_jobs(jobs_slash)
        assert len(result_slash) == 1
        
        # Test combined variations
        jobs_combined = [
            {'title': 'Original', 'link': 'https://in.indeed.com/viewjob?jk=999'},
            {'title': 'All variations', 'link': 'https://IN.Indeed.COM/viewjob?jk=999&from=serp#section/'},
        ]
        result_combined = deduplicate_jobs(jobs_combined)
        assert len(result_combined) == 1
    
    def test_requirement_5_1_identify_duplicates_by_url(self):
        """
        Requirement 5.1: Deduplicator shall identify duplicates by comparing job link URLs
        """
        jobs = [
            {'title': 'Job 1', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Job 2', 'link': 'https://in.indeed.com/viewjob?jk=456'},
            {'title': 'Job 1 Duplicate', 'link': 'https://in.indeed.com/viewjob?jk=123'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Duplicates should be identified by comparing URLs
        assert len(result) == 2
    
    def test_requirement_5_2_retain_first_occurrence(self):
        """
        Requirement 5.2: Deduplicator shall retain only the first occurrence
        """
        jobs = [
            {'title': 'First', 'company': 'A', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Second', 'company': 'B', 'link': 'https://in.indeed.com/viewjob?jk=123'},
            {'title': 'Third', 'company': 'C', 'link': 'https://in.indeed.com/viewjob?jk=123'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Only first occurrence should be retained
        assert len(result) == 1
        assert result[0]['title'] == 'First'
        assert result[0]['company'] == 'A'
    
    def test_requirement_5_3_preserve_order(self):
        """
        Requirement 5.3: Deduplicator shall preserve original order of Job_Records
        """
        jobs = [
            {'title': 'Third', 'link': 'https://in.indeed.com/viewjob?jk=333'},
            {'title': 'First', 'link': 'https://in.indeed.com/viewjob?jk=111'},
            {'title': 'Second', 'link': 'https://in.indeed.com/viewjob?jk=222'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # Order should be preserved (not sorted)
        assert result[0]['title'] == 'Third'
        assert result[1]['title'] == 'First'
        assert result[2]['title'] == 'Second'
    
    def test_requirement_5_4_normalize_urls(self):
        """
        Requirement 5.4: Deduplicator shall normalize job link URLs before comparison
        """
        jobs = [
            {'title': 'Job 1', 'link': 'https://in.indeed.com/viewjob?jk=123&from=serp'},
            {'title': 'Job 2', 'link': 'https://IN.Indeed.COM/viewjob?jk=123#apply/'},
        ]
        
        result = deduplicate_jobs(jobs)
        
        # URLs should be normalized before comparison (different formats, same job)
        assert len(result) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
