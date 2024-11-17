import requests
from dotenv import load_dotenv
load_dotenv()
import os 

SERP_API_KEY = os.getenv("SERP_API_KEY")

# SERP_API_KEY = "cc6b0293dc8ff5eeeb96f3442e940f51d9103682588e23f3ea9f337b0aba532c"
search_url = "https://serpapi.com/search.json"

# Function to fetch data based on task request
def fetch_data(query):
    params = {
        "engine": "google",
        "q": f"{query}",  # Customize the search query
        "api_key": SERP_API_KEY
    }

    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        data = response.json()
        print(data['organic_results'])
if __name__ == "__main__":
    fetch_data(query="tcs email id and adress")