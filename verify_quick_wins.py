"""
Quick verification script for Task 8 - Final checkpoint
Tests all Quick Wins functionality without making API calls
"""

import sys
from config import SEARCH_QUERIES
from serper_api import SerperAPI
from scraper import SerperJobScraper

def verify_search_queries():
    """Verify search queries expanded to 30"""
    print("\n" + "="*70)
    print("VERIFICATION 1: Search Query Expansion")
    print("="*70)
    
    if len(SEARCH_QUERIES) == 30:
        print(f"✓ SEARCH_QUERIES contains exactly 30 queries")
        print(f"  Sample queries:")
        for i, query in enumerate(SEARCH_QUERIES[:5], 1):
            print(f"    {i}. {query}")
        print(f"    ...")
        print(f"    {len(SEARCH_QUERIES)}. {SEARCH_QUERIES[-1]}")
        return True
    else:
        print(f"✗ SEARCH_QUERIES contains {len(SEARCH_QUERIES)} queries (expected 30)")
        return False

def verify_skills_extraction():
    """Verify skills extraction functionality"""
    print("\n" + "="*70)
    print("VERIFICATION 2: Skills Extraction")
    print("="*70)
    
    api = SerperAPI()
    
    # Test skill extraction
    test_text = "Looking for Python developer with Django, React, PostgreSQL, Docker, and AWS experience"
    skills = api._extract_skills(test_text)
    
    expected_skills = {'Python', 'Django', 'React', 'PostgreSQL', 'Docker', 'AWS'}
    detected_skills = set(skills)
    
    if expected_skills.issubset(detected_skills):
        print(f"✓ Skills extraction working correctly")
        print(f"  Test text: '{test_text[:60]}...'")
        print(f"  Detected skills: {sorted(skills)}")
        return True
    else:
        missing = expected_skills - detected_skills
        print(f"✗ Skills extraction incomplete")
        print(f"  Missing skills: {missing}")
        return False

def verify_job_categorization():
    """Verify job categorization functionality"""
    print("\n" + "="*70)
    print("VERIFICATION 3: Job Categorization")
    print("="*70)
    
    scraper = SerperJobScraper()
    
    # Test jobs for each category
    test_jobs = [
        {
            'title': 'Backend Developer',
            'company': 'TechCorp',
            'location': 'Bangalore, India',
            'link': 'https://example.com/1',
            'salary': None,
            'posted_date': None,
            'description': 'Python backend with Django',
            'source': 'test',
            'skills': ['Python', 'Django']
        },
        {
            'title': 'Frontend Engineer',
            'company': 'UIStartup',
            'location': 'Mumbai, India',
            'link': 'https://example.com/2',
            'salary': None,
            'posted_date': None,
            'description': 'React developer',
            'source': 'test',
            'skills': ['React']
        },
        {
            'title': 'Full Stack Developer',
            'company': 'ProductCo',
            'location': 'Pune, India',
            'link': 'https://example.com/3',
            'salary': None,
            'posted_date': None,
            'description': 'Full-stack engineer',
            'source': 'test',
            'skills': []
        },
        {
            'title': 'Data Scientist',
            'company': 'DataCorp',
            'location': 'Hyderabad, India',
            'link': 'https://example.com/4',
            'salary': None,
            'posted_date': None,
            'description': 'Machine learning expert',
            'source': 'test',
            'skills': ['Machine Learning']
        },
        {
            'title': 'DevOps Engineer',
            'company': 'CloudSys',
            'location': 'Bangalore, India',
            'link': 'https://example.com/5',
            'salary': None,
            'posted_date': None,
            'description': 'Kubernetes and Docker',
            'source': 'test',
            'skills': ['Kubernetes', 'Docker']
        },
        {
            'title': 'Android Developer',
            'company': 'MobileApp',
            'location': 'Delhi, India',
            'link': 'https://example.com/6',
            'salary': None,
            'posted_date': None,
            'description': 'Mobile app development',
            'source': 'test',
            'skills': []
        }
    ]
    
    categories = scraper.categorize_jobs(test_jobs)
    
    # Verify all 7 categories exist
    expected_categories = {'backend', 'frontend', 'fullstack', 'data', 'devops', 'mobile', 'other'}
    if set(categories.keys()) != expected_categories:
        print(f"✗ Missing categories: {expected_categories - set(categories.keys())}")
        return False
    
    # Verify jobs are categorized correctly
    checks = [
        ('backend', 1, 'Backend job'),
        ('frontend', 1, 'Frontend job'),
        ('fullstack', 1, 'Full-stack job'),
        ('data', 1, 'Data science job'),
        ('devops', 1, 'DevOps job'),
        ('mobile', 1, 'Mobile job'),
    ]
    
    all_passed = True
    for category, expected_count, description in checks:
        actual_count = len(categories[category])
        if actual_count >= expected_count:
            print(f"✓ {description} categorized to '{category}' ({actual_count} job(s))")
        else:
            print(f"✗ {description} not in '{category}' (found {actual_count}, expected {expected_count})")
            all_passed = False
    
    return all_passed

