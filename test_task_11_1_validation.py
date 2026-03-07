"""
Unit tests for Task 11.1: CAPTCHA Detection Function

This test suite validates the detect_captcha() function implementation,
ensuring it correctly detects CAPTCHA challenges using both keyword search
and element selector methods.

Requirements Validated:
- 10.4: Detect CAPTCHA by searching for common CAPTCHA-related text patterns
- 10.5: Detect CAPTCHA by searching for common CAPTCHA-related element selectors

Properties Validated:
- Property 22: CAPTCHA Detection by Text Patterns
- Property 23: CAPTCHA Detection by Element Selectors
"""

import pytest
from unittest.mock import Mock, MagicMock
from scraper import detect_captcha
import config


class TestCaptchaDetection:
    """Test suite for CAPTCHA detection functionality."""
    
    def test_detect_captcha_by_keyword_captcha(self):
        """Test CAPTCHA detection when 'captcha' keyword is present in page content."""
        # Create mock page with CAPTCHA keyword in content
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Please solve the captcha to continue</body></html>"
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when 'captcha' keyword is present"
    
    def test_detect_captcha_by_keyword_robot(self):
        """Test CAPTCHA detection when 'robot' keyword is present in page content."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Are you a robot? Please verify.</body></html>"
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when 'robot' keyword is present"
    
    def test_detect_captcha_by_keyword_verify(self):
        """Test CAPTCHA detection when 'verify' keyword is present in page content."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Please verify you're human</body></html>"
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when 'verify' keyword is present"
    
    def test_detect_captcha_by_keyword_case_insensitive(self):
        """Test CAPTCHA detection is case-insensitive for keywords."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Please solve the CAPTCHA to continue</body></html>"
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA regardless of case"
    
    def test_detect_captcha_by_selector_recaptcha(self):
        """Test CAPTCHA detection when #recaptcha element is present."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Normal page content</body></html>"
        
        # Mock query_selector to return element for #recaptcha
        def mock_query_selector(selector):
            if selector == '#recaptcha':
                return Mock()  # Return mock element
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when #recaptcha element is present"
    
    def test_detect_captcha_by_selector_g_recaptcha(self):
        """Test CAPTCHA detection when .g-recaptcha element is present."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Normal page content</body></html>"
        
        # Mock query_selector to return element for .g-recaptcha
        def mock_query_selector(selector):
            if selector == '.g-recaptcha':
                return Mock()  # Return mock element
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when .g-recaptcha element is present"
    
    def test_detect_captcha_by_selector_captcha_id(self):
        """Test CAPTCHA detection when #captcha element is present."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Normal page content</body></html>"
        
        # Mock query_selector to return element for #captcha
        def mock_query_selector(selector):
            if selector == '#captcha':
                return Mock()  # Return mock element
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when #captcha element is present"
    
    def test_no_captcha_detected_normal_page(self):
        """Test that normal pages without CAPTCHA indicators return False."""
        mock_page = Mock()
        mock_page.content.return_value = """
        <html>
            <body>
                <h1>Job Listings</h1>
                <div class="job">Software Engineer at Tech Corp</div>
                <div class="job">Python Developer at StartUp Inc</div>
            </body>
        </html>
        """
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is False, "Should not detect CAPTCHA on normal job listing page"
    
    def test_detect_captcha_uses_config_keywords(self):
        """Test that detect_captcha uses keywords from config.CAPTCHA_KEYWORDS."""
        # Verify config has expected keywords
        assert 'captcha' in config.CAPTCHA_KEYWORDS, "Config should contain 'captcha' keyword"
        assert 'robot' in config.CAPTCHA_KEYWORDS, "Config should contain 'robot' keyword"
        assert 'verify' in config.CAPTCHA_KEYWORDS, "Config should contain 'verify' keyword"
    
    def test_detect_captcha_uses_config_selectors(self):
        """Test that detect_captcha uses selectors from config.CAPTCHA_SELECTORS."""
        # Verify config has expected selectors
        assert '#recaptcha' in config.CAPTCHA_SELECTORS, "Config should contain '#recaptcha' selector"
        assert '.g-recaptcha' in config.CAPTCHA_SELECTORS, "Config should contain '.g-recaptcha' selector"
        assert '#captcha' in config.CAPTCHA_SELECTORS, "Config should contain '#captcha' selector"
    
    def test_detect_captcha_keyword_in_middle_of_text(self):
        """Test CAPTCHA detection when keyword appears in middle of longer text."""
        mock_page = Mock()
        mock_page.content.return_value = """
        <html>
            <body>
                <p>We need to verify that you are a human user before proceeding.</p>
                <p>This helps us protect our site from automated bots.</p>
            </body>
        </html>
        """
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when keyword is embedded in text"
    
    def test_detect_captcha_multiple_keywords_present(self):
        """Test CAPTCHA detection when multiple keywords are present."""
        mock_page = Mock()
        mock_page.content.return_value = """
        <html>
            <body>
                <h1>CAPTCHA Verification</h1>
                <p>Please verify you are not a robot</p>
            </body>
        </html>
        """
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when multiple keywords are present"
    
    def test_detect_captcha_both_keyword_and_selector(self):
        """Test CAPTCHA detection when both keyword and selector are present."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Please solve the captcha</body></html>"
        
        # Mock query_selector to return element for #recaptcha
        def mock_query_selector(selector):
            if selector == '#recaptcha':
                return Mock()
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when both keyword and selector are present"
    
    def test_detect_captcha_error_handling(self):
        """Test that detect_captcha handles errors gracefully and returns False."""
        mock_page = Mock()
        mock_page.content.side_effect = Exception("Page content unavailable")
        
        result = detect_captcha(mock_page)
        
        assert result is False, "Should return False when error occurs during detection"
    
    def test_detect_captcha_query_selector_error(self):
        """Test that detect_captcha handles query_selector errors gracefully."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Normal content</body></html>"
        mock_page.query_selector.side_effect = Exception("Selector query failed")
        
        result = detect_captcha(mock_page)
        
        assert result is False, "Should return False when query_selector fails"
    
    def test_detect_captcha_empty_page(self):
        """Test CAPTCHA detection on empty page content."""
        mock_page = Mock()
        mock_page.content.return_value = ""
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is False, "Should return False for empty page content"
    
    def test_detect_captcha_partial_keyword_match(self):
        """Test that partial keyword matches are detected (e.g., 'verify you are human' contains 'verify')."""
        mock_page = Mock()
        mock_page.content.return_value = "<html><body>Please verify you are human to continue</body></html>"
        mock_page.query_selector.return_value = None
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA when keyword is part of a phrase"


