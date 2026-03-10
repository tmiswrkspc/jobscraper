# Current Improvements

Practical enhancements you can implement **right now** with zero additional cost and no new dependencies. All improvements respect the constraints in `DECISIONS.md` and follow conventions in `CONVENTIONS.md`.

---

## Quick Wins (Implement Today)

### 1. Expand Search Queries (5 minutes)

**Current**: 8 queries → ~70-75 jobs  
**Improved**: 30 queries → ~200-250 jobs

Edit `config.py`:

```python
SEARCH_QUERIES = [
    # Bangalore - Core roles
    "software engineer Bangalore",
    "python developer Bangalore",
    "data analyst Bangalore",
    "frontend developer Bangalore",
    "java developer Bangalore",
    "full stack developer Bangalore",
    "data scientist Bangalore",
    "devops engineer Bangalore",
    "backend developer Bangalore",
    "machine learning engineer Bangalore",
    
    # Bangalore - Specific tech
    "django developer Bangalore",
    "react developer Bangalore",
    "nodejs developer Bangalore",
    "aws engineer Bangalore",
    "kubernetes engineer Bangalore",
    
    # Remote India
    "remote software engineer India",
    "remote python developer India",
    "remote full stack developer India",
    "work from home developer India",
    "remote backend engineer India",
    
    # Other cities
    "software engineer Mumbai",
    "software engineer Pune",
    "software engineer Hyderabad",
    "software engineer Delhi",
    "python developer Mumbai",
    
    # Experience levels
    "junior software engineer Bangalore",
    "senior software engineer Bangalore",
    "lead developer Bangalore",
    
    # Domains
    "fintech developer Bangalore",
    "ecommerce developer Bangalore",
]
```

**Impact**: 3x more jobs per run, still under API limit (30 calls vs 2,500/month)

---

### 2. Extract Skills from Descriptions (30 minutes)

Add to `serper_api.py` after the `_normalize_*` methods:

```python
def _extract_skills(self, text: str) -> List[str]:
    """Extract common tech skills from job description."""
    if not text:
        return []
    
    # Common skills to detect (expand this list)
    skills_keywords = [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Rust', 'C++',
        'React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js',
        'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Terraform',
        'Git', 'CI/CD', 'Jenkins', 'GitHub Actions',
        'REST API', 'GraphQL', 'gRPC', 'Microservices',
        'Machine Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in skills_keywords:
        if skill.lower() in text_lower:
            found_skills.append(skill)
    
    return found_skills
```

Then update both normalization methods to add `'skills': self._extract_skills(description)` to the job dict.

**Impact**: Enables filtering and analysis by skills

---

### 3. Add Job Categorization (30 minutes)

Add to `scraper.py`:

```python
def categorize_jobs(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize jobs by role type.
    
    Returns:
        Dict mapping category name to list of jobs
    """
    categories = {
        'backend': [],
        'frontend': [],
        'fullstack': [],
        'data': [],
        'devops': [],
        'mobile': [],
        'other': []
    }
    
    for job in jobs:
        title_lower = job['title'].lower()
        desc_lower = job.get('description', '').lower()
        combined = title_lower + ' ' + desc_lower
        
        if any(kw in combined for kw in ['backend', 'django', 'flask', 'spring', 'api', 'server']):
            categories['backend'].append(job)
        elif any(kw in combined for kw in ['frontend', 'react', 'angular', 'vue', 'css', 'ui']):
            categories['frontend'].append(job)
        elif any(kw in combined for kw in ['full stack', 'fullstack', 'full-stack']):
            categories['fullstack'].append(job)
        elif any(kw in combined for kw in ['data scientist', 'data analyst', 'ml', 'machine learning', 'ai']):
            categories['data'].append(job)
        elif any(kw in combined for kw in ['devops', 'sre', 'infrastructure', 'kubernetes', 'docker']):
            categories['devops'].append(job)
        elif any(kw in combined for kw in ['mobile', 'android', 'ios', 'flutter', 'react native']):
            categories['mobile'].append(job)
        else:
            categories['other'].append(job)
    
    return categories
```

Update `main()` to use it:

```python
# After deduplication
categories = scraper.categorize_jobs(jobs)

# Export by category
for category, cat_jobs in categories.items():
    if cat_jobs:
        cat_filename = f"jobs_{category}_{timestamp}.json"
        cat_path = Path(OUTPUT_DIR) / cat_filename
        with open(cat_path, 'w', encoding='utf-8') as f:
            json.dump(cat_jobs, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ {category.title()}: {len(cat_jobs)} jobs → {cat_path}")
```

**Impact**: Organized exports by role type

---

## Medium Improvements (1-2 hours each)

### 4. Add Filtering Functions

Add to `scraper.py`:

