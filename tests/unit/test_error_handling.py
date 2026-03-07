"""
Unit tests for error handling functions.

This module tests the error handling components including CAPTCHA detection,
network error handling, and selector validation.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from playwright.sync_api import Page
import sys
import os

# Add parent directory to path to import scraper module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import scraper
import config


class TestValidateSelectors:
    """Tests for the validate_selectors function."""
    
    def test_validate_selectors_all_present(self):
        """Test selector validation when all selectors are present."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.url = "https://in.indeed.com/jobs?q=test"
        
        # Mock query_selector to return elements for all selectors
        mock_element = Mock()
        mock_page.query_selector.return_value = mock_element
        
        # Call validate_selectors
        result = scraper.validate_selectors(mock_page)
        
        # Verify all selectors are marked as present
        assert result['job_card'] == True
        assert result['title'] == True
        assert result['company'] == True
        assert result['location'] == True
        assert result['link'] == True
        assert result['salary'] == True
        assert result['posted'] == True
        assert result['snippet'] == True
    
    def test_validate_selectors_some_missing(self):
        """Test selector validation when some selectors are missing."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.url = "https://in.indeed.com/jobs?q=test"
        
        # Mock query_selector to return None for some selectors
        def mock_query_selector(selector):
            # Return element for required selectors, None for optional ones
            if 'salary' in selector or 'posted' in selector:
                return None
            return Mock()
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        # Call validate_selectors
        result = scraper.validate_selectors(mock_page)
        
        # Verify required selectors are present
        assert result['job_card'] == True
        assert result['title'] == True
        assert result['company'] == True
        assert result['location'] == True
        
        # Verify optional selectors may be missing (depends on mock behavior)
        # Note: Since we're using fallback selectors, this test may need adjustment
    
    def test_validate_selectors_all_missing(self):
        """Test selector validation when all selectors are missing."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.url = "https://in.indeed.com/jobs?q=test"
        
        # Mock query_selector to return None for all selectors
        mock_page.query_selector.return_value = None
        
        # Call validate_selectors
        result = scraper.validate_selectors(mock_page)
        
        # Verify all selectors are marked as absent
        assert result['job_card'] == False
        assert result['title'] == False
        assert result['company'] == False
        assert result['location'] == False
        assert result['link'] == False
        assert result['salary'] == False
        assert result['posted'] == False
        assert result['snippet'] == False
    
    def test_validate_selectors_with_fallbacks(self):
        """Test that fallback selectors are tried when primary fails."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.url = "https://in.indeed.com/jobs?q=test"
        
        # Track which selectors were tried
        tried_selectors = []
        
        def mock_query_selector(selector):
            tried_selectors.append(selector)
            # Return None for first selector, element for second (fallback)
            if len([s for s in tried_selectors if selector in s]) == 1:
                return None
            return Mock()
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        # Call validate_selectors
        result = scraper.validate_selectors(mock_page)
        
        # Verify that multiple selectors were tried (fallbacks)
        assert len(tried_selectors) > len(config.SELECTORS)
    
    def test_validate_selectors_logs_warnings(self, caplog):
        """Test that warnings are logged for missing selectors."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.url = "https://in.indeed.com/jobs?q=test"
        
        # Mock query_selector to return None for all selectors
        mock_page.query_selector.return_value = None
        
        # Call validate_selectors
        with caplog.at_level('WARNING'):
            result = scraper.validate_selectors(mock_page)
        
        # Verify warnings were logged
        assert len(caplog.records) > 0
        assert any('Selector validation failed' in record.message for record in caplog.records)
        assert any(mock_page.url in record.message for record in caplog.records)
    
    def test_validate_selectors_returns_dict(self):
        """Test that validate_selectors returns a dictionary."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.url = "https://in.indeed.com/jobs?q=test"
        mock_page.query_selector.return_value = Mock()
        
        # Call validate_selectors
        result = scraper.validate_selectors(mock_page)
        
        # Verify return type is dict
        assert isinstance(result, dict)
        
        # Verify all expected keys are present
        expected_keys = ['job_card', 'title', 'company', 'location', 'link', 'salary', 'posted', 'snippet']
        for key in expected_keys:
            assert key in result
            assert isinstance(result[key], bool)


class TestDetectCaptcha:
    """Tests for the detect_captcha function."""
    
    def test_detect_captcha_by_keyword(self):
        """Test CAPTCHA detection by keyword in page content."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.content.return_value = "Please verify you are not a robot"
        
        # Call detect_captcha
        result = scraper.detect_captcha(mock_page)
        
        # Verify CAPTCHA detected
        assert result == True
    
    def test_detect_captcha_by_selector(self):
        """Test CAPTCHA detection by element selector."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.content.return_value = "Normal page content"
        
        # Mock query_selector to return element for CAPTCHA selector
        mock_element = Mock()
        mock_page.query_selector.return_value = mock_element
        
        # Call detect_captcha
        result = scraper.detect_captcha(mock_page)
        
        # Verify CAPTCHA detected
        assert result == True
    
    def test_detect_captcha_no_captcha(self):
        """Test CAPTCHA detection when no CAPTCHA present."""
        # Create mock page
        mock_page = Mock(spec=Page)
        mock_page.content.return_value = "Normal job listing page"
        mock_page.query_selector.return_value = None
        
        # Call detect_captcha
        result = scraper.detect_captcha(mock_page)
        
        # Verify no CAPTCHA detected
        assert result == False


class TestHandleCaptchaDetection:
    """Tests for the handle_captcha_detection function."""
    
    def test_handle_captcha_increments_count(self):
        """Test that consecutive count is incremented."""
        # Call handle_captcha_detection
        result = scraper.handle_captcha_detection("test query", 1, 0)
        
        # Verify count incremented
        assert result == 1
    
    def test_handle_captcha_logs_critical_at_threshold(self, caplog):
        """Test that critical warning is logged at threshold."""
        # Call handle_captcha_detection at threshold
        with caplog.at_level('CRITICAL'):
            result = scraper.handle_captcha_detection("test query", 3, 2)
        
        # Verify critical warning logged
        assert any('CRITICAL' in record.message for record in caplog.records)
        assert result == 3


class TestHandleNetworkError:
    """Tests for the handle_network_error function."""
    
    def test_handle_network_error_increments_count(self):
        """Test that error count is incremented."""
        # Create error tracker
        tracker = {'query': 'test', 'total_attempts': 2, 'error_count': 0}
        
        # Create mock error
        error = Exception("Network timeout")
        
        # Call handle_network_error
        result = scraper.handle_network_error(error, "https://test.com", tracker)
        
        # Verify error count incremented
        assert result['error_count'] == 1
        assert result['error_rate'] == 0.5
    
    def test_handle_network_error_logs_warning_at_threshold(self, caplog):
        """Test that warning is logged when error rate exceeds threshold."""
        # Create error tracker with high error rate
        tracker = {'query': 'test', 'total_attempts': 2, 'error_count': 1}
        
        # Create mock error
        error = Exception("Network timeout")
        
        # Call handle_network_error
        with caplog.at_level('WARNING'):
            result = scraper.handle_network_error(error, "https://test.com", tracker)
        
        # Verify warning logged
        assert any('High error rate' in record.message for record in caplog.records)
        assert result['error_rate'] > config.ERROR_RATE_THRESHOLD
    
    def test_handle_network_error_creates_tracker_if_none(self):
        """Test that error tracker is created if None provided."""
        # Create mock error
        error = Exception("Network timeout")
        
        # Call handle_network_error with no tracker
        result = scraper.handle_network_error(error, "https://test.com", None)
        
        # Verify tracker created
        assert isinstance(result, dict)
        assert 'error_count' in result
        assert 'total_attempts' in result
        assert result['error_count'] == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
