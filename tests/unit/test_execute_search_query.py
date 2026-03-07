"""
Unit tests for execute_search_query function (Task 12.1).

Tests the single query execution function that orchestrates:
- URL construction and pagination
- Page navigation with timeout
- Anti-detection behavior
- CAPTCHA detection and handling
- Job extraction
- Network error handling
- Random delays between pages
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from scraper import execute_search_query
import config

# Create a mock TimeoutError for testing
class MockTimeoutError(Exception):
    """Mock Playwright TimeoutError for testing."""
    pass


class TestExecuteSearchQuery:
    """Test suite for execute_search_query function."""
    
    def test_successful_execution_single_page(self):
        """Test successful execution with single page returning jobs."""
        # Create mock page
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        # Mock all the functions called by execute_search_query
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.validate_selectors') as mock_validate, \
             patch('scraper.extract_jobs_from_page') as mock_extract, \
             patch('scraper.random_delay') as mock_delay:
            
            # Setup mocks
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = ["https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"]
            mock_captcha.return_value = False
            mock_validate.return_value = {
                'job_card': True, 'title': True, 'company': True,
                'location': True, 'link': True
            }
            mock_extract.return_value = [
                {
                    'title': 'Python Developer',
                    'company': 'Tech Corp',
                    'location': 'Bangalore',
                    'link': 'https://in.indeed.com/viewjob?jk=123',
                    'salary': None,
                    'posted_date': '2 days ago',
                    'description': 'Great opportunity'
                }
            ]
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=1)
            
            # Verify results
            assert len(result) == 1
            assert result[0]['title'] == 'Python Developer'
            assert result[0]['company'] == 'Tech Corp'
            
            # Verify function calls
            mock_construct.assert_called_once_with("python developer")
            mock_pagination.assert_called_once()
            mock_page.goto.assert_called_once()
            mock_captcha.assert_called_once_with(mock_page)
            mock_anti_detection.assert_called_once_with(mock_page)
            mock_extract.assert_called_once_with(mock_page)
            # No delay for single page
            mock_delay.assert_not_called()
    
    def test_successful_execution_multiple_pages(self):
        """Test successful execution with multiple pages."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.validate_selectors') as mock_validate, \
             patch('scraper.extract_jobs_from_page') as mock_extract, \
             patch('scraper.random_delay') as mock_delay:
            
            # Setup mocks for 3 pages
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = [
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=100"
            ]
            mock_captcha.return_value = False
            mock_validate.return_value = {'job_card': True, 'title': True, 'company': True, 'location': True, 'link': True}
            
            # Return different jobs for each page
            mock_extract.side_effect = [
                [{'title': 'Job 1', 'company': 'Company 1', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job1'}],
                [{'title': 'Job 2', 'company': 'Company 2', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job2'}],
                [{'title': 'Job 3', 'company': 'Company 3', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job3'}]
            ]
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=3)
            
            # Verify results
            assert len(result) == 3
            assert result[0]['title'] == 'Job 1'
            assert result[1]['title'] == 'Job 2'
            assert result[2]['title'] == 'Job 3'
            
            # Verify page.goto called 3 times
            assert mock_page.goto.call_count == 3
            
            # Verify random_delay called 2 times (not after last page)
            assert mock_delay.call_count == 2
            mock_delay.assert_called_with(config.MIN_DELAY, config.MAX_DELAY)
    
    def test_network_error_handling(self):
        """Test that network errors are handled gracefully and execution continues."""
        mock_page = Mock()
        
        # Import the real TimeoutError to use in the test
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        
        # First page fails, second page succeeds
        mock_page.goto = Mock(side_effect=[
            PlaywrightTimeoutError("Timeout"),
            None  # Second call succeeds
        ])
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.handle_network_error') as mock_handle_error, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.validate_selectors') as mock_validate, \
             patch('scraper.extract_jobs_from_page') as mock_extract, \
             patch('scraper.random_delay') as mock_delay:
            
            # Setup mocks
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = [
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50"
            ]
            mock_captcha.return_value = False
            mock_validate.return_value = {'job_card': True, 'title': True, 'company': True, 'location': True, 'link': True}
            mock_extract.return_value = [
                {'title': 'Job from page 2', 'company': 'Company', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job2'}
            ]
            mock_handle_error.return_value = {'query': 'python developer', 'total_attempts': 2, 'error_count': 1}
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=2)
            
            # Verify results - should only have jobs from second page
            assert len(result) == 1
            assert result[0]['title'] == 'Job from page 2'
            
            # Verify error handler was called
            mock_handle_error.assert_called_once()
            
            # Verify extraction only called once (for successful page)
            mock_extract.assert_called_once()
    
    def test_captcha_detection_and_skip(self):
        """Test that CAPTCHA detection causes page to be skipped."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.handle_captcha_detection') as mock_handle_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.extract_jobs_from_page') as mock_extract, \
             patch('scraper.random_delay') as mock_delay:
            
            # Setup mocks - first page has CAPTCHA, second page is clean
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = [
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50"
            ]
            mock_captcha.side_effect = [True, False]  # CAPTCHA on first page only
            mock_handle_captcha.return_value = 1  # Return consecutive count
            mock_extract.return_value = [
                {'title': 'Job from page 2', 'company': 'Company', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job2'}
            ]
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=2)
            
            # Verify results - should only have jobs from second page (first was skipped)
            assert len(result) == 1
            assert result[0]['title'] == 'Job from page 2'
            
            # Verify CAPTCHA handler was called
            mock_handle_captcha.assert_called_once()
            
            # Verify anti-detection only called once (for non-CAPTCHA page)
            mock_anti_detection.assert_called_once()
            
            # Verify extraction only called once (for non-CAPTCHA page)
            mock_extract.assert_called_once()
    
    def test_consecutive_captcha_tracking(self):
        """Test that consecutive CAPTCHAs are tracked correctly."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.handle_captcha_detection') as mock_handle_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.extract_jobs_from_page') as mock_extract:
            
            # Setup mocks - all pages have CAPTCHA
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = [
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=100"
            ]
            mock_captcha.return_value = True  # All pages have CAPTCHA
            mock_handle_captcha.side_effect = [1, 2, 3]  # Increment consecutive count
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=3)
            
            # Verify results - should be empty (all pages skipped)
            assert len(result) == 0
            
            # Verify CAPTCHA handler called 3 times with incrementing counts
            assert mock_handle_captcha.call_count == 3
            calls = mock_handle_captcha.call_args_list
            assert calls[0][0][2] == 0  # First call with count 0
            assert calls[1][0][2] == 1  # Second call with count 1
            assert calls[2][0][2] == 2  # Third call with count 2
            
            # Verify extraction never called
            mock_extract.assert_not_called()
    
    def test_consecutive_captcha_reset_on_success(self):
        """Test that consecutive CAPTCHA counter resets on successful page load."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.handle_captcha_detection') as mock_handle_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.validate_selectors') as mock_validate, \
             patch('scraper.extract_jobs_from_page') as mock_extract:
            
            # Setup mocks - CAPTCHA, success, CAPTCHA pattern
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = [
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=100"
            ]
            mock_captcha.side_effect = [True, False, True]  # CAPTCHA, success, CAPTCHA
            mock_handle_captcha.side_effect = [1, 1]  # Should reset after success
            mock_validate.return_value = {'job_card': True, 'title': True, 'company': True, 'location': True, 'link': True}
            mock_extract.return_value = [{'title': 'Job', 'company': 'Company', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job'}]
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=3)
            
            # Verify CAPTCHA handler called twice
            assert mock_handle_captcha.call_count == 2
            calls = mock_handle_captcha.call_args_list
            # First CAPTCHA: count should be 0
            assert calls[0][0][2] == 0
            # Second CAPTCHA: count should be 0 (reset after successful page)
            assert calls[1][0][2] == 0
    
    def test_empty_page_extraction(self):
        """Test handling of pages with no jobs."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.validate_selectors') as mock_validate, \
             patch('scraper.extract_jobs_from_page') as mock_extract:
            
            # Setup mocks
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = ["https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"]
            mock_captcha.return_value = False
            mock_validate.return_value = {'job_card': True, 'title': True, 'company': True, 'location': True, 'link': True}
            mock_extract.return_value = []  # No jobs found
            
            # Execute function
            result = execute_search_query(mock_page, "python developer", max_pages=1)
            
            # Verify results - should be empty
            assert len(result) == 0
            
            # Verify extraction was still called
            mock_extract.assert_called_once()
    
    def test_extraction_error_handling(self):
        """Test that extraction errors are handled gracefully."""
        mock_page = Mock()
        mock_page.goto = Mock()
        mock_page.url = "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0"
        
        with patch('scraper.construct_search_url') as mock_construct, \
             patch('scraper.get_pagination_urls') as mock_pagination, \
             patch('scraper.detect_captcha') as mock_captcha, \
             patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
             patch('scraper.validate_selectors') as mock_validate, \
             patch('scraper.extract_jobs_from_page') as mock_extract:
            
            # Setup mocks - extraction raises exception on first page, succeeds on second
            mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer&sort=date"
            mock_pagination.return_value = [
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=0",
                "https://in.indeed.com/jobs?q=python+developer&sort=date&start=50"
            ]
            mock_captcha.return_value = False
            mock_validate.return_value = {'job_card': True, 'title': True, 'company': True, 'location': True, 'link': True}
            mock_extract.side_effect = [
                Exception("Extraction failed"),
                [{'title': 'Job', 'company': 'Company', 'location': 'Bangalore', 'link': 'https://in.indeed.com/job'}]
            ]
            
            # Execute function - should not raise exception
            result = execute_search_query(mock_page, "python developer", max_pages=2)
            
            # Verify results - should only have jobs from second page
            assert len(result) == 1
            assert result[0]['title'] == 'Job'
            
            # Verify extraction was called twice
            assert mock_extract.call_count == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