```python
class JobFilter:
    """Filter jobs by various criteria."""
    
    @staticmethod
    def by_skills(jobs: List[Dict], required_skills: List[str]) -> List[Dict]:
        """Filter jobs that mention any of the required skills."""
        filtered = []
        for job in jobs:
            job_skills = job.get('skills', [])
            if any(skill in job_skills for skill in required_skills):
                filtered.append(job)
        return filtered
    
    @staticmethod
    def by_remote(jobs: List[Dict]) -> List[Dict]:
        """Filter only remote jobs."""
        remote_keywords = ['remote', 'work from home', 'wfh', 'anywhere']
        filtered = []
        for job in jobs:
            text = (job['title'] + ' ' + job.get('description', '')).lower()
            if any(kw in text for kw in remote_keywords):
                filtered.append(job)
        return filtered
    
    @staticmethod
    def by_company(jobs: List[Dict], companies: List[str]) -> List[Dict]:
        """Filter jobs from specific companies."""
        filtered = []
        for job in jobs:
            if any(company.lower() in job['company'].lower() for company in companies):
                filtered.append(job)
        return filtered
```

**Usage**:
```python
# In main() after deduplication
python_jobs = JobFilter.by_skills(jobs, ['Python', 'Django'])
remote_jobs = JobFilter.by_remote(jobs)
```

---

### 5. Add Markdown Summary Report

Add to `scraper.py`:

```python
def export_markdown_summary(self, jobs: List[Dict], categories: Dict[str, List[Dict]]) -> str:
    """
    Export jobs as readable Markdown report.
    
    Returns:
        Path to generated markdown file
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"jobs_summary_{timestamp}.md"
    filepath = Path(OUTPUT_DIR) / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"# Job Search Results\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Jobs**: {len(jobs)}\n\n")
        
        # Summary by category
        f.write("## Summary by Category\n\n")
        for category, cat_jobs in categories.items():
            if cat_jobs:
                f.write(f"- **{category.title()}**: {len(cat_jobs)} jobs\n")
        f.write("\n---\n\n")
        
        # Jobs by category
        for category, cat_jobs in categories.items():
            if not cat_jobs:
                continue
                
            f.write(f"## {category.title()} Jobs ({len(cat_jobs)})\n\n")
            
            for i, job in enumerate(cat_jobs[:10], 1):  # Limit to 10 per category
                f.write(f"### {i}. {job['title']}\n\n")
                f.write(f"**Company**: {job['company']}\n\n")
                f.write(f"**Location**: {job['location']}\n\n")
                
                if job.get('salary'):
                    f.write(f"**Salary**: {job['salary']}\n\n")
                
                if job.get('skills'):
                    f.write(f"**Skills**: {', '.join(job['skills'])}\n\n")
                
                f.write(f"**Link**: [{job['link']}]({job['link']})\n\n")
                f.write("---\n\n")
    
    logger.info(f"✓ Markdown summary: {filepath}")
    return str(filepath)
```

**Impact**: Human-readable reports for quick review

---

### 6. Add SQLite Database for Historical Tracking

Create new file `database.py`:

```python
"""
SQLite database for historical job tracking.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class JobDatabase:
    """Store and track jobs over time."""
    
    def __init__(self, db_path: str = "jobs.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                salary TEXT,
                link TEXT UNIQUE NOT NULL,
                description TEXT,
                source TEXT NOT NULL,
                skills TEXT,
                first_seen DATE NOT NULL,
                last_seen DATE NOT NULL,
                times_seen INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TIMESTAMP NOT NULL,
                jobs_found INTEGER NOT NULL,
                new_jobs INTEGER NOT NULL,
                queries_used INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def save_jobs(self, jobs: List[Dict], queries_count: int) -> int:
        """
        Save jobs to database, update if already exists.
        
        Returns:
            Number of new jobs added
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date()
        new_jobs = 0
        
        for job in jobs:
            skills_str = ','.join(job.get('skills', []))
            
            try:
                cursor.execute('''
                    INSERT INTO jobs (title, company, location, salary, link, 
                                    description, source, skills, first_seen, last_seen, times_seen)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    job['title'],
                    job['company'],
                    job['location'],
                    job.get('salary'),
                    job['link'],
                    job.get('description'),
                    job['source'],
                    skills_str,
                    today,
                    today
                ))
                new_jobs += 1
            except sqlite3.IntegrityError:
                # Job already exists, update last_seen and times_seen
                cursor.execute('''
                    UPDATE jobs 
                    SET last_seen = ?, times_seen = times_seen + 1
                    WHERE link = ?
                ''', (today, job['link']))
        
        # Record scrape run
        cursor.execute('''
            INSERT INTO scrape_runs (run_date, jobs_found, new_jobs, queries_used)
            VALUES (?, ?, ?, ?)
        ''', (datetime.now(), len(jobs), new_jobs, queries_count))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database updated: {new_jobs} new jobs, {len(jobs) - new_jobs} existing")
        return new_jobs
    
    def get_new_jobs_since(self, days: int = 7) -> List[tuple]:
        """Get jobs first seen in last N days."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, company, location, link, first_seen
            FROM jobs 
            WHERE first_seen >= date('now', '-' || ? || ' days')
            ORDER BY first_seen DESC
        ''', (days,))
        
        jobs = cursor.fetchall()
        conn.close()
        return jobs
    
    def get_trending_companies(self, days: int = 30, limit: int = 10) -> List[tuple]:
        """Get companies posting most jobs recently."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT company, COUNT(*) as job_count
            FROM jobs
            WHERE first_seen >= date('now', '-' || ? || ' days')
            GROUP BY company
            ORDER BY job_count DESC
            LIMIT ?
        ''', (days, limit))
        
        companies = cursor.fetchall()
        conn.close()
        return companies
```

