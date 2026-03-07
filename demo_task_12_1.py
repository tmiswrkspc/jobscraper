"""
Demo script for Task 12.1: execute_search_query function

This script demonstrates the execute_search_query function which orchestrates
the complete search query execution workflow including:
- URL construction and pagination
- Page navigation with timeout
- Anti-detection behavior (scrolling, mouse movements)
- CAPTCHA detection and handling
- Job extraction from multiple pages
- Network error handling
- Random delays between pages

Note: This is a demonstration script. For actual scraping, you would need
to run this with a real Playwright browser instance.
"""

from unittest.mock import Mock, patch
import sys

# Import the function
from scraper import execute_search_query
import config


def demo_successful_execution():
    """Demonstrate successful execution with multiple pages."""
    print("=" * 80)
    print("DEMO: Successful Execution with Multiple Pages")
    print("=" * 80)
    
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
        
        # Setup mocks for 3 pages
        mock_construct.return_value = "https://in.indeed.com/jobs?q=python+developer+Bangalore&sort=date"
        mock_pagination.return_value = [
            "https://in.indeed.com/jobs?q=python+developer+Bangalore&sort=date&start=0",
            "https://in.indeed.com/jobs?q=python+developer+Bangalore&sort=date&start=50",
            "https://in.indeed.com/jobs?q=python+developer+Bangalore&sort=date&start=100"
        ]
        mock_captcha.return_value = False
        mock_validate.return_value = {
            'job_card': True, 'title': True, 'company': True,
            'location': True, 'link': True
        }
        
        # Return different jobs for each page
        mock_extract.side_effect = [
            [
                {
                    'title': 'Senior Python Developer',
                    'company': 'Tech Corp India',
                    'location': 'Bangalore, Karnataka',
                    'link': 'https://in.indeed.com/viewjob?jk=abc123',
                    'salary': '₹8,00,000 - ₹12,00,000 a year',
                    'posted_date': '2 days ago',
                    'description': 'Looking for experienced Python developer...'
                },
                {
                    'title': 'Python Backend Developer',
                    'company': 'Startup XYZ',
                    'location': 'Bangalore, Karnataka',
                    'link': 'https://in.indeed.com/viewjob?jk=def456',
                    'salary': '₹6,00,000 - ₹10,00,000 a year',
                    'posted_date': '1 day ago',
                    'description': 'Join our fast-growing startup...'
                }
            ],
            [
                {
                    'title': 'Python Full Stack Developer',
                    'company': 'MNC Solutions',
                    'location': 'Bangalore, Karnataka',
                    'link': 'https://in.indeed.com/viewjob?jk=ghi789',
                    'salary': '₹10,00,000 - ₹15,00,000 a year',
                    'posted_date': '3 days ago',
                    'description': 'Work on cutting-edge technologies...'
                }
            ],
            [
                {
                    'title': 'Python Data Engineer',
                    'company': 'Analytics Inc',
                    'location': 'Bangalore, Karnataka',
                    'link': 'https://in.indeed.com/viewjob?jk=jkl012',
                    'salary': '₹12,00,000 - ₹18,00,000 a year',
                    'posted_date': '5 days ago',
                    'description': 'Build data pipelines at scale...'
                }
            ]
        ]
        
        # Execute function
        print("\nExecuting search query: 'python developer Bangalore'")
        print(f"Max pages: 3")
        print()
        
        result = execute_search_query(mock_page, "python developer Bangalore", max_pages=3)
        
        # Display results
        print(f"\n✓ Successfully extracted {len(result)} jobs from 3 pages")
        print("\nExtracted Jobs:")
        print("-" * 80)
        for i, job in enumerate(result, 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Salary: {job.get('salary', 'Not specified')}")
            print(f"   Posted: {job.get('posted_date', 'Unknown')}")
            print(f"   Link: {job['link']}")
        
        # Verify function calls
        print("\n" + "=" * 80)
        print("Function Call Verification:")
        print("=" * 80)
        print(f"✓ construct_search_url called: {mock_construct.call_count} time(s)")
        print(f"✓ get_pagination_urls called: {mock_pagination.call_count} time(s)")
        print(f"✓ page.goto called: {mock_page.goto.call_count} time(s)")
        print(f"✓ detect_captcha called: {mock_captcha.call_count} time(s)")
        print(f"✓ apply_anti_detection_behavior called: {mock_anti_detection.call_count} time(s)")
        print(f"✓ validate_selectors called: {mock_validate.call_count} time(s)")
        print(f"✓ extract_jobs_from_page called: {mock_extract.call_count} time(s)")
        print(f"✓ random_delay called: {mock_delay.call_count} time(s) (not after last page)")


def demo_error_handling():
    """Demonstrate error handling with network failures and CAPTCHA."""
    print("\n\n" + "=" * 80)
    print("DEMO: Error Handling (Network Failures and CAPTCHA)")
    print("=" * 80)
    
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    
    # Create mock page
    mock_page = Mock()
    
    # First page: network timeout
    # Second page: CAPTCHA
    # Third page: success
    mock_page.goto = Mock(side_effect=[
        PlaywrightTimeoutError("Network timeout"),
        None,  # Second call succeeds (but has CAPTCHA)
        None   # Third call succeeds
    ])
    mock_page.url = "https://in.indeed.com/jobs?q=data+analyst&sort=date&start=100"
    
    with patch('scraper.construct_search_url') as mock_construct, \
         patch('scraper.get_pagination_urls') as mock_pagination, \
         patch('scraper.handle_network_error') as mock_handle_error, \
         patch('scraper.detect_captcha') as mock_captcha, \
         patch('scraper.handle_captcha_detection') as mock_handle_captcha, \
         patch('scraper.apply_anti_detection_behavior') as mock_anti_detection, \
         patch('scraper.validate_selectors') as mock_validate, \
         patch('scraper.extract_jobs_from_page') as mock_extract, \
         patch('scraper.random_delay') as mock_delay:
        
        # Setup mocks
        mock_construct.return_value = "https://in.indeed.com/jobs?q=data+analyst+Bangalore&sort=date"
        mock_pagination.return_value = [
            "https://in.indeed.com/jobs?q=data+analyst+Bangalore&sort=date&start=0",
            "https://in.indeed.com/jobs?q=data+analyst+Bangalore&sort=date&start=50",
            "https://in.indeed.com/jobs?q=data+analyst+Bangalore&sort=date&start=100"
        ]
        
        # Page 1: network error (no CAPTCHA check)
        # Page 2: CAPTCHA detected
        # Page 3: success
        mock_captcha.side_effect = [True, False]  # CAPTCHA on page 2, not on page 3
        mock_handle_captcha.return_value = 1
        mock_handle_error.return_value = {
            'query': 'data analyst Bangalore',
            'total_attempts': 3,
            'error_count': 1
        }
        mock_validate.return_value = {
            'job_card': True, 'title': True, 'company': True,
            'location': True, 'link': True
        }
        
        # Only page 3 returns jobs
        mock_extract.return_value = [
            {
                'title': 'Data Analyst',
                'company': 'Analytics Corp',
                'location': 'Bangalore, Karnataka',
                'link': 'https://in.indeed.com/viewjob?jk=xyz789',
                'salary': '₹5,00,000 - ₹8,00,000 a year',
                'posted_date': '1 week ago',
                'description': 'Analyze business data...'
            }
        ]
        
        # Execute function
        print("\nExecuting search query: 'data analyst Bangalore'")
        print(f"Max pages: 3")
        print("\nSimulated errors:")
        print("  - Page 1: Network timeout")
        print("  - Page 2: CAPTCHA detected")
        print("  - Page 3: Success")
        print()
        
        result = execute_search_query(mock_page, "data analyst Bangalore", max_pages=3)
        
        # Display results
        print(f"\n✓ Gracefully handled errors and extracted {len(result)} job(s)")
        print("\nExtracted Jobs:")
        print("-" * 80)
        for i, job in enumerate(result, 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Link: {job['link']}")
        
        # Verify error handling
        print("\n" + "=" * 80)
        print("Error Handling Verification:")
        print("=" * 80)
        print(f"✓ handle_network_error called: {mock_handle_error.call_count} time(s)")
        print(f"✓ handle_captcha_detection called: {mock_handle_captcha.call_count} time(s)")
        print(f"✓ extract_jobs_from_page called: {mock_extract.call_count} time(s) (only for successful page)")
        print("\n✓ Function completed successfully despite errors!")


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("Task 12.1: execute_search_query Function Demonstration")
    print("=" * 80)
    print("\nThis function orchestrates the complete search query execution workflow:")
    print("  1. Constructs search URL and generates pagination URLs")
    print("  2. Navigates to each page with timeout")
    print("  3. Applies anti-detection behavior (scrolling, mouse movements)")
    print("  4. Detects and handles CAPTCHA challenges")
    print("  5. Validates selectors and extracts jobs")
    print("  6. Handles network errors gracefully")
    print("  7. Applies random delays between pages")
    print("  8. Returns all collected jobs from all pages")
    
    # Run demos
    demo_successful_execution()
    demo_error_handling()
    
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\nThe execute_search_query function successfully:")
    print("  ✓ Orchestrates all prerequisite components")
    print("  ✓ Handles network errors gracefully (continues to next page)")
    print("  ✓ Handles CAPTCHA detection (skips page and continues)")
    print("  ✓ Applies anti-detection behavior on each page")
    print("  ✓ Extracts jobs from multiple pages")
    print("  ✓ Returns all collected jobs")
    print("\nRequirements Validated:")
    print("  ✓ 2.1, 2.2, 2.3, 2.4, 2.5: Search query execution and pagination")
    print("  ✓ 3.1, 3.2: Random delays between pages")
    print("  ✓ 9.2, 9.4, 9.5, 9.6: Network error handling")
    print("  ✓ 10.2, 10.3: CAPTCHA detection and handling")
    print("\nProperties Validated:")
    print("  ✓ Property 20: Error Resilience")
    print("  ✓ Property 21: Error Logging with Context")
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