class TestCaptchaDetectionIntegration:
    """Integration tests for CAPTCHA detection with realistic HTML."""
    
    def test_detect_captcha_realistic_recaptcha_page(self):
        """Test CAPTCHA detection with realistic reCAPTCHA HTML structure."""
        mock_page = Mock()
        mock_page.content.return_value = """
        <!DOCTYPE html>
        <html>
        <head><title>Verification Required</title></head>
        <body>
            <h1>Please verify you're not a robot</h1>
            <div class="g-recaptcha" data-sitekey="6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"></div>
            <script src="https://www.google.com/recaptcha/api.js"></script>
        </body>
        </html>
        """
        
        # Mock query_selector to find .g-recaptcha
        def mock_query_selector(selector):
            if selector == '.g-recaptcha':
                return Mock()
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA on realistic reCAPTCHA page"
    
    def test_detect_captcha_indeed_style_challenge(self):
        """Test CAPTCHA detection with Indeed-style challenge page."""
        mock_page = Mock()
        mock_page.content.return_value = """
        <!DOCTYPE html>
        <html>
        <head><title>Indeed - Verify</title></head>
        <body>
            <div class="content">
                <h1>One more step...</h1>
                <p>Please verify you're a human to continue to Indeed.</p>
                <div id="captcha-container">
                    <div id="recaptcha"></div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Mock query_selector to find #recaptcha
        def mock_query_selector(selector):
            if selector == '#recaptcha':
                return Mock()
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = detect_captcha(mock_page)
        
        assert result is True, "Should detect CAPTCHA on Indeed-style challenge page"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
