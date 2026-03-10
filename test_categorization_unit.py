"""
Unit tests for job categorization - Task 4.6

These tests complement the property-based tests and verify specific examples
and edge cases for the categorize_jobs() method.

Test Coverage:
- Each category with representative job examples
- 'other' category for jobs without keywords
- Case-insensitive categorization
- Keyword in title vs description vs both
- Fullstack priority (should match before backend/frontend)
- categorize_jobs returns all 7 categories
- Empty job list edge case
- Jobs with missing title or description fields
"""

from scraper import SerperJobScraper


def test_categorization_each_category():
    """Test each category with representative job examples."""
    scraper = SerperJobScraper()
    
    print(f"\n{'='*70}")
    print("Unit Test: Each Category with Representative Examples")
    print(f"{'='*70}")
    
    # Test cases: (job_data, expected_category, description)
    test_cases = [
        # Backend category
        ({
            'title': 'Backend Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': 'Looking for backend engineer with API development experience',
            'skills': []
        }, 'backend', 'Backend in title'),
        
        ({
            'title': 'Python Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/2',
            'description': 'Django and Flask experience required for server-side development',
            'skills': []
        }, 'backend', 'Django/Flask/server in description'),
        
        # Frontend category
        ({
            'title': 'Frontend Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/3',
            'description': 'Build user interfaces with modern frameworks',
            'skills': []
        }, 'frontend', 'Frontend in title'),
        
        ({
            'title': 'UI Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/4',
            'description': 'React and Angular experience with CSS skills',
            'skills': []
        }, 'frontend', 'React/Angular/CSS/UI in description'),
        
        # Fullstack category
        ({
            'title': 'Full Stack Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/5',
            'description': 'Work on both frontend and backend',
            'skills': []
        }, 'fullstack', 'Full stack in title'),
        
        ({
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/6',
            'description': 'Looking for fullstack engineer with React and Node.js',
            'skills': []
        }, 'fullstack', 'Fullstack in description'),
        
        # Data category
        ({
            'title': 'Data Scientist',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/7',
            'description': 'Analyze data and create ML models',
            'skills': []
        }, 'data', 'Data scientist in title'),
        
        ({
            'title': 'Data Analyst',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/8',
            'description': 'Machine learning and AI experience needed',
            'skills': []
        }, 'data', 'Data analyst/ML/AI in title and description'),
        
        # DevOps category
        ({
            'title': 'DevOps Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/9',
            'description': 'Manage cloud infrastructure',
            'skills': []
        }, 'devops', 'DevOps in title'),
        
        ({
            'title': 'SRE',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/10',
            'description': 'Kubernetes and Docker experience with infrastructure management',
            'skills': []
        }, 'devops', 'SRE/Kubernetes/Docker/infrastructure in description'),
        
        # Mobile category
        ({
            'title': 'Android Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/11',
            'description': 'Create Android apps',
            'skills': []
        }, 'mobile', 'Android in title'),
        
        ({
            'title': 'iOS Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/12',
            'description': 'iOS and Flutter development',
            'skills': []
        }, 'mobile', 'iOS/Flutter in title and description'),
    ]
    
    passed = 0
    failed = 0
    
    for job, expected_category, description in test_cases:
        result = scraper.categorize_jobs([job])
        
        # Find which category the job was assigned to
        actual_category = None
        for category, jobs in result.items():
            if job in jobs:
                actual_category = category
                break
        
        if actual_category == expected_category:
            passed += 1
            print(f"✓ {description}: '{job['title']}' → {actual_category}")
        else:
            failed += 1
            print(f"✗ {description}: '{job['title']}' → Expected {expected_category}, got {actual_category}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} test cases failed"
    print("✓ All category representative tests passed\n")


def test_categorization_other_category():
    """Test 'other' category for jobs without keywords."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: 'Other' Category for Jobs Without Keywords")
    print(f"{'='*70}")
    
    # Jobs without any category-specific keywords
    test_jobs = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': 'Looking for talented engineer with strong problem solving skills',
            'skills': []
        },
        {
            'title': 'Technical Lead',
            'company': 'Innovate Labs',
            'location': 'Mumbai, India',
            'link': 'https://example.com/job/2',
            'description': 'Lead team of developers and manage projects',
            'skills': []
        },
        {
            'title': 'Developer',
            'company': 'Code Factory',
            'location': 'Pune, India',
            'link': 'https://example.com/job/3',
            'description': 'Work on exciting projects with great team',
            'skills': []
        },
    ]
    
    result = scraper.categorize_jobs(test_jobs)
    
    # All jobs should be in 'other' category
    if len(result['other']) == len(test_jobs):
        print(f"✓ All {len(test_jobs)} jobs correctly assigned to 'other' category")
        
        # Verify no jobs in specific categories
        specific_categories = ['backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile']
        all_empty = all(len(result[cat]) == 0 for cat in specific_categories)
        
        if all_empty:
            print(f"✓ All specific categories are empty")
            print("✓ 'Other' category test passed\n")
        else:
            non_empty = [cat for cat in specific_categories if len(result[cat]) > 0]
            print(f"✗ Unexpected jobs in categories: {non_empty}")
            assert False, f"Jobs found in specific categories when they should be in 'other'"
    else:
        print(f"✗ Expected {len(test_jobs)} jobs in 'other', got {len(result['other'])}")
        assert False, f"Not all jobs assigned to 'other' category"


def test_categorization_case_insensitive():
    """Test case-insensitive categorization."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: Case-Insensitive Categorization")
    print(f"{'='*70}")
    
    # Test cases with different case variations
    test_cases = [
        # Backend - different cases
        ('Backend Developer', 'backend', 'Backend (title case)'),
        ('BACKEND ENGINEER', 'backend', 'BACKEND (uppercase)'),
        ('backend developer', 'backend', 'backend (lowercase)'),
        
        # Frontend - different cases
        ('Frontend Developer', 'frontend', 'Frontend (title case)'),
        ('REACT DEVELOPER', 'frontend', 'REACT (uppercase)'),
        ('angular engineer', 'frontend', 'angular (lowercase)'),
        
        # Fullstack - different cases
        ('Full Stack Developer', 'fullstack', 'Full Stack (title case)'),
        ('FULLSTACK ENGINEER', 'fullstack', 'FULLSTACK (uppercase)'),
        ('full-stack developer', 'fullstack', 'full-stack (lowercase)'),
    ]
    
    passed = 0
    failed = 0
    
    for title, expected_category, description in test_cases:
        job = {
            'title': title,
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': 'Job description',
            'skills': []
        }
        
        result = scraper.categorize_jobs([job])
        
        # Find which category the job was assigned to
        actual_category = None
        for category, jobs in result.items():
            if job in jobs:
                actual_category = category
                break
        
        if actual_category == expected_category:
            passed += 1
            print(f"✓ {description}: '{title}' → {actual_category}")
        else:
            failed += 1
            print(f"✗ {description}: '{title}' → Expected {expected_category}, got {actual_category}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} test cases failed"
    print("✓ All case-insensitive categorization tests passed\n")


def test_categorization_keyword_in_title_vs_description():
    """Test keyword in title vs description vs both."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: Keyword in Title vs Description vs Both")
    print(f"{'='*70}")
    
    # Test cases: (title, description, expected_category, description_text)
    test_cases = [
        # Keyword in title only
        (
            'Backend Developer',
            'Looking for talented engineer',
            'backend',
            'Backend keyword in title only'
        ),
        (
            'React Developer',
            'Build modern applications',
            'frontend',
            'React keyword in title only'
        ),
        
        # Keyword in description only
        (
            'Software Engineer',
            'Looking for backend developer with API experience',
            'backend',
            'Backend keyword in description only'
        ),
        (
            'Developer',
            'Need frontend engineer with React and CSS skills',
            'frontend',
            'Frontend keyword in description only'
        ),
        
        # Keyword in both title and description
        (
            'Backend Engineer',
            'Backend development with Django and Flask',
            'backend',
            'Backend keyword in both title and description'
        ),
        (
            'Frontend Developer',
            'Frontend engineer with React experience',
            'frontend',
            'Frontend keyword in both title and description'
        ),
    ]
    
    passed = 0
    failed = 0
    
    for title, description, expected_category, test_description in test_cases:
        job = {
            'title': title,
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': description,
            'skills': []
        }
        
        result = scraper.categorize_jobs([job])
        
        # Find which category the job was assigned to
        actual_category = None
        for category, jobs in result.items():
            if job in jobs:
                actual_category = category
                break
        
        if actual_category == expected_category:
            passed += 1
            print(f"✓ {test_description} → {actual_category}")
        else:
            failed += 1
            print(f"✗ {test_description} → Expected {expected_category}, got {actual_category}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} test cases failed"
    print("✓ All keyword placement tests passed\n")


def test_categorization_fullstack_priority():
    """Test fullstack priority (should match before backend/frontend)."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: Fullstack Priority Over Backend/Frontend")
    print(f"{'='*70}")
    
    # Jobs that contain both fullstack keywords AND backend/frontend keywords
    # Should be categorized as fullstack (checked first)
    test_cases = [
        {
            'title': 'Full Stack Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': 'Backend and frontend development with React and Django',
            'skills': []
        },
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/2',
            'description': 'Fullstack engineer working on React frontend and API backend',
            'skills': []
        },
        {
            'title': 'Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/3',
            'description': 'Full-stack development with UI and server experience',
            'skills': []
        },
    ]
    
    passed = 0
    failed = 0
    
    for job in test_cases:
        result = scraper.categorize_jobs([job])
        
        # Find which category the job was assigned to
        actual_category = None
        for category, jobs in result.items():
            if job in jobs:
                actual_category = category
                break
        
        if actual_category == 'fullstack':
            passed += 1
            print(f"✓ '{job['title']}' → fullstack (priority respected)")
        else:
            failed += 1
            print(f"✗ '{job['title']}' → Expected fullstack, got {actual_category}")
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} test cases failed"
    print("✓ All fullstack priority tests passed\n")


