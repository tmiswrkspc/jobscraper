"""
Demonstration of Task 10.3: save_intermediate_results() function

This script demonstrates how the save_intermediate_results() function
would be used in the context of the Indeed Job Scraper to preserve
progress after each search query completes.

Usage:
    python3 demo_task_10_3.py
"""

import os
import json
from scraper import save_intermediate_results
from config import OUTPUT_DIR, INTERMEDIATE_RESULTS_FILENAME


def demo_session_with_intermediate_saves():
    """
    Demonstrates saving intermediate results after each query completion.
    
    This simulates the scraper workflow where:
    1. Query 1 completes -> save intermediate results (2 jobs)
    2. Query 2 completes -> save intermediate results (5 jobs total)
    3. Query 3 completes -> save intermediate results (8 jobs total)
    """
    print("=" * 70)
    print("Demo: Saving Intermediate Results During Scraping Session")
    print("=" * 70)
    print()
    
    # Prepare output path
    output_path = os.path.join(OUTPUT_DIR, INTERMEDIATE_RESULTS_FILENAME)
    
    # Simulate Query 1: "software engineer Bangalore"
    print("Query 1: 'software engineer Bangalore' completed")
    accumulated_jobs = [
        {
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=abc123',
            'salary': '₹8,00,000 - ₹12,00,000 a year',
            'posted_date': '2 days ago',
            'description': 'We are looking for a skilled software engineer...'
        },
        {
            'title': 'Senior Software Engineer',
            'company': 'Innovation Labs',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=def456',
            'salary': '₹15,00,000 - ₹20,00,000 a year',
            'posted_date': '1 day ago',
            'description': 'Senior engineer needed for cloud infrastructure'
        }
    ]
    save_intermediate_results(accumulated_jobs, output_path)
    print(f"  → Saved {len(accumulated_jobs)} jobs to intermediate results")
    print()
    
    # Simulate Query 2: "python developer Bangalore"
    print("Query 2: 'python developer Bangalore' completed")
    accumulated_jobs.extend([
        {
            'title': 'Python Developer',
            'company': 'Software Solutions',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=ghi789',
            'salary': '₹6,00,000 - ₹10,00,000 a year',
            'posted_date': '3 days ago',
            'description': 'Python developer for backend development'
        },
        {
            'title': 'Python Backend Engineer',
            'company': 'Data Systems Inc',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=jkl012',
            'salary': '₹12,00,000 - ₹16,00,000 a year',
            'posted_date': '1 week ago',
            'description': 'Backend engineer with Python and Django experience'
        },
        {
            'title': 'Python Full Stack Developer',
            'company': 'Web Tech',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=mno345',
            'salary': None,
            'posted_date': '5 days ago',
            'description': 'Full stack developer with Python and React'
        }
    ])
    save_intermediate_results(accumulated_jobs, output_path)
    print(f"  → Saved {len(accumulated_jobs)} jobs to intermediate results")
    print()
    
    # Simulate Query 3: "data analyst Bangalore"
    print("Query 3: 'data analyst Bangalore' completed")
    accumulated_jobs.extend([
        {
            'title': 'Data Analyst',
            'company': 'Analytics Corp',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=pqr678',
            'salary': '₹5,00,000 - ₹8,00,000 a year',
            'posted_date': '2 days ago',
            'description': 'Data analyst with SQL and Python skills'
        },
        {
            'title': 'Senior Data Analyst',
            'company': 'Business Intelligence Ltd',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=stu901',
            'salary': '₹10,00,000 - ₹14,00,000 a year',
            'posted_date': '4 days ago',
            'description': 'Senior analyst for business intelligence projects'
        },
        {
            'title': 'Data Analyst - Marketing',
            'company': 'Marketing Solutions',
            'location': 'Bangalore, Karnataka',
            'link': 'https://in.indeed.com/viewjob?jk=vwx234',
            'salary': '₹7,00,000 - ₹11,00,000 a year',
            'posted_date': '1 week ago',
            'description': 'Marketing data analyst with analytics experience'
        }
    ])
    save_intermediate_results(accumulated_jobs, output_path)
    print(f"  → Saved {len(accumulated_jobs)} jobs to intermediate results")
    print()
    
    # Show final intermediate results file
    print("=" * 70)
    print("Final Intermediate Results File")
    print("=" * 70)
    print(f"Location: {output_path}")
    print(f"Total jobs saved: {len(accumulated_jobs)}")
    print()
    
    # Verify file contents
    with open(output_path, 'r', encoding='utf-8') as f:
        loaded_jobs = json.load(f)
    
    print(f"Verification: Loaded {len(loaded_jobs)} jobs from file")
    print()
    
    # Show sample of saved jobs
    print("Sample of saved jobs:")
    for i, job in enumerate(loaded_jobs[:3], 1):
        print(f"\n  Job {i}:")
        print(f"    Title: {job['title']}")
        print(f"    Company: {job['company']}")
        print(f"    Location: {job['location']}")
        print(f"    Salary: {job.get('salary', 'Not specified')}")
        print(f"    Link: {job['link']}")
    
    print()
    print("=" * 70)
    print("✅ Demo completed successfully!")
    print("=" * 70)
    print()
    print("Key Benefits:")
    print("  • Progress is saved after each query completes")
    print("  • If scraper is interrupted, partial results are preserved")
    print("  • Session can be resumed from the last completed query")
    print("  • All job data including UTF-8 characters (₹) is preserved")
    print()


def demo_interruption_recovery():
    """
    Demonstrates how intermediate results enable recovery from interruption.
    """
    print("=" * 70)
    print("Demo: Recovery from Interruption Using Intermediate Results")
    print("=" * 70)
    print()
    
    output_path = os.path.join(OUTPUT_DIR, INTERMEDIATE_RESULTS_FILENAME)
    
    # Check if intermediate results exist from previous demo
    if os.path.exists(output_path):
        print("✓ Found intermediate results file from previous session")
        print(f"  Location: {output_path}")
        print()
        
        # Load intermediate results
        with open(output_path, 'r', encoding='utf-8') as f:
            recovered_jobs = json.load(f)
        
        print(f"✓ Recovered {len(recovered_jobs)} jobs from interrupted session")
        print()
        
        print("Recovered job titles:")
        for i, job in enumerate(recovered_jobs, 1):
            print(f"  {i}. {job['title']} at {job['company']}")
        
        print()
        print("=" * 70)
        print("✅ Recovery demo completed!")
        print("=" * 70)
        print()
        print("The scraper can now:")
        print("  • Continue from where it left off")
        print("  • Skip already-completed queries")
        print("  • Merge new results with recovered results")
        print()
    else:
        print("⚠ No intermediate results file found")
        print("  Run demo_session_with_intermediate_saves() first")
        print()


if __name__ == '__main__':
    # Run demos
    demo_session_with_intermediate_saves()
    print("\n" + "=" * 70 + "\n")
    demo_interruption_recovery()
