"""
Comprehensive test for categorize_jobs() method.

Tests all requirements from the design document:
- All 7 categories supported
- Keyword matching for each category
- Case-insensitive matching
- Combined title and description matching
- Fullstack priority (checked first)
- Default to 'other' category
"""

from scraper import SerperJobScraper


def test_fullstack_priority():
    """Test that fullstack is checked first (most specific)."""
    scraper = SerperJobScraper()
    
    # Job with both fullstack and backend keywords
    jobs = [{
        'title': 'Full Stack Developer',
        'company': 'Test',
        'location': 'Bangalore',
        'link': 'https://example.com/1',
        'salary': None,
        'posted_date': None,
        'description': 'Backend API development with Django',
        'source': 'test'
    }]
    
    categorized = scraper.categorize_jobs(jobs)
    
    # Should be in fullstack, not backend
    assert len(categorized['fullstack']) == 1
    assert len(categorized['backend']) == 0
    print("✓ Fullstack priority test passed")


def test_keyword_in_title_only():
    """Test keyword matching in title only."""
    scraper = SerperJobScraper()
    
    jobs = [{
        'title': 'Backend Engineer',
        'company': 'Test',
        'location': 'Bangalore',
        'link': 'https://example.com/1',
        'salary': None,
        'posted_date': None,
        'description': 'General software development',
        'source': 'test'
    }]
    
    categorized = scraper.categorize_jobs(jobs)
    assert len(categorized['backend']) == 1
    print("✓ Keyword in title only test passed")


def test_keyword_in_description_only():
    """Test keyword matching in description only."""
    scraper = SerperJobScraper()
    
    jobs = [{
        'title': 'Software Engineer',
        'company': 'Test',
        'location': 'Bangalore',
        'link': 'https://example.com/1',
        'salary': None,
        'posted_date': None,
        'description': 'Looking for React developer',
        'source': 'test'
    }]
    
    categorized = scraper.categorize_jobs(jobs)
    assert len(categorized['frontend']) == 1
    print("✓ Keyword in description only test passed")


def test_empty_job_list():
    """Test with empty job list."""
    scraper = SerperJobScraper()
    
    categorized = scraper.categorize_jobs([])
    
    # Should return all 7 categories with empty lists
    assert len(categorized) == 7
    assert all(len(jobs) == 0 for jobs in categorized.values())
    print("✓ Empty job list test passed")


def test_missing_fields():
    """Test jobs with missing title or description."""
    scraper = SerperJobScraper()
    
    jobs = [
        # Missing description
        {
            'title': 'Backend Developer',
            'company': 'Test',
            'location': 'Bangalore',
            'link': 'https://example.com/1',
            'salary': None,
            'posted_date': None,
            'source': 'test'
        },
        # Missing title
        {
            'company': 'Test',
            'location': 'Bangalore',
            'link': 'https://example.com/2',
            'salary': None,
            'posted_date': None,
            'description': 'React development',
            'source': 'test'
        }
    ]
    
    categorized = scraper.categorize_jobs(jobs)
    
    # First job should be in backend (title has keyword)
    assert len(categorized['backend']) == 1
    # Second job should be in frontend (description has keyword)
    assert len(categorized['frontend']) == 1
    print("✓ Missing fields test passed")


def test_all_category_keywords():
    """Test that each category's keywords work correctly."""
    scraper = SerperJobScraper()
    
    test_cases = [
        ('backend', 'Backend Developer', 'API development'),
        ('backend', 'Engineer', 'Django and Flask development'),
        ('frontend', 'Frontend Developer', 'React and Angular'),
        ('frontend', 'Developer', 'CSS and UI design'),
        ('fullstack', 'Full Stack Engineer', 'Web development'),
        ('fullstack', 'Developer', 'Full-stack development'),
        ('data', 'Data Scientist', 'Analytics work'),
        ('data', 'Engineer', 'Machine learning and AI'),
        ('devops', 'DevOps Engineer', 'Infrastructure'),
        ('devops', 'Engineer', 'Kubernetes and Docker'),
        ('mobile', 'Mobile Developer', 'App development'),
        ('mobile', 'Developer', 'iOS and Android'),
    ]
    
    for expected_category, title, description in test_cases:
        jobs = [{
            'title': title,
            'company': 'Test',
            'location': 'Bangalore',
            'link': 'https://example.com/1',
            'salary': None,
            'posted_date': None,
            'description': description,
            'source': 'test'
        }]
        
        categorized = scraper.categorize_jobs(jobs)
        assert len(categorized[expected_category]) == 1, \
            f"Failed for {expected_category}: {title} - {description}"
    
    print("✓ All category keywords test passed")


def test_case_variations():
    """Test case-insensitive matching with various case combinations."""
    scraper = SerperJobScraper()
    
    jobs = [
        {'title': 'BACKEND DEVELOPER', 'company': 'T', 'location': 'B', 
         'link': 'http://1', 'salary': None, 'posted_date': None, 
         'description': 'DJANGO', 'source': 'test'},
        {'title': 'frontend developer', 'company': 'T', 'location': 'B',
         'link': 'http://2', 'salary': None, 'posted_date': None,
         'description': 'react', 'source': 'test'},
        {'title': 'FuLl StAcK', 'company': 'T', 'location': 'B',
         'link': 'http://3', 'salary': None, 'posted_date': None,
         'description': 'DeVeLoPeR', 'source': 'test'},
    ]
    
    categorized = scraper.categorize_jobs(jobs)
    
    assert len(categorized['backend']) == 1
    assert len(categorized['frontend']) == 1
    assert len(categorized['fullstack']) == 1
    print("✓ Case variations test passed")


def test_other_category():
    """Test that jobs without specific keywords go to 'other'."""
    scraper = SerperJobScraper()
    
    jobs = [{
        'title': 'Software Engineer',
        'company': 'Test',
        'location': 'Bangalore',
        'link': 'https://example.com/1',
        'salary': None,
        'posted_date': None,
        'description': 'General programming work',
        'source': 'test'
    }]
    
    categorized = scraper.categorize_jobs(jobs)
    assert len(categorized['other']) == 1
    print("✓ Other category test passed")


def test_no_jobs_lost():
    """Test that all jobs are categorized (none lost)."""
    scraper = SerperJobScraper()
    
    # Create 20 random jobs
    jobs = []
    for i in range(20):
        jobs.append({
            'title': f'Job {i}',
            'company': 'Test',
            'location': 'Bangalore',
            'link': f'https://example.com/{i}',
            'salary': None,
            'posted_date': None,
            'description': 'Some description',
            'source': 'test'
        })
    
    categorized = scraper.categorize_jobs(jobs)
    
    total_categorized = sum(len(cat_jobs) for cat_jobs in categorized.values())
    assert total_categorized == len(jobs)
    print("✓ No jobs lost test passed")


def run_all_tests():
    """Run all comprehensive tests."""
    print("Running Comprehensive Categorization Tests")
    print("=" * 70)
    
    test_fullstack_priority()
    test_keyword_in_title_only()
    test_keyword_in_description_only()
    test_empty_job_list()
    test_missing_fields()
    test_all_category_keywords()
    test_case_variations()
    test_other_category()
    test_no_jobs_lost()
    
    print("=" * 70)
    print("✓ All comprehensive tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
