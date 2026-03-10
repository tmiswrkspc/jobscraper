# Usage Examples

## Basic Usage

### Run with Default Settings

```bash
python3 scraper.py
```

This will:
- Use queries from `config.py`
- Search in "Bangalore, India"
- Collect 20 results per query
- Save to `output/jobs_*.json` and `output/jobs_*.csv`

## Custom Queries

### Single Custom Query

```python
from serper_api import SerperAPI

api = SerperAPI()
jobs = api.search_jobs(
    query="data scientist",
    location="Mumbai, India",
    num_results=50
)

print(f"Found {len(jobs)} jobs")
for job in jobs[:5]:
    print(f"- {job['title']} at {job['company']}")
```

### Multiple Queries

```python
from scraper import SerperJobScraper

scraper = SerperJobScraper(location="Delhi, India")

custom_queries = [
    "machine learning engineer",
    "devops engineer",
    "cloud architect"
]

jobs = scraper.scrape_all_queries(
    queries=custom_queries,
    results_per_query=30
)

print(f"Total jobs collected: {len(jobs)}")
```

## Different Locations

### Search Multiple Cities

```python
from serper_api import SerperAPI

api = SerperAPI()
all_jobs = []

locations = [
    "Bangalore, India",
    "Mumbai, India",
    "Pune, India",
    "Hyderabad, India"
]

for location in locations:
    jobs = api.search_jobs(
        query="python developer",
        location=location,
        num_results=20
    )
    all_jobs.extend(jobs)
    print(f"{location}: {len(jobs)} jobs")

print(f"Total: {len(all_jobs)} jobs")
```

## Export Options

### Export to JSON Only

```python
import json
from datetime import datetime

# ... collect jobs ...

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"output/jobs_{timestamp}.json"

with open(filename, 'w', encoding='utf-8') as f:
    json.dump(jobs, f, indent=2, ensure_ascii=False)

print(f"Saved to {filename}")
```

### Export to CSV Only

```python
import csv
from datetime import datetime

# ... collect jobs ...

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"output/jobs_{timestamp}.csv"

with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
    writer.writeheader()
    writer.writerows(jobs)

print(f"Saved to {filename}")
```

## Filtering Results

### Filter by Salary

```python
jobs = api.search_jobs(query="software engineer", location="Bangalore, India")

# Filter jobs with salary info
jobs_with_salary = [job for job in jobs if job.get('salary')]

print(f"Jobs with salary: {len(jobs_with_salary)}/{len(jobs)}")
```

### Filter by Company

```python
target_companies = ["Google", "Microsoft", "Amazon", "Meta"]

filtered_jobs = [
    job for job in jobs 
    if any(company.lower() in job['company'].lower() for company in target_companies)
]

print(f"Jobs at target companies: {len(filtered_jobs)}")
```

### Filter by Keywords

```python
keywords = ["remote", "work from home", "hybrid"]

remote_jobs = [
    job for job in jobs
    if any(keyword.lower() in job['description'].lower() for keyword in keywords)
]

print(f"Remote jobs: {len(remote_jobs)}")
```

## Deduplication

### Custom Deduplication Threshold

```python
from deduplicator import deduplicate_jobs

# Stricter matching (95% similarity)
unique_jobs = deduplicate_jobs(jobs, similarity_threshold=0.95)

# Looser matching (85% similarity)
unique_jobs = deduplicate_jobs(jobs, similarity_threshold=0.85)
```

### Skip Deduplication

```python
# Don't deduplicate - keep all results
scraper = SerperJobScraper()
jobs = scraper.scrape_all_queries(queries=SEARCH_QUERIES)
# Don't call deduplicate_jobs()
```

## Scheduling

### Daily Cron Job

```bash
# Run every day at 9 AM
0 9 * * * cd /path/to/indeed-job-scraper && /usr/bin/python3 scraper.py
```

### Weekly Cron Job

```bash
# Run every Monday at 8 AM
0 8 * * 1 cd /path/to/indeed-job-scraper && /usr/bin/python3 scraper.py
```

## Error Handling

### Graceful API Failures

```python
from serper_api import SerperAPI

api = SerperAPI()

try:
    jobs = api.search_jobs(
        query="software engineer",
        location="Bangalore, India"
    )
    print(f"Success: {len(jobs)} jobs")
except Exception as e:
    print(f"Error: {e}")
    jobs = []
```

### Retry Logic

```python
import time

def search_with_retry(api, query, location, max_retries=3):
    for attempt in range(max_retries):
        try:
            jobs = api.search_jobs(query=query, location=location)
            return jobs
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # Wait 5 seconds before retry
    return []

jobs = search_with_retry(api, "python developer", "Bangalore, India")
```

## Advanced Usage

### Combine Multiple Sources

```python
from serper_api import SerperAPI

api = SerperAPI()
all_jobs = []

# Different query variations
queries = [
    "software engineer Bangalore",
    "software developer Bangalore",
    "programmer Bangalore"
]

for query in queries:
    jobs = api.search_jobs(query=query, location="Bangalore, India")
    all_jobs.extend(jobs)

# Deduplicate combined results
from deduplicator import deduplicate_jobs
unique_jobs = deduplicate_jobs(all_jobs)

print(f"Total: {len(all_jobs)} → Unique: {len(unique_jobs)}")
```

### Track API Usage

```python
from serper_api import SerperAPI

api = SerperAPI()
queries_used = 0

for query in SEARCH_QUERIES:
    jobs = api.search_jobs(query=query, location="Bangalore, India")
    queries_used += 1
    print(f"Query {queries_used}: {len(jobs)} jobs")

print(f"\nTotal API calls: {queries_used}")
print(f"Remaining this month: {2500 - queries_used}")
```

## Integration Examples

### Save to Database

```python
import sqlite3

# Create database
conn = sqlite3.connect('jobs.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        salary TEXT,
        link TEXT UNIQUE,
        collected_date TEXT
    )
''')

# Insert jobs
from datetime import datetime
collected_date = datetime.now().isoformat()

for job in jobs:
    try:
        cursor.execute('''
            INSERT INTO jobs (title, company, location, salary, link, collected_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job['title'],
            job['company'],
            job['location'],
            job.get('salary'),
            job['link'],
            collected_date
        ))
    except sqlite3.IntegrityError:
        pass  # Skip duplicates

conn.commit()
conn.close()
```

### Send Email Notification

```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification(jobs_count):
    msg = MIMEText(f"Job scraper completed. Collected {jobs_count} jobs.")
    msg['Subject'] = 'Job Scraper Results'
    msg['From'] = '[email]'
    msg['To'] = '[email]'
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('[email]', '[password]')
        server.send_message(msg)

# After scraping
send_email_notification(len(jobs))
```

## Testing

### Test API Connection

```bash
python3 test_api.py
```

### Test Single Query

```python
from serper_api import SerperAPI

api = SerperAPI()

if api.is_configured():
    jobs = api.search_jobs("test query", "Bangalore, India", num_results=5)
    print(f"✓ API working - {len(jobs)} jobs found")
else:
    print("✗ API key not configured")
```

## Tips & Best Practices

1. **Start small**: Test with 1-2 queries before running all
2. **Monitor usage**: Check [serper.dev/dashboard](https://serper.dev/dashboard) regularly
3. **Use specific queries**: "python developer Bangalore" better than "developer"
4. **Deduplicate**: Always run deduplication to remove duplicates
5. **Schedule wisely**: Daily runs use 8 API calls = 240/month (well under 2,500 limit)
6. **Backup data**: Keep historical exports for trend analysis
7. **Handle errors**: Always wrap API calls in try-except blocks