Update `scraper.py` to use it:

```python
from database import JobDatabase

# In main()
db = JobDatabase()
new_jobs_count = db.save_jobs(jobs, len(SEARCH_QUERIES))

# Print trends
print("\n📊 Trending Companies (Last 30 days):")
for company, count in db.get_trending_companies(30):
    print(f"   {company}: {count} jobs")
```

**Impact**: Historical tracking, trend analysis, new job alerts

---

## Automation (30 minutes)

### 7. Daily Cron Job with Email Notifications

Create `run_daily.sh`:

```bash
#!/bin/bash

cd /path/to/indeed-job-scraper
source venv/bin/activate

echo "Starting daily job scrape: $(date)"
python3 scraper.py

echo "Completed: $(date)"
```

Make executable:
```bash
chmod +x run_daily.sh
```

Add to crontab:
```bash
crontab -e

# Run every day at 9 AM
0 9 * * * /path/to/indeed-job-scraper/run_daily.sh >> /path/to/logs/scraper.log 2>&1
```

**Optional**: Add email notifications by creating `email_notifier.py`:

```python
"""
Email notifications for scraping results.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict

def send_notification(jobs_count: int, new_jobs_count: int, categories: Dict):
    """Send email with scraping results."""
    
    sender = os.getenv('EMAIL_SENDER')
    receiver = os.getenv('EMAIL_RECEIVER')
    password = os.getenv('EMAIL_PASSWORD')
    
    if not all([sender, receiver, password]):
        return  # Skip if not configured
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Daily Job Scrape: {jobs_count} jobs ({new_jobs_count} new)"
    message["From"] = sender
    message["To"] = receiver
    
    html = f"""
    <html>
      <body>
        <h2>Daily Job Scrape Results</h2>
        <p><strong>Total Jobs:</strong> {jobs_count}</p>
        <p><strong>New Jobs:</strong> {new_jobs_count}</p>
        
        <h3>Jobs by Category:</h3>
        <ul>
    """
    
    for category, cat_jobs in categories.items():
        if cat_jobs:
            html += f"<li><strong>{category.title()}:</strong> {len(cat_jobs)} jobs</li>"
    
    html += """
        </ul>
      </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, message.as_string())
```

---

## Implementation Priority

### Week 1: Data Enhancement
1. ✅ Expand search queries to 30+
2. ✅ Add skills extraction
3. ✅ Add job categorization

### Week 2: Better Organization
1. ✅ Add filtering functions
2. ✅ Add Markdown reports
3. ✅ Test all exports

### Week 3: Persistence
1. ✅ Setup SQLite database
2. ✅ Track jobs over time
3. ✅ Generate trend reports

### Week 4: Automation
1. ✅ Setup daily cron job
2. ✅ Add email notifications (optional)
3. ✅ Monitor and tune

---

## What NOT to Do

Following `DECISIONS.md`:

- ❌ Don't add new dependencies (keep it minimal)
- ❌ Don't add async/await yet (synchronous is intentional)
- ❌ Don't change the job dict schema without discussion
- ❌ Don't add subdirectories (flat structure is deliberate)
- ❌ Don't lower `FUZZY_SIMILARITY_THRESHOLD` below 0.85

---

## After These Improvements

You'll have:

✅ **More data**: 30 queries = 200-250 jobs per run  
✅ **Better insights**: Skills extracted, jobs categorized  
✅ **Historical tracking**: SQLite database with trends  
✅ **Multiple formats**: JSON, CSV, Markdown, categorized exports  
✅ **Automation**: Daily runs with optional email alerts  
✅ **Better filtering**: By skills, remote, company  

**All with ZERO additional API costs!**

Then you're ready for Phase 2 (LLM integration) from `FUTURE_UPDATES.md`.
