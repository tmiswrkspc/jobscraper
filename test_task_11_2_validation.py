"""
Validation tests for Task 11.2: Create CAPTCHA handling function

This test file validates the handle_captcha_detection() function implementation.

Tests verify:
1. Function logs warning with query and page number
2. Function tracks consecutive CAPTCHA count
3. Function logs critical warning at threshold (3+ consecutive)
4. Function returns updated count
"""

import pytest
import logging
from scraper import handle_captcha_detection
import config


def test_handle_captcha_single_detection(caplog):
    """Test that single CAPTCHA detection logs warning with query and page number."""
    caplog.set_level(logging.WARNING)
    
    query = "software engineer Bangalore"
    page_num = 2
    consecutive_count = 0
    
    # Call function
    result = handle_captcha_detection(query, page_num, consecutive_count)
    
    # Verify warning was logged
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "WARNING"
    
    # Verify message contains query and page number
    message = caplog.records[0].message
    assert query in message
    assert f"page {page_num}" in message
    assert "consecutive: 1" in message
    
    # Verify count was incremented
    assert result == 1


def test_handle_captcha_consecutive_tracking(caplog):
    """Test that consecutive CAPTCHA count is tracked correctly."""
    caplog.set_level(logging.WARNING)
    
    query = "python developer"
    consecutive = 0
    
    # First CAPTCHA
    consecutive = handle_captcha_detection(query, 1, consecutive)
    assert consecutive == 1
    
    # Second CAPTCHA
    consecutive = handle_captcha_detection(query, 2, consecutive)
    assert consecutive == 2
    
    # Verify two warnings logged
    assert len(caplog.records) == 2


def test_handle_captcha_critical_warning_at_threshold(caplog):
    """Test that critical warning is logged at threshold (3 consecutive)."""
    caplog.set_level(logging.WARNING)
    
    query = "data analyst"
    consecutive = 0
    
    # First two CAPTCHAs - should only log warnings
    consecutive = handle_captcha_detection(query, 1, consecutive)
    consecutive = handle_captcha_detection(query, 2, consecutive)
    
    # Check no critical warnings yet
    critical_logs = [r for r in caplog.records if r.levelname == "CRITICAL"]
    assert len(critical_logs) == 0
    
    # Third CAPTCHA - should trigger critical warning
    caplog.clear()
    consecutive = handle_captcha_detection(query, 3, consecutive)
    
    # Verify critical warning was logged
    critical_logs = [r for r in caplog.records if r.levelname == "CRITICAL"]
    assert len(critical_logs) == 1
    
    # Verify critical message content
    critical_message = critical_logs[0].message
    assert "CRITICAL" in critical_message
    assert "3 consecutive CAPTCHAs" in critical_message
    assert "blocking" in critical_message.lower()


def test_handle_captcha_critical_warning_above_threshold(caplog):
    """Test that critical warning continues to be logged above threshold."""
    caplog.set_level(logging.WARNING)
    
    query = "frontend developer"
    consecutive = 3  # Start at threshold
    
    # Fourth CAPTCHA - should still log critical
    consecutive = handle_captcha_detection(query, 4, consecutive)
    
    # Verify critical warning was logged
    critical_logs = [r for r in caplog.records if r.levelname == "CRITICAL"]
    assert len(critical_logs) == 1
    assert consecutive == 4


def test_handle_captcha_uses_config_threshold(caplog):
    """Test that function uses CONSECUTIVE_CAPTCHA_THRESHOLD from config."""
    caplog.set_level(logging.WARNING)
    
    query = "test query"
    
    # Verify threshold is 3 (as per config)
    assert config.CONSECUTIVE_CAPTCHA_THRESHOLD == 3
    
    # Test below threshold (should not trigger critical)
    # Function increments first, so pass threshold - 2 to get threshold - 1 after increment
    consecutive = config.CONSECUTIVE_CAPTCHA_THRESHOLD - 2
    handle_captcha_detection(query, 1, consecutive)
    
    critical_logs = [r for r in caplog.records if r.levelname == "CRITICAL"]
    assert len(critical_logs) == 0
    
    # Test at threshold (should trigger critical)
    # Function increments first, so pass threshold - 1 to get threshold after increment
    caplog.clear()
    consecutive = config.CONSECUTIVE_CAPTCHA_THRESHOLD - 1
    handle_captcha_detection(query, 2, consecutive)
    
    critical_logs = [r for r in caplog.records if r.levelname == "CRITICAL"]
    assert len(critical_logs) == 1


def test_handle_captcha_return_value():
    """Test that function returns incremented count."""
    query = "test"
    
    # Test with various starting counts
    assert handle_captcha_detection(query, 1, 0) == 1
    assert handle_captcha_detection(query, 1, 1) == 2
    assert handle_captcha_detection(query, 1, 5) == 6
    assert handle_captcha_detection(query, 1, 10) == 11


def test_handle_captcha_default_consecutive_count():
    """Test that consecutive_count defaults to 0."""
    query = "test"
    page_num = 1
    
    # Call without consecutive_count parameter
    result = handle_captcha_detection(query, page_num)
    
    # Should return 1 (0 + 1)
    assert result == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
