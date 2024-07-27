from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class Url(BaseModel):
    url: str

@app.post("/url/")
async def create_short_link(long_url: Url):
    api_url = 'https://api.t.ly/api/v1/link/shorten'
    payload = {
        "long_url": long_url.url,
        "expire_at_datetime": "2035-01-17 15:00:00",
        "description": "Social Media Link",
        "public_stats": True
    }
    headers = {
        'Authorization': 'Bearer QCxI8nJjHdXgOyYOEM7PXaSuuG6tBjxwF2FX2x0Dto7kPsN41QAHB9QkZ1Ax',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return {'Short_link': data['short_url']}
    return {'Status': 'Fail'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)
