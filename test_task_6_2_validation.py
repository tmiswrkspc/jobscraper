"""
Validation tests for Task 6.2: Create page extraction function

This test file validates the extract_jobs_from_page() function implementation.
It tests the function's ability to:
- Find all job card elements using container selector
- Call extract_single_job() for each element
- Filter out None results (invalid records)
- Return list of valid job records

Requirements validated: 4.1, 4.2, 4.3, 4.4, 4.5
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from scraper import extract_jobs_from_page


def test_extract_jobs_from_page_with_valid_jobs():
    """Test extraction with multiple valid job cards"""
    # Create mock page
    mock_page = Mock()
    mock_page.url = "https://in.indeed.com/jobs?q=test"
    
    # Create mock job elements
    mock_job1 = Mock()
    mock_job2 = Mock()
    mock_job3 = Mock()
    
    # Mock query_selector_all to return job elements
    mock_page.query_selector_all.return_value = [mock_job1, mock_job2, mock_job3]
    
    # Mock extract_single_job to return valid job records
    valid_job1 = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'link': 'https://in.indeed.com/job1',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    valid_job2 = {
        'title': 'Python Developer',
        'company': 'Dev Inc',
        'location': 'Mumbai',
        'link': 'https://in.indeed.com/job2',
        'salary': '₹10,00,000',
        'posted_date': '2 days ago',
        'description': 'Great opportunity'
    }
    
    valid_job3 = {
        'title': 'Data Analyst',
        'company': 'Data Co',
        'location': 'Delhi',
        'link': 'https://in.indeed.com/job3',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    with patch('scraper.extract_single_job') as mock_extract:
        mock_extract.side_effect = [valid_job1, valid_job2, valid_job3]
        
        # Call the function
        result = extract_jobs_from_page(mock_page)
        
        # Verify results
        assert len(result) == 3
        assert result[0]['title'] == 'Software Engineer'
        assert result[1]['title'] == 'Python Developer'
        assert result[2]['title'] == 'Data Analyst'
        
        # Verify extract_single_job was called for each element
        assert mock_extract.call_count == 3


def test_extract_jobs_from_page_filters_none_results():
    """Test that None results (invalid records) are filtered out"""
    # Create mock page
    mock_page = Mock()
    mock_page.url = "https://in.indeed.com/jobs?q=test"
    
    # Create mock job elements
    mock_job1 = Mock()
    mock_job2 = Mock()
    mock_job3 = Mock()
    mock_job4 = Mock()
    
    # Mock query_selector_all to return job elements
    mock_page.query_selector_all.return_value = [mock_job1, mock_job2, mock_job3, mock_job4]
    
    # Mock extract_single_job to return mix of valid and None
    valid_job1 = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'link': 'https://in.indeed.com/job1',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    valid_job2 = {
        'title': 'Data Analyst',
        'company': 'Data Co',
        'location': 'Delhi',
        'link': 'https://in.indeed.com/job3',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    with patch('scraper.extract_single_job') as mock_extract:
        # Return valid, None, valid, None pattern
        mock_extract.side_effect = [valid_job1, None, valid_job2, None]
        
        # Call the function
        result = extract_jobs_from_page(mock_page)
        
        # Verify only valid jobs are returned
        assert len(result) == 2
        assert result[0]['title'] == 'Software Engineer'
        assert result[1]['title'] == 'Data Analyst'
        
        # Verify extract_single_job was called for all elements
        assert mock_extract.call_count == 4


def test_extract_jobs_from_page_no_job_cards():
    """Test behavior when no job cards are found on page"""
    # Create mock page
    mock_page = Mock()
    mock_page.url = "https://in.indeed.com/jobs?q=test"
    
    # Mock query_selector_all to return empty list
    mock_page.query_selector_all.return_value = []
    
    # Call the function
    result = extract_jobs_from_page(mock_page)
    
    # Verify empty list is returned
    assert result == []
    assert len(result) == 0


def test_extract_jobs_from_page_uses_fallback_selectors():
    """Test that function tries fallback selectors if primary fails"""
    # Create mock page
    mock_page = Mock()
    mock_page.url = "https://in.indeed.com/jobs?q=test"
    
    # Create mock job element
    mock_job = Mock()
    
    # Mock query_selector_all to fail on first call, succeed on second
    mock_page.query_selector_all.side_effect = [
        [],  # First selector returns empty
        [mock_job]  # Second selector returns job
    ]
    
    valid_job = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'link': 'https://in.indeed.com/job1',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    with patch('scraper.extract_single_job') as mock_extract:
        mock_extract.return_value = valid_job
        
        # Call the function
        result = extract_jobs_from_page(mock_page)
        
        # Verify job was extracted using fallback selector
        assert len(result) == 1
        assert result[0]['title'] == 'Software Engineer'


def test_extract_jobs_from_page_handles_extraction_errors():
    """Test that extraction errors for individual jobs don't stop the process"""
    # Create mock page
    mock_page = Mock()
    mock_page.url = "https://in.indeed.com/jobs?q=test"
    
    # Create mock job elements
    mock_job1 = Mock()
    mock_job2 = Mock()
    mock_job3 = Mock()
    
    # Mock query_selector_all to return job elements
    mock_page.query_selector_all.return_value = [mock_job1, mock_job2, mock_job3]
    
    valid_job1 = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'link': 'https://in.indeed.com/job1',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    valid_job3 = {
        'title': 'Data Analyst',
        'company': 'Data Co',
        'location': 'Delhi',
        'link': 'https://in.indeed.com/job3',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    with patch('scraper.extract_single_job') as mock_extract:
        # First succeeds, second raises exception, third succeeds
        mock_extract.side_effect = [valid_job1, Exception("Extraction error"), valid_job3]
        
        # Call the function
        result = extract_jobs_from_page(mock_page)
        
        # Verify that valid jobs are still extracted despite error
        assert len(result) == 2
        assert result[0]['title'] == 'Software Engineer'
        assert result[1]['title'] == 'Data Analyst'


def test_extract_jobs_from_page_returns_list():
    """Test that function always returns a list"""
    # Create mock page
    mock_page = Mock()
    mock_page.url = "https://in.indeed.com/jobs?q=test"
    
    # Test with no job cards
    mock_page.query_selector_all.return_value = []
    result = extract_jobs_from_page(mock_page)
    assert isinstance(result, list)
    
    # Test with job cards
    mock_job = Mock()
    mock_page.query_selector_all.return_value = [mock_job]
    
    valid_job = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'link': 'https://in.indeed.com/job1',
        'salary': None,
        'posted_date': None,
        'description': None
    }
    
    with patch('scraper.extract_single_job') as mock_extract:
        mock_extract.return_value = valid_job
        result = extract_jobs_from_page(mock_page)
        assert isinstance(result, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
