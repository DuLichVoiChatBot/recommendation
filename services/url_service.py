from model.url import Url
import requests
from dotenv import load_dotenv
import os
load_dotenv()

def create_short_link(long_url: Url):
    api_url = 'https://api.t.ly/api/v1/link/shorten'
    payload = {
        "long_url": long_url.url,
        "expire_at_datetime": "2035-01-17 15:00:00",
        "description": "Social Media Link",
        "public_stats": True
    }
    headers = {
        'Authorization': 'Bearer ' + os.getenv('KEY_FOODY'),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return {'Short_link': data['short_url']}
    return {'Status': 'Fail'}