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
payload = {
    "q": "apple",
    "gl": "us"
}
response = requests.post(url, headers=headers, json=payload)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
