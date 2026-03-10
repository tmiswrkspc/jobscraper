"""
Serper API Integration for Job Search

This module provides integration with Serper.dev API for job searches.
Serper provides clean, structured job data from Google without CAPTCHA issues.

Free tier: 2,500 searches/month
API docs: https://serper.dev/docs
"""

import os
import logging
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv
from config import SEARCH_FRESHNESS

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# Skills detection patterns - maps canonical skill names to search patterns
SKILLS_PATTERNS = {
    'Python': ['python'],
    'Java': ['java'],
    'JavaScript': ['javascript', 'js'],
    'TypeScript': ['typescript', 'ts'],
    'Go': ['golang', ' go ', ' go,', ' go.', 'go ', ',go,', '.go.'],
    'Rust': ['rust'],
    'C++': ['c++', 'cpp'],
    'C#': ['c#', 'csharp'],
    'Ruby': ['ruby'],
    'PHP': ['php'],
    'Swift': ['swift'],
    'Kotlin': ['kotlin'],
    'Scala': ['scala'],
    'React': ['react', 'reactjs', 'react.js'],
    'Angular': ['angular'],
    'Vue': ['vue', 'vuejs', 'vue.js'],
    'Django': ['django'],
    'Flask': ['flask'],
    'Spring': ['spring boot', 'spring'],
    'Node.js': ['node.js', 'nodejs', 'node js'],
    'Express': ['express', 'expressjs'],
    'FastAPI': ['fastapi'],
    'PostgreSQL': ['postgresql', 'postgres'],
    'MySQL': ['mysql'],
    'MongoDB': ['mongodb', 'mongo'],
    'Redis': ['redis'],
    'Elasticsearch': ['elasticsearch', 'elastic search'],
    'Cassandra': ['cassandra'],
    'Oracle': ['oracle database', 'oracle db', 'oracle'],
    'SQL Server': ['sql server', 'mssql'],
    'Docker': ['docker'],
    'Kubernetes': ['kubernetes', 'k8s'],
    'AWS': ['aws', 'amazon web services'],
    'Azure': ['azure', 'microsoft azure'],
    'GCP': ['gcp', 'google cloud'],
    'Terraform': ['terraform'],
    'Git': [' git ', 'git,', 'git.', 'git '],
    'CI/CD': ['ci/cd', 'ci cd', 'continuous integration', 'continuous deployment'],
    'Jenkins': ['jenkins'],
    'GitHub Actions': ['github actions'],
    'GitLab CI': ['gitlab ci'],
    'REST API': ['rest api', 'restful', ' rest '],
    'GraphQL': ['graphql'],
    'gRPC': ['grpc'],
    'Microservices': ['microservices', 'micro services', 'micro-services'],
    'Machine Learning': ['machine learning', ' ml ', 'ml,', 'ml.'],
    'Deep Learning': ['deep learning'],
    'TensorFlow': ['tensorflow'],
    'PyTorch': ['pytorch'],
    'Pandas': ['pandas'],
    'NumPy': ['numpy'],
    'Scikit-learn': ['scikit-learn', 'sklearn'],
    'Kafka': ['kafka'],
    'RabbitMQ': ['rabbitmq'],
    'Linux': ['linux'],
    'Bash': ['bash', 'shell scripting'],
    
    # AI/ML (hot in India 2025)
    'LangChain': ['langchain'],
    'LLM': ['llm', 'large language model', 'generative ai', 'gen ai', 'genai'],
    'OpenAI API': ['openai', 'gpt-4', 'gpt4', 'chatgpt api'],
    'HuggingFace': ['huggingface', 'hugging face'],
    'RAG': ['rag', 'retrieval augmented', 'vector database', 'vector db', 'pinecone', 'weaviate'],
    'MLOps': ['mlops', 'ml ops', 'model serving', 'model deployment'],

    # Cloud & Infra
    'Snowflake': ['snowflake'],
    'Databricks': ['databricks'],
    'Airflow': ['airflow', 'apache airflow'],
    'Celery': ['celery'],
    'ArgoCD': ['argocd', 'argo cd', 'gitops'],
    'Ansible': ['ansible'],
    'Prometheus': ['prometheus'],
    'Grafana': ['grafana'],

    # Web Frameworks
    'Next.js': ['next.js', 'nextjs'],
    'NestJS': ['nestjs', 'nest.js'],
    'Spring Boot': ['spring boot', 'springboot'],
    'WebSocket': ['websocket', 'socket.io'],

    # Domain
    'Agile': ['agile', 'scrum'],
    'System Design': ['system design', 'distributed systems'],
    'FinTech': ['fintech', 'payment gateway', 'upi integration'],
}

