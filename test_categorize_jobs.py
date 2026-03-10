"""
Test script for categorize_jobs() method.

This script tests the job categorization functionality added in Task 4.1.
"""

from scraper import SerperJobScraper


def test_categorize_jobs():
    """Test the categorize_jobs method with sample jobs."""
    
    scraper = SerperJobScraper()
    
    # Create sample jobs for each category
    sample_jobs = [
        # Backend job
        {
            'title': 'Backend Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore',
            'link': 'https://example.com/1',
            'salary': None,
            'posted_date': None,
            'description': 'Looking for Django and Flask developer to build APIs',
            'source': 'test'
        },
        # Frontend job
        {
            'title': 'Frontend Engineer',
            'company': 'UI Company',
            'location': 'Mumbai',
            'link': 'https://example.com/2',
            'salary': None,
            'posted_date': None,
            'description': 'React and Angular experience required for UI development',
            'source': 'test'
        },
        # Fullstack job
        {
            'title': 'Full Stack Developer',
            'company': 'Startup Inc',
            'location': 'Pune',
            'link': 'https://example.com/3',
            'salary': None,
            'posted_date': None,
            'description': 'Full-stack engineer needed for web application',
            'source': 'test'
        },
        # Data job
        {
            'title': 'Data Scientist',
            'company': 'Analytics Co',
            'location': 'Bangalore',
            'link': 'https://example.com/4',
            'salary': None,
            'posted_date': None,
            'description': 'Machine learning and AI experience needed',
            'source': 'test'
        },
        # DevOps job
        {
            'title': 'DevOps Engineer',
            'company': 'Cloud Systems',
            'location': 'Hyderabad',
            'link': 'https://example.com/5',
            'salary': None,
            'posted_date': None,
            'description': 'Kubernetes and Docker infrastructure management',
            'source': 'test'
        },
        # Mobile job
        {
            'title': 'Mobile Developer',
            'company': 'App Studio',
            'location': 'Delhi',
            'link': 'https://example.com/6',
            'salary': None,
            'posted_date': None,
            'description': 'iOS and Android development with Flutter',
            'source': 'test'
        },
        # Other job (no specific keywords)
        {
            'title': 'Software Engineer',
            'company': 'Generic Tech',
            'location': 'Bangalore',
            'link': 'https://example.com/7',
            'salary': None,
            'posted_date': None,
            'description': 'General software development position',
            'source': 'test'
        },
        # Case insensitive test - BACKEND in uppercase
        {
            'title': 'BACKEND DEVELOPER',
            'company': 'Test Corp',
            'location': 'Bangalore',
            'link': 'https://example.com/8',
            'salary': None,
            'posted_date': None,
            'description': 'BACKEND API DEVELOPMENT',
            'source': 'test'
        }
    ]
    
    # Categorize jobs
    categorized = scraper.categorize_jobs(sample_jobs)
    
    # Verify results
    print("Categorization Results:")
    print("=" * 70)
    
    for category, jobs in categorized.items():
        print(f"\n{category.upper()} ({len(jobs)} jobs):")
        for job in jobs:
            print(f"  - {job['title']} at {job['company']}")
    
    print("\n" + "=" * 70)
    print("Verification:")
    print("=" * 70)
    
    # Check that all categories exist
    expected_categories = ['backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other']
    assert set(categorized.keys()) == set(expected_categories), "Missing categories!"
    print("✓ All 7 categories present")
    
    # Check backend category (should have 2 jobs - including uppercase one)
    assert len(categorized['backend']) == 2, f"Expected 2 backend jobs, got {len(categorized['backend'])}"
    print("✓ Backend category has 2 jobs (case-insensitive working)")
    
    # Check frontend category
    assert len(categorized['frontend']) == 1, f"Expected 1 frontend job, got {len(categorized['frontend'])}"
    print("✓ Frontend category has 1 job")
    
    # Check fullstack category
    assert len(categorized['fullstack']) == 1, f"Expected 1 fullstack job, got {len(categorized['fullstack'])}"
    print("✓ Fullstack category has 1 job")
    
    # Check data category
    assert len(categorized['data']) == 1, f"Expected 1 data job, got {len(categorized['data'])}"
    print("✓ Data category has 1 job")
    
    # Check devops category
    assert len(categorized['devops']) == 1, f"Expected 1 devops job, got {len(categorized['devops'])}"
    print("✓ DevOps category has 1 job")
    
    # Check mobile category
    assert len(categorized['mobile']) == 1, f"Expected 1 mobile job, got {len(categorized['mobile'])}"
    print("✓ Mobile category has 1 job")
    
    # Check other category
    assert len(categorized['other']) == 1, f"Expected 1 other job, got {len(categorized['other'])}"
    print("✓ Other category has 1 job")
    
    # Check total count
    total_categorized = sum(len(jobs) for jobs in categorized.values())
    assert total_categorized == len(sample_jobs), "Some jobs were lost during categorization!"
    print(f"✓ All {len(sample_jobs)} jobs categorized (no jobs lost)")
    
    print("\n" + "=" * 70)
    print("✓ All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_categorize_jobs()
