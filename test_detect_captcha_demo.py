"""
Quick demo to verify detect_captcha function works correctly.
"""

from unittest.mock import Mock
from scraper import detect_captcha
import config

def demo_captcha_detection():
    """Demonstrate CAPTCHA detection functionality."""
    
    print("=" * 60)
    print("CAPTCHA Detection Function Demo")
    print("=" * 60)
    
    # Test 1: Page with CAPTCHA keyword
    print("\n1. Testing page with 'captcha' keyword:")
    mock_page = Mock()
    mock_page.content.return_value = "<html><body>Please solve the captcha</body></html>"
    mock_page.query_selector.return_value = None
    result = detect_captcha(mock_page)
    print(f"   Result: {result} (Expected: True)")
    
    # Test 2: Page with CAPTCHA element
    print("\n2. Testing page with #recaptcha element:")
    mock_page = Mock()
    mock_page.content.return_value = "<html><body>Normal content</body></html>"
    def mock_query_selector(selector):
        if selector == '#recaptcha':
            return Mock()
        return None
    mock_page.query_selector.side_effect = mock_query_selector
    result = detect_captcha(mock_page)
    print(f"   Result: {result} (Expected: True)")
    
    # Test 3: Normal page without CAPTCHA
    print("\n3. Testing normal page without CAPTCHA:")
    mock_page = Mock()
    mock_page.content.return_value = "<html><body>Job listings here</body></html>"
    mock_page.query_selector.return_value = None
    result = detect_captcha(mock_page)
    print(f"   Result: {result} (Expected: False)")
    
    # Display configuration
    print("\n" + "=" * 60)
    print("Configuration from config.py:")
    print("=" * 60)
    print(f"CAPTCHA_KEYWORDS: {config.CAPTCHA_KEYWORDS}")
    print(f"CAPTCHA_SELECTORS: {config.CAPTCHA_SELECTORS}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    demo_captcha_detection()
