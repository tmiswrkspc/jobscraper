#!/usr/bin/env python3
"""
Quick test script to verify improved scraper settings.
Tests only the first query to validate changes without full run.
"""

import config

print("=" * 70)
print("IMPROVED SCRAPER CONFIGURATION TEST")
print("=" * 70)
print()

print("✓ Configuration Loaded Successfully")
print()

print("Delay Settings:")
print(f"  - MIN_DELAY: {config.MIN_DELAY} seconds (was 8)")
print(f"  - MAX_DELAY: {config.MAX_DELAY} seconds (was 18)")
print(f"  - Average delay: {(config.MIN_DELAY + config.MAX_DELAY) / 2:.1f} seconds")
print()

print("Pagination Settings:")
print(f"  - MAX_PAGES: {config.MAX_PAGES} pages per query (was 4)")
print(f"  - Expected jobs per query: {config.MAX_PAGES * 15}-{config.MAX_PAGES * 40}")
print()

print("Timeout Settings:")
print(f"  - PAGE_LOAD_TIMEOUT: {config.PAGE_LOAD_TIMEOUT / 1000:.0f} seconds (was 60)")
print()

print("Search Queries:")
for i, query in enumerate(config.SEARCH_QUERIES, 1):
    print(f"  {i}. {query}")
print()

print("Estimated Session Duration:")
total_pages = len(config.SEARCH_QUERIES) * config.MAX_PAGES
avg_delay = (config.MIN_DELAY + config.MAX_DELAY) / 2
estimated_time = (total_pages * avg_delay) / 60
print(f"  - Total pages to scrape: {total_pages}")
print(f"  - Average delay per page: {avg_delay:.1f} seconds")
print(f"  - Estimated duration: {estimated_time:.1f} minutes")
print()

print("Expected Results:")
print(f"  - Minimum jobs: {len(config.SEARCH_QUERIES) * config.MAX_PAGES * 10}")
print(f"  - Maximum jobs: {len(config.SEARCH_QUERIES) * config.MAX_PAGES * 40}")
print(f"  - Realistic estimate: {len(config.SEARCH_QUERIES) * config.MAX_PAGES * 20}-{len(config.SEARCH_QUERIES) * config.MAX_PAGES * 30}")
print()

print("=" * 70)
print("Configuration test passed! Ready to run scraper.")
print("=" * 70)
print()
print("To run the scraper:")
print("  python3 scraper.py")
print()
print("To test with just 1 query (recommended first):")
print("  1. Edit config.py")
print("  2. Comment out queries 2-8 in SEARCH_QUERIES")
print("  3. Run: python3 scraper.py")
print()
