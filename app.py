from fastapi import FastAPI
import uvicorn
from model.url import Url
from services.location_rcm_service import recommend
from services.url_service import create_short_link
from services.item_service import recommend_items as service_recommend_items, getUserByID as service_getUserByID, start_listening as service_start_listening, stop_listening as service_stop_listening, train
from dotenv import load_dotenv
import os 

app = FastAPI()
load_dotenv()
start_chat = False

@app.get("/train_rcm")
async def train_rcm():
    model = train()
    if model: 
        return {
            'Status': 'Successfully'
        }
    return {
            'Status': 'Fail'
        }

@app.get("/items/{cost_id}&{location_id}&{space_id}")
async def recommend_items(cost_id: int, location_id: int, space_id: int):
    results = service_recommend_items(cost_id, location_id, space_id)
    return results

@app.get("/user/{user_id}")
async def get_user_by_id(user_id: str):
    results = service_getUserByID(user_id)
    return results

@app.get("/start-listening/{user_id}")
async def start_listening(user_id: str):
    return service_start_listening(user_id)

@app.get("/stop-listening/{user_id}")
async def stop_listening(user_id: str):
    return service_stop_listening(user_id)

@app.post("/url/")
async def create_short_link1(long_url: Url):
    return create_short_link(long_url)

@app.get("/recommend/{user_id}")
async def rcm(user_id):
    return recommend(user_id)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host= str(os.getenv('HOST')),
        port= int(os.getenv('PORT'))
    )
