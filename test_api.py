#!/usr/bin/env python3
"""
Quick test script for Serper API integration
"""

from serper_api import SerperAPI
import json

def test_api():
    """Test Serper API with a single query"""
    print("="*70)
    print("SERPER API TEST")
    print("="*70)
    print()
    
    # Initialize API
    api = SerperAPI()
    
    # Check configuration
    if not api.is_configured():
        print("❌ API key not configured")
        print("Set SERPER_API_KEY in .env file")
        return
    
    print("✓ API key configured")
    print()
    
    # Test query
    query = "software engineer"
    location = "Bangalore, India"
    
    print(f"Searching: '{query}' in '{location}'")
    print()
    
    # Search for jobs
    jobs = api.search_jobs(query=query, location=location, num_results=10)
    
    # Display results
    if jobs:
        print(f"✓ Found {len(jobs)} jobs")
        print()
        print("Sample jobs:")
        print("-" * 70)
        
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            if job.get('salary'):
                print(f"   Salary: {job['salary']}")
            print(f"   Link: {job['link']}")
        
        print()
        print("="*70)
        print(f"✓ Test completed successfully - {len(jobs)} jobs found")
    else:
        print("❌ No jobs found")
        print("Check your API key and internet connection")

if __name__ == "__main__":
    test_api()
