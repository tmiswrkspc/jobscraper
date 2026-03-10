"""
Tavily API Integration for Job Enrichment

This module provides optional job enrichment using Tavily AI search.
Falls back gracefully if Tavily API key is not configured.

Features:
- Full job description extraction from URLs
- Company research and information gathering
- Learning resource discovery for skills
- GitHub project recommendations

Free tier: 1,000 requests/month
API docs: https://docs.tavily.com/
"""

import os
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TavilyEnricher:
    """
    Optional job enrichment using Tavily AI search.
    
    Gracefully degrades if API key is not configured.
    All methods return safe defaults on failure.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily enricher.
        
        Args:
            api_key: Tavily API key (reads from TAVILY_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv('TAVILY_API_KEY')
        self.enabled = bool(self.api_key and self.api_key != 'your_tavily_api_key_here')
        
        if not self.enabled:
            logger.info("Tavily enrichment disabled (no API key configured)")
            self.client = None
        else:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("Tavily enrichment enabled")
            except ImportError:
                logger.warning("tavily-python not installed - run: pip install tavily-python")
                self.enabled = False
                self.client = None
            except Exception as e:
                logger.error(f"Failed to initialize Tavily client: {e}")
                self.enabled = False
                self.client = None
    
    def is_enabled(self) -> bool:
        """Check if Tavily enrichment is available."""
        return self.enabled
    
    def enrich_job(self, job: Dict) -> Dict:
        """
        Enrich job with full description from job posting URL.
        
        Args:
            job: Job dictionary with at least 'link' field
            
        Returns:
            Job dictionary with added 'full_description' and 'enriched' fields
            Returns original job if enrichment fails or is disabled
        """
        if not self.enabled:
            return job
        
        try:
            logger.debug(f"Enriching job: {job.get('title')} at {job.get('company')}")
            
            # Extract full content from job URL
            response = self.client.extract(urls=[job['link']])
            
            if response and 'results' in response and response['results']:
                result = response['results'][0]
                
                # Add full content
                job['full_description'] = result.get('raw_content', '')
                job['enriched'] = True
                job['enrichment_source'] = 'tavily'
                
                logger.debug(f"Successfully enriched job: {job['title']}")
            
            return job
            
        except Exception as e:
            logger.warning(f"Tavily enrichment failed for {job.get('link')}: {e}")
            return job
    
    def enrich_jobs_batch(self, jobs: List[Dict], max_jobs: int = 10) -> List[Dict]:
        """
        Enrich multiple jobs (limited to avoid API quota).
        
        Args:
            jobs: List of job dictionaries
            max_jobs: Maximum number of jobs to enrich (default: 10)
            
        Returns:
            List of enriched jobs
        """
        if not self.enabled:
            logger.info("Tavily enrichment skipped (disabled)")
            return jobs
        
        logger.info(f"Enriching up to {max_jobs} jobs with Tavily...")
        
        enriched_count = 0
        for i, job in enumerate(jobs):
            if enriched_count >= max_jobs:
                logger.info(f"Reached enrichment limit ({max_jobs} jobs)")
                break
            
            job = self.enrich_job(job)
            if job.get('enriched'):
                enriched_count += 1
        
        logger.info(f"Enriched {enriched_count} jobs with Tavily")
        return jobs
    
    def research_company(self, company_name: str) -> Optional[Dict]:
        """
        Research company information using Tavily search.
        
        Args:
            company_name: Name of the company to research
            
        Returns:
            Dictionary with company information or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            logger.info(f"Researching company: {company_name}")
            
            query = f"{company_name} company information tech stack culture"
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            if response and 'results' in response:
                company_info = {
                    'company_name': company_name,
                    'summary': response.get('answer', ''),
                    'sources': []
                }
                
                for result in response['results'][:3]:
                    company_info['sources'].append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', '')
                    })
                
                logger.info(f"Found company info for: {company_name}")
                return company_info
            
            return None
            
        except Exception as e:
            logger.error(f"Company research failed for {company_name}: {e}")
            return None
    
    def find_learning_resources(self, skill: str, max_results: int = 5) -> List[Dict]:
        """
        Find learning resources (tutorials, courses, docs) for a skill.
        
        Args:
            skill: Skill name (e.g., "Django", "React", "AWS")
            max_results: Maximum number of resources to return
            
        Returns:
            List of learning resource dictionaries
        """
        if not self.enabled:
            return []
        
        try:
            logger.info(f"Finding learning resources for: {skill}")
            
            query = f"{skill} tutorial course documentation learn"
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results
            )
            
            resources = []
            if response and 'results' in response:
                for result in response['results']:
                    resources.append({
                        'skill': skill,
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('content', ''),
                        'source': 'tavily'
                    })
                
                logger.info(f"Found {len(resources)} learning resources for {skill}")
            
            return resources
            
        except Exception as e:
            logger.error(f"Learning resource search failed for {skill}: {e}")
            return []
    
    def find_github_projects(self, skills: List[str], max_results: int = 5) -> List[Dict]:
        """
        Find relevant GitHub projects demonstrating specific skills.
        
        Args:
            skills: List of skill names
            max_results: Maximum number of projects to return
            
        Returns:
            List of GitHub project dictionaries
        """
        if not self.enabled:
            return []
        
        try:
            skills_str = " ".join(skills)
            logger.info(f"Finding GitHub projects for: {skills_str}")
            
            query = f"github {skills_str} project example repository"
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_domains=["github.com"]
            )
            
            projects = []
            if response and 'results' in response:
                for result in response['results']:
                    if 'github.com' in result.get('url', ''):
                        projects.append({
                            'title': result.get('title', ''),
                            'url': result.get('url', ''),
                            'description': result.get('content', ''),
                            'skills': skills,
                            'source': 'tavily'
                        })
                
                logger.info(f"Found {len(projects)} GitHub projects")
            
            return projects
            
        except Exception as e:
            logger.error(f"GitHub project search failed: {e}")
            return []


def test_tavily_enricher():
    """Test Tavily enricher integration."""
    print("="*70)
    print("TAVILY ENRICHER TEST")
    print("="*70)
    print()
    
    enricher = TavilyEnricher()
    
    if not enricher.is_enabled():
        print("❌ Tavily not configured")
        print("Set TAVILY_API_KEY in .env file")
        return
    
    print("✓ Tavily enricher initialized")
    print()
    
    # Test job enrichment
    print("Testing job enrichment...")
    test_job = {
        'title': 'Senior Python Developer',
        'company': 'Test Corp',
        'link': 'https://www.naukri.com/job-listings-senior-python-developer-test-corp-bangalore-5-to-10-years-123456'
    }
    
    enriched_job = enricher.enrich_job(test_job)
    
    if enriched_job.get('enriched'):
        print("✓ Job enrichment successful")
        print(f"  Full description length: {len(enriched_job.get('full_description', ''))} chars")
    else:
        print("⚠ Job enrichment skipped or failed")
    
    print()
    
    # Test learning resources
    print("Testing learning resource search...")
    resources = enricher.find_learning_resources("Django", max_results=3)
    
    if resources:
        print(f"✓ Found {len(resources)} learning resources")
        for i, resource in enumerate(resources, 1):
            print(f"  {i}. {resource['title']}")
            print(f"     {resource['url']}")
    else:
        print("⚠ No learning resources found")
    
    print()
    print("="*70)


if __name__ == "__main__":
    test_tavily_enricher()