def test_categorization_returns_all_categories():
    """Test that categorize_jobs returns all 7 categories."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: Returns All 7 Categories")
    print(f"{'='*70}")
    
    # Test with empty list
    result_empty = scraper.categorize_jobs([])
    
    expected_categories = {'backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other'}
    actual_categories = set(result_empty.keys())
    
    if actual_categories == expected_categories:
        print(f"✓ Empty job list: All 7 categories present")
    else:
        missing = expected_categories - actual_categories
        extra = actual_categories - expected_categories
        print(f"✗ Empty job list: Missing {missing}, Extra {extra}")
        assert False, "Not all categories returned for empty list"
    
    # Test with non-empty list
    test_jobs = [
        {
            'title': 'Backend Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': 'Backend development',
            'skills': []
        },
    ]
    
    result_non_empty = scraper.categorize_jobs(test_jobs)
    actual_categories_non_empty = set(result_non_empty.keys())
    
    if actual_categories_non_empty == expected_categories:
        print(f"✓ Non-empty job list: All 7 categories present")
        print("✓ All categories returned test passed\n")
    else:
        missing = expected_categories - actual_categories_non_empty
        extra = actual_categories_non_empty - expected_categories
        print(f"✗ Non-empty job list: Missing {missing}, Extra {extra}")
        assert False, "Not all categories returned for non-empty list"


def test_categorization_empty_job_list():
    """Test empty job list edge case."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: Empty Job List Edge Case")
    print(f"{'='*70}")
    
    result = scraper.categorize_jobs([])
    
    # Should return all 7 categories with empty lists
    expected_categories = ['backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other']
    
    passed = True
    for category in expected_categories:
        if category not in result:
            print(f"✗ Missing category: {category}")
            passed = False
        elif len(result[category]) != 0:
            print(f"✗ Category {category} should be empty, has {len(result[category])} jobs")
            passed = False
    
    if passed:
        print(f"✓ Empty job list returns all 7 categories with empty lists")
        print("✓ Empty job list test passed\n")
    else:
        assert False, "Empty job list test failed"