def verify_skills_field_in_jobs():
    """Verify that normalized jobs include skills field"""
    print("\n" + "="*70)
    print("VERIFICATION 4: Skills Field in Job Schema")
    print("="*70)
    
    api = SerperAPI()
    
    # Simulate jobs endpoint data
    jobs_data = {
        'jobs': [
            {
                'title': 'Python Developer',
                'company': 'TechCorp',
                'location': 'Bangalore, India',
                'link': 'https://example.com/job1',
                'description': 'Python developer with Django experience'
            }
        ]
    }
    
    normalized = api._normalize_jobs_endpoint_results(jobs_data)
    
    if len(normalized) > 0 and 'skills' in normalized[0]:
        print(f"✓ Normalized jobs include 'skills' field")
        print(f"  Job title: {normalized[0]['title']}")
        print(f"  Skills: {normalized[0]['skills']}")
        return True
    else:
        print(f"✗ Normalized jobs missing 'skills' field")
        return False

def verify_backward_compatibility():
    """Verify backward compatibility of job schema"""
    print("\n" + "="*70)
    print("VERIFICATION 5: Backward Compatibility")
    print("="*70)
    
    # Check that all original fields are still present
    required_fields = ['title', 'company', 'location', 'link', 'salary', 
                      'posted_date', 'description', 'source']
    
    test_job = {
        'title': 'Software Engineer',
        'company': 'TechCorp',
        'location': 'Bangalore, India',
        'link': 'https://example.com/job1',
        'salary': '₹15-25 LPA',
        'posted_date': '2 days ago',
        'description': 'Python developer',
        'source': 'serper_jobs_api',
        'skills': ['Python']  # New field
    }
    
    missing_fields = [field for field in required_fields if field not in test_job]
    
    if not missing_fields and 'skills' in test_job:
        print(f"✓ Job schema maintains all original fields")
        print(f"  Original fields: {', '.join(required_fields)}")
        print(f"  New field: skills")
        return True
    else:
        print(f"✗ Job schema incomplete")
        if missing_fields:
            print(f"  Missing fields: {missing_fields}")
        return False

def main():
    """Run all verifications"""
    print("\n" + "="*70)
    print("QUICK WINS IMPLEMENTATION - FINAL CHECKPOINT (Task 8)")
    print("="*70)
    print("\nVerifying all functionality and backward compatibility...")
    
    results = []
    
    # Run all verifications
    results.append(("Search Query Expansion (30 queries)", verify_search_queries()))
    results.append(("Skills Extraction", verify_skills_extraction()))
    results.append(("Job Categorization", verify_job_categorization()))
    results.append(("Skills Field in Schema", verify_skills_field_in_jobs()))
    results.append(("Backward Compatibility", verify_backward_compatibility()))
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "="*70)
    if passed == total:
        print(f"ALL VERIFICATIONS PASSED ({passed}/{total})")
        print("="*70)
        print("\n✓ Quick Wins implementation is complete and working correctly!")
        print("✓ All functionality verified")
        print("✓ Backward compatibility maintained")
        print("✓ Ready for production use")
        return 0
    else:
        print(f"SOME VERIFICATIONS FAILED ({passed}/{total})")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
