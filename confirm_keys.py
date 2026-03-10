import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_serper():
    api_key = os.getenv('SERPER_API_KEY')
    print(f"Testing Serper API with key ending in: ...{api_key[-5:] if api_key else 'None'}")
    url = "https://google.serper.dev/search"
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    payload = {"q": "test", "num": 1}
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Serper API Key confirmed working.")
        else:
            print(f"❌ Serper API Key failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Serper API connection error: {e}")

def test_tavily():
    api_key = os.getenv('TAVILY_API_KEY')
    print(f"Testing Tavily API with key ending in: ...{api_key[-5:] if api_key else 'None'}")
    url = "https://api.tavily.com/search"
    payload = {"api_key": api_key, "query": "test", "max_results": 1}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Tavily API Key confirmed working.")
        else:
            print(f"❌ Tavily API Key failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Tavily API connection error: {e}")

if __name__ == "__main__":
    test_serper()
    print("-" * 30)
    test_tavily()