def test_categorization_missing_fields():
    """Test jobs with missing title or description fields."""
    scraper = SerperJobScraper()
    
    print(f"{'='*70}")
    print("Unit Test: Jobs with Missing Title or Description Fields")
    print(f"{'='*70}")
    
    test_cases = [
        # Missing title
        {
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/1',
            'description': 'Backend developer with Django experience',
            'skills': []
        },
        # Missing description
        {
            'title': 'Frontend Developer',
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/2',
            'skills': []
        },
        # Missing both title and description
        {
            'company': 'Tech Corp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/job/3',
            'skills': []
        },
    ]
    
    passed = 0
    failed = 0
    
    for i, job in enumerate(test_cases, 1):
        try:
            result = scraper.categorize_jobs([job])
            
            # Job should be categorized (likely to 'other' if no keywords found)
            job_found = False
            for category, jobs in result.items():
                if job in jobs:
                    job_found = True
                    print(f"✓ Job {i} (missing fields) → {category}")
                    passed += 1
                    break
            
            if not job_found:
                print(f"✗ Job {i} not found in any category")
                failed += 1
        except Exception as e:
            print(f"✗ Job {i} raised exception: {e}")
            failed += 1
    
    print(f"\nPassed: {passed}/{len(test_cases)}")
    assert failed == 0, f"{failed} test cases failed"
    print("✓ All missing fields tests passed\n")


if __name__ == '__main__':
    print("Running Job Categorization Unit Tests (Task 4.6)")
    print("=" * 70)
    print()
    
    try:
        test_categorization_each_category()
        test_categorization_other_category()
        test_categorization_case_insensitive()
        test_categorization_keyword_in_title_vs_description()
        test_categorization_fullstack_priority()
        test_categorization_returns_all_categories()
        test_categorization_empty_job_list()
        test_categorization_missing_fields()
        
        print("=" * 70)
        print("ALL CATEGORIZATION UNIT TESTS PASSED ✓")
        print("=" * 70)
    except AssertionError as e:
        print(f"\n{'='*70}")
        print(f"TEST FAILED: {e}")
        print(f"{'='*70}")
        exit(1)
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"ERROR: {e}")
        print(f"{'='*70}")
        import traceback
        traceback.print_exc()
        exit(1)
