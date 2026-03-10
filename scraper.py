"""
Multi-Site Job Scraper - Serper API Version

This is a simplified scraper that uses Serper API instead of browser automation.
Benefits:
- No CAPTCHAs
- No proxy management
- Fast execution (seconds vs minutes)
- Clean, structured data
- No browser overhead

All infrastructure is FREE - uses Serper API free tier (2,500 searches/month)
"""

import logging
import json
import csv
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from serper_api import SerperAPI
from deduplicator import deduplicate_jobs
from tavily_enricher import TavilyEnricher
from tavily_enricher import TavilyEnricher
from config import (
    SEARCH_QUERIES, OUTPUT_DIR, ENABLE_ENRICHMENT, 
    MAX_ENRICHMENT_JOBS, RESULTS_PER_QUERY, DEFAULT_LOCATION
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('Scraper')


class SerperJobScraper:
    """
    Job scraper using Serper API for fast, CAPTCHA-free data collection.
    """
    
    def __init__(self, location: str = DEFAULT_LOCATION):
        """
        Initialize scraper.
        
        Args:
            location: Default location for job searches
        """
        self.api = SerperAPI()
        self.enricher = TavilyEnricher()
        self.location = location
        self.all_jobs = []
        
        # Ensure output directory exists
        Path(OUTPUT_DIR).mkdir(exist_ok=True)
    
    def scrape_all_queries(
        self,
        queries: List[str] = None,
        results_per_query: int = 20
    ) -> List[Dict]:
        """
        Scrape jobs for all queries.
        
        Args:
            queries: List of search queries (uses config default if None)
            results_per_query: Number of results per query
            
        Returns:
            List of all collected jobs
        """
        if queries is None:
            queries = SEARCH_QUERIES
        
        logger.info("="*70)
        logger.info("MULTI-SITE JOB SCRAPER - SERPER API")
        logger.info("="*70)
        logger.info(f"Location: {self.location}")
        logger.info(f"Queries: {len(queries)}")
        logger.info(f"Results per query: {results_per_query}")
        logger.info("="*70)
        logger.info("")
        
        # Check API configuration
        if not self.api.is_configured():
            logger.error("Serper API key not configured!")
            logger.error("Set SERPER_API_KEY in .env file")
            return []
        
        # Scrape each query
        for i, query in enumerate(queries, 1):
            logger.info(f"\nQuery {i}/{len(queries)}: '{query}'")
            logger.info("-"*70)
            
            jobs = self.api.search_jobs(
                query=query,
                location=self.location,
                num_results=results_per_query
            )
            
            logger.info(f"Collected {len(jobs)} jobs")
            
            # Add to collection
            self.all_jobs.extend(jobs)
        
        # Deduplicate
        logger.info("\n" + "="*70)
        logger.info("DEDUPLICATION")
        logger.info("="*70)
        
        initial_count = len(self.all_jobs)
        self.all_jobs, dedup_stats = deduplicate_jobs(self.all_jobs)
        final_count = len(self.all_jobs)
        
        logger.info(f"Initial jobs: {initial_count}")
        logger.info(f"URL duplicates removed: {dedup_stats['url_duplicates']}")
        logger.info(f"Fuzzy duplicates removed: {dedup_stats['fuzzy_duplicates']}")
        logger.info(f"Unique jobs: {final_count}")
        
        # Optional: Enrich jobs with Tavily
        if ENABLE_ENRICHMENT and self.enricher.is_enabled():
            logger.info("\n" + "="*70)
            logger.info("ENRICHMENT (Tavily)")
            logger.info("="*70)
            self.all_jobs = self.enricher.enrich_jobs_batch(
                self.all_jobs,
                max_jobs=MAX_ENRICHMENT_JOBS
            )
        
        return self.all_jobs
    
    def export_results(self, jobs: List[Dict] = None) -> tuple:
            """
            Export results to JSON and CSV.

            Args:
                jobs: List of jobs to export (uses self.all_jobs if None)

            Returns:
                Tuple of (json_path, csv_path)
            """
            if jobs is None:
                jobs = self.all_jobs

            if not jobs:
                logger.warning("No jobs to export")
                return None, None

            # Generate timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Export to JSON
            json_filename = f"serper_jobs_{timestamp}.json"
            json_path = Path(OUTPUT_DIR) / json_filename

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)

            logger.info(f"✓ JSON exported: {json_path}")

            # Export to CSV
            csv_filename = f"serper_jobs_{timestamp}.csv"
            csv_path = Path(OUTPUT_DIR) / csv_filename

            if jobs:
                fieldnames = ['title', 'company', 'location', 'link', 'salary', 'posted_date', 'description', 'source', 'skills']

                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                    writer.writeheader()
                    writer.writerows(jobs)

                logger.info(f"✓ CSV exported: {csv_path}")

            # Export category-specific JSON files
            categories = self.categorize_jobs(jobs)

            for category_name, category_jobs in categories.items():
                if not category_jobs:
                    continue

                category_filename = f"jobs_{category_name}_{timestamp}.json"
                category_path = Path(OUTPUT_DIR) / category_filename

                with open(category_path, 'w', encoding='utf-8') as f:
                    json.dump(category_jobs, f, indent=2, ensure_ascii=False)

                logger.info(f"✓ {category_name.capitalize()} jobs exported: {category_path} ({len(category_jobs)} jobs)")

            return str(json_path), str(csv_path)
    
    def print_summary(self, jobs: List[Dict] = None):
        """
        Print summary statistics.
        
        Args:
            jobs: List of jobs (uses self.all_jobs if None)
        """
        if jobs is None:
            jobs = self.all_jobs
        
        logger.info("\n" + "="*70)
        logger.info("SUMMARY")
        logger.info("="*70)
        
        if not jobs:
            logger.info("No jobs collected")
            return
        
        # Count by source
        sources = {}
        for job in jobs:
            source = job.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info(f"Total unique jobs: {len(jobs)}")
        logger.info(f"Sources:")
        for source, count in sorted(sources.items()):
            logger.info(f"  - {source}: {count}")
        
        # Count jobs with salary info
        with_salary = sum(1 for job in jobs if job.get('salary'))
        logger.info(f"Jobs with salary info: {with_salary}")
        
        # New stats: skills and enrichment
        unknown_count = sum(1 for j in jobs if j.get('company', '').strip().lower() in ['unknown', '', 'none'])
        known_count = len(jobs) - unknown_count
        logger.info(f"Company identified: {known_count} ({known_count/len(jobs)*100:.1f}%)")
        logger.info(f"Company = Unknown: {unknown_count} ({unknown_count/len(jobs)*100:.1f}%)")

        enriched_jobs = [j for j in jobs if j.get('enriched')]
        snippet_jobs = [j for j in jobs if not j.get('enriched')]
        
        enriched_count = len(enriched_jobs)
        logger.info(f"Jobs enriched by Tavily: {enriched_count}")
        
        enriched_with_skills = sum(1 for j in enriched_jobs if j.get('skills'))
        snippet_with_skills = sum(1 for j in snippet_jobs if j.get('skills'))
        
        if enriched_jobs:
            logger.info(f"Tavily-enriched skill detection: {enriched_with_skills}/{len(enriched_jobs)} ({enriched_with_skills/len(enriched_jobs)*100:.1f}%)")
        if snippet_jobs:
            logger.info(f"Snippet-only skill detection:    {snippet_with_skills}/{len(snippet_jobs)} ({snippet_with_skills/len(snippet_jobs)*100:.1f}%)")
        
        # New stats: Category breakdown
        logger.info(f"\nCategory breakdown:")
        categorized = self.categorize_jobs(jobs)
        for cat, cat_jobs in categorized.items():
            if cat_jobs:
                logger.info(f"  - {cat}: {len(cat_jobs)}")
        
        # Show sample jobs
        logger.info("\nSample jobs (first 5):")
        for i, job in enumerate(jobs[:5], 1):
            logger.info(f"\n{i}. {job['title']}")
            logger.info(f"   Company: {job['company']}")
            logger.info(f"   Location: {job['location']}")
            logger.info(f"   Link: {job['link'][:60]}...")
        
        logger.info("\n" + "="*70)

    def categorize_jobs(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize jobs by role type based on title and description keywords.

        Categories:
        - backend: Backend development roles
        - frontend: Frontend/UI development roles
        - fullstack: Full-stack development roles
        - data: Data science, ML, analytics roles
        - devops: DevOps, SRE, infrastructure roles
        - mobile: Mobile app development roles
        - other: Jobs not matching specific categories

        Args:
            jobs: List of job dictionaries

        Returns:
            Dictionary mapping category names to lists of jobs
        """
        CATEGORY_KEYWORDS = {
            'backend': ['backend', 'back-end', 'django', 'flask', 'spring', 'api', 'server'],
            'frontend': ['frontend', 'front-end', 'react', 'angular', 'vue', 'css', 'ui'],
            'fullstack': ['full stack', 'fullstack', 'full-stack'],
            'ai_ml': ['machine learning engineer', 'ml engineer', 'ai engineer', 
                     'artificial intelligence', 'nlp engineer', 'computer vision',
                     'llm', 'generative ai', 'mlops', 'langchain'],
            'data': ['data scientist', 'data analyst'],
            'cloud': ['cloud engineer', 'cloud architect', 'platform engineer',
                     'site reliability', 'infrastructure engineer', 'cloud native'],
            'devops': ['devops', 'sre', 'infrastructure'],
            'mobile': ['mobile', 'android', 'ios', 'flutter developer', 
                      'react native', 'swift', 'kotlin', 'mobile engineer'],
            'qa': ['qa engineer', 'quality assurance', 'test engineer', 'sdet',
                  'automation testing', 'selenium', 'cypress']
        }

        # Initialize result dictionary with all categories
        categorized = {
            'backend': [],
            'frontend': [],
            'fullstack': [],
            'ai_ml': [],
            'data': [],
            'cloud': [],
            'devops': [],
            'mobile': [],
            'qa': [],
            'other': []
        }

        # Categorize each job
        for job in jobs:
            # Combine title and description for keyword matching
            title = job.get('title', '').lower()
            description = job.get('description', '').lower()
            combined_text = f"{title} {description}"

            # Check fullstack first (most specific)
            categorized_flag = False
            if any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['fullstack']):
                categorized['fullstack'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['ai_ml']):
                categorized['ai_ml'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['cloud']):
                categorized['cloud'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['data']):
                categorized['data'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['mobile']):
                categorized['mobile'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['qa']):
                categorized['qa'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['backend']):
                categorized['backend'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['frontend']):
                categorized['frontend'].append(job)
                categorized_flag = True
            elif any(keyword in combined_text for keyword in CATEGORY_KEYWORDS['devops']):
                categorized['devops'].append(job)
                categorized_flag = True

            # If no match, assign to 'other'
            if not categorized_flag:
                categorized['other'].append(job)

        return categorized



def main():
    """
    Main entry point for Serper-based scraper.
    """
    # Initialize scraper
    scraper = SerperJobScraper(location=DEFAULT_LOCATION)
    
    # Scrape all queries
    jobs = scraper.scrape_all_queries(
        queries=SEARCH_QUERIES,
        results_per_query=RESULTS_PER_QUERY
    )
    
    # Export results
    if jobs:
        scraper.export_results(jobs)
        scraper.print_summary(jobs)
    else:
        logger.error("No jobs collected - check API configuration")
    
    logger.info("\n✓ Scraping complete!")


if __name__ == "__main__":
    main()
