#!/usr/bin/env python3
"""
Test script for Tavily enrichment integration
"""

from tavily_enricher import TavilyEnricher

def test_tavily():
    """Test Tavily enrichment features"""
    print("="*70)
    print("TAVILY ENRICHMENT TEST")
    print("="*70)
    print()
    
    # Initialize enricher
    enricher = TavilyEnricher()
    
    # Check configuration
    if not enricher.is_enabled():
        print("❌ Tavily not configured")
        print("Set TAVILY_API_KEY in .env file")
        print()
        print("Get your free API key from: https://tavily.com/")
        return
    
    print("✓ Tavily enricher configured")
    print()
    
    # Test 1: Job enrichment
    print("Test 1: Job Enrichment")
    print("-" * 70)
    test_job = {
        'title': 'Senior Python Developer',
        'company': 'Tech Corp',
        'location': 'Bangalore',
        'link': 'https://www.naukri.com/job-listings-senior-python-developer'
    }
    
    enriched = enricher.enrich_job(test_job)
    if enriched.get('enriched'):
        print(f"✓ Job enriched successfully")
        print(f"  Full description: {len(enriched.get('full_description', ''))} characters")
    else:
        print("⚠ Job enrichment skipped or failed")
    print()
    
    # Test 2: Learning resources
    print("Test 2: Learning Resources")
    print("-" * 70)
    resources = enricher.find_learning_resources("Django", max_results=3)
    if resources:
        print(f"✓ Found {len(resources)} learning resources for Django:")
        for i, resource in enumerate(resources, 1):
            print(f"\n{i}. {resource['title']}")
            print(f"   URL: {resource['url']}")
            print(f"   {resource['description'][:100]}...")
    else:
        print("⚠ No learning resources found")
    print()
    
    # Test 3: GitHub projects
    print("Test 3: GitHub Projects")
    print("-" * 70)
    projects = enricher.find_github_projects(["Python", "Django"], max_results=3)
    if projects:
        print(f"✓ Found {len(projects)} GitHub projects:")
        for i, project in enumerate(projects, 1):
            print(f"\n{i}. {project['title']}")
            print(f"   URL: {project['url']}")
    else:
        print("⚠ No GitHub projects found")
    print()
    
    # Test 4: Company research
    print("Test 4: Company Research")
    print("-" * 70)
    company_info = enricher.research_company("Google")
    if company_info:
        print(f"✓ Found company information:")
        print(f"  Company: {company_info['company_name']}")
        print(f"  Summary: {company_info['summary'][:200]}...")
        print(f"  Sources: {len(company_info['sources'])} articles")
    else:
        print("⚠ Company research failed")
    print()
    
    print("="*70)
    print("✓ All tests completed")
    print("="*70)

if __name__ == "__main__":
    test_tavily()
