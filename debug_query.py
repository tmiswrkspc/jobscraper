import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('SERPER_API_KEY')
url = "https://google.serper.dev/search"
headers = {
    'X-API-KEY': api_key,
    'Content-Type': 'application/json'
}
query = "software engineer Bangalore site:linkedin.com/jobs OR site:naukri.com/job-listings OR site:instahyre.com"
payload = {
    "q": query,
    "gl": "in",
    "hl": "en",
    "num": 20,
    "tbs": "qdr:w"
}
try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