def extract_skills(text: str) -> List[str]:
    """
    Extract technical skills from job description text.
    """
    if not text:
        return []

    text_lower = text.lower()
    detected_skills = []
    for skill_name, patterns in SKILLS_PATTERNS.items():
        for pattern in patterns:
            if pattern.lower() in text_lower:
                detected_skills.append(skill_name)
                break
    return detected_skills


class SerperAPI:
    """
    Serper API client for job searches.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Serper API client.
        
        Args:
            api_key: Serper API key (reads from SERPER_API_KEY env var if not provided)
        """
        self.api_key = api_key or os.getenv('SERPER_API_KEY')
        
        if not self.api_key or self.api_key == 'your_api_key_here':
            logger.warning("Serper API key not configured - API calls will fail")
            logger.warning("Set SERPER_API_KEY in .env file or environment variable")
        
        self.search_url = "https://google.serper.dev/search"
        self.jobs_url = "https://google.serper.dev/jobs"
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def is_configured(self) -> bool:
        """
        Check if API key is properly configured.
        
        Returns:
            True if API key is set and not placeholder
        """
        return bool(self.api_key and self.api_key != 'your_api_key_here')
    
    def search_jobs(
        self,
        query: str,
        location: str = "Bangalore, India",
        num_results: int = 10
    ) -> List[Dict]:
        """
        Search for jobs using Serper API (tries jobs endpoint first, falls back to search).
        
        Args:
            query: Job search query (e.g., "software engineer")
            location: Location for job search
            num_results: Number of results to return (max 100)
            
        Returns:
            List of job dictionaries with standardized fields
        """
        if not self.is_configured():
            logger.error("Serper API key not configured")
            return []
        
        # Try jobs endpoint first
        jobs = self._search_jobs_endpoint(query, location, num_results)
        if jobs:
            return jobs
        
        # Fallback to regular search
        logger.info("[Serper] Jobs endpoint returned no results, trying search endpoint")
        return self._search_regular_endpoint(query, location, num_results)
    
    def _search_jobs_endpoint(
        self,
        query: str,
        location: str,
        num_results: int
    ) -> List[Dict]:
        """
        Search using dedicated jobs endpoint.
        """
        payload = {
            "q": query,
            "location": location,
            "gl": "in",
            "hl": "en",
            "num": min(num_results, 100)
        }
        
        try:
            logger.info(f"[Serper Jobs] Searching: '{query}' in '{location}'")
            
            response = requests.post(
                self.jobs_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            jobs = self._normalize_jobs_endpoint_results(data)
            logger.info(f"[Serper Jobs] Found {len(jobs)} jobs")
            
            return jobs
            
        except Exception as e:
            logger.warning(f"[Serper Jobs] Request failed: {e}")
            return []
    
    def _search_regular_endpoint(
        self,
        query: str,
        location: str,
        num_results: int
    ) -> List[Dict]:
        """
        Search using regular search endpoint.
        """
        search_query = f"{query} site:linkedin.com/jobs OR site:naukri.com/job-listings OR site:instahyre.com"
        
        payload = {
            "q": search_query,
            "gl": "in",
            "hl": "en",
            "num": min(num_results, 100),
            "tbs": SEARCH_FRESHNESS
        }
        
        try:
            logger.info(f"[Serper Search] Searching: '{search_query}'")
            
            response = requests.post(
                self.search_url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            jobs = self._normalize_search_results(data, query, location)
            logger.info(f"[Serper Search] Found {len(jobs)} jobs")
            
            return jobs
            
        except Exception as e:
            logger.error(f"[Serper Search] Request failed: {e}")
            return []
    
    def _normalize_jobs_endpoint_results(self, data: Dict) -> List[Dict]:
            """
            Normalize results from jobs endpoint.
            """
            jobs = []
            job_results = data.get('jobs', [])

            for result in job_results:
                job = {
                    'title': result.get('title', ''),
                    'company': result.get('company', 'Unknown'),
                    'location': result.get('location', ''),
                    'link': result.get('link', ''),
                    'salary': result.get('salary'),
                    'posted_date': result.get('date'),
                    'description': result.get('description', ''),
                    'source': 'serper_jobs_api',
                    'skills': extract_skills(result.get('description', ''))
                }

                if job['title'] and job['company'] and job['link']:
                    jobs.append(job)

            return jobs
    
    def _normalize_search_results(
        self,
        data: Dict,
        query: str,
        location: str
    ) -> List[Dict]:
        """
        Normalize results from search endpoint.
        """
        jobs = []
        organic_results = data.get('organic', [])

        for result in organic_results:
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            link = result.get('link', '')

            if not self._is_job_result(title, snippet, link):
                continue

            job = {
                'title': self._extract_job_title(title),
                'company': self._extract_company(title, snippet),
                'location': location,
                'link': link,
                'salary': None,
                'posted_date': None,
                'description': snippet,
                'source': 'serper_search_api',
                'skills': extract_skills(snippet)
            }

            if job['title'] and job['company'] and job['link']:
                jobs.append(job)

        return jobs

    
    def _is_job_result(self, title: str, snippet: str, link: str) -> bool:
        """Check if result is job-related."""
        job_domains = [
            'naukri.com', 'foundit.in', 'shine.com', 'indeed.com',
            'linkedin.com', 'glassdoor.com', 'monster.com', 'timesjobs.com'
        ]
        
        for domain in job_domains:
            if domain in link.lower():
                return True
        
        job_keywords = ['job', 'hiring', 'vacancy', 'opening', 'career', 'position']
        text = (title + ' ' + snippet).lower()
        
        return any(keyword in text for keyword in job_keywords)
    
    def _extract_job_title(self, title: str) -> str:
        """Extract clean job title."""
        suffixes = [' - Naukri.com', ' - Indeed', ' - LinkedIn', ' | Glassdoor']
        
        for suffix in suffixes:
            if suffix in title:
                title = title.split(suffix)[0]
        
        return title.strip()
    
    def _extract_company(self, title: str, snippet: str) -> str:
        """Extract company name."""
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                company = parts[-1]
                site_names = ['Naukri.com', 'Indeed', 'LinkedIn', 'Glassdoor']
                for site in site_names:
                    if site in company:
                        if len(parts) >= 3:
                            company = parts[-2]
                        break
                return company.strip()
        
        import re
        match = re.search(r'Company:\s*([^,\.\n]+)', snippet)
        if match:
            return match.group(1).strip()
        
        match = re.search(r'\bat\s+([A-Z][a-zA-Z\s&]+?)(?:\s+in|\s+for|\.|,)', snippet)
        if match:
            return match.group(1).strip()
        
        return 'Unknown'
    def _extract_skills(self, text: str) -> List[str]:
        """
        [DEPRECATED] Use module-level extract_skills instead.
        """
        return extract_skills(text)


def test_serper_api():
    """Test Serper API integration."""
    print("="*70)
    print("SERPER API TEST")
    print("="*70)
    
    api = SerperAPI()
    
    if not api.is_configured():
        print("❌ API key not configured")
        print("Set SERPER_API_KEY in .env file")
        return
    
    print("✓ API key configured")
    print()
    
    print("Testing search: 'software engineer' in 'Bangalore, India'")
    print("-"*70)
    
    jobs = api.search_jobs(
        query="software engineer",
        location="Bangalore, India",
        num_results=10
    )
    
    print(f"\nFound {len(jobs)} jobs:")
    print()
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job['location']}")
        print(f"   Source: {job['source']}")
        print(f"   Link: {job['link'][:60]}...")
        print()
    
    print("="*70)


if __name__ == "__main__":
    test_serper_api()
