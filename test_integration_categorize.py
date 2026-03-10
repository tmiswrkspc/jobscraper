"""
Integration test for categorize_jobs() with SerperJobScraper.

This test verifies that the categorize_jobs method integrates correctly
with the SerperJobScraper class and can be called as part of the workflow.
"""

from scraper import SerperJobScraper


def test_integration():
    """Test categorize_jobs integration with SerperJobScraper."""
    
    # Initialize scraper
    scraper = SerperJobScraper(location="Bangalore, India")
    
    # Create sample jobs (simulating scraped data)
    scraper.all_jobs = [
        {
            'title': 'Senior Backend Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job1',
            'salary': '₹15-25 LPA',
            'posted_date': '2 days ago',
            'description': 'Looking for Python developer with Django and Flask experience. Build REST APIs.',
            'source': 'serper_jobs_api'
        },
        {
            'title': 'Frontend Engineer',
            'company': 'UI Startup',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job2',
            'salary': '₹12-20 LPA',
            'posted_date': '1 day ago',
            'description': 'React and Angular developer needed for modern web applications.',
            'source': 'serper_jobs_api'
        },
        {
            'title': 'Full Stack Developer',
            'company': 'Product Company',
            'location': 'Pune, India',
            'link': 'https://example.com/job3',
            'salary': '₹18-30 LPA',
            'posted_date': '3 days ago',
            'description': 'Full-stack engineer with experience in both frontend and backend.',
            'source': 'serper_jobs_api'
        },
        {
            'title': 'Data Scientist',
            'company': 'Analytics Inc',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job4',
            'salary': '₹20-35 LPA',
            'posted_date': '1 week ago',
            'description': 'Machine learning engineer with Python, TensorFlow, and AI experience.',
            'source': 'serper_jobs_api'
        },
        {
            'title': 'DevOps Engineer',
            'company': 'Cloud Systems',
            'location': 'Hyderabad, India',
            'link': 'https://example.com/job5',
            'salary': '₹15-28 LPA',
            'posted_date': '4 days ago',
            'description': 'SRE role managing Kubernetes and Docker infrastructure on AWS.',
            'source': 'serper_jobs_api'
        },
        {
            'title': 'Mobile App Developer',
            'company': 'App Studio',
            'location': 'Delhi, India',
            'link': 'https://example.com/job6',
            'salary': '₹10-18 LPA',
            'posted_date': '5 days ago',
            'description': 'iOS and Android development using Flutter.',
            'source': 'serper_jobs_api'
        },
        {
            'title': 'Software Engineer',
            'company': 'Generic Tech',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job7',
            'salary': '₹8-15 LPA',
            'posted_date': '1 week ago',
            'description': 'General software development position for fresh graduates.',
            'source': 'serper_jobs_api'
        }
    ]
    
    print("Integration Test: Categorizing Jobs")
    print("=" * 70)
    print(f"Total jobs to categorize: {len(scraper.all_jobs)}")
    print()
    
    # Call categorize_jobs method
    categorized = scraper.categorize_jobs(scraper.all_jobs)
    
    # Display results
    print("Categorization Results:")
    print("-" * 70)
    for category, jobs in categorized.items():
        if jobs:
            print(f"\n{category.upper()} ({len(jobs)} jobs):")
            for job in jobs:
                print(f"  • {job['title']} at {job['company']}")
                print(f"    Location: {job['location']}")
                print(f"    Salary: {job['salary']}")
    
    print("\n" + "=" * 70)
    print("Verification:")
    print("-" * 70)
    
    # Verify all categories exist
    assert set(categorized.keys()) == {'backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other'}
    print("✓ All 7 categories present")
    
    # Verify no jobs lost
    total = sum(len(jobs) for jobs in categorized.values())
    assert total == len(scraper.all_jobs)
    print(f"✓ All {len(scraper.all_jobs)} jobs categorized (no jobs lost)")
    
    # Verify expected categorization
    assert len(categorized['backend']) == 1
    assert len(categorized['frontend']) == 1
    assert len(categorized['fullstack']) == 1
    assert len(categorized['data']) == 1
    assert len(categorized['devops']) == 1
    assert len(categorized['mobile']) == 1
    assert len(categorized['other']) == 1
    print("✓ Jobs distributed correctly across categories")
    
    # Verify method can be called multiple times
    categorized2 = scraper.categorize_jobs(scraper.all_jobs)
    assert categorized == categorized2
    print("✓ Method is idempotent (same results on repeated calls)")
    
    print("\n" + "=" * 70)
    print("✓ Integration test passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_integration()
