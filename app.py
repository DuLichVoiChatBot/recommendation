from fastapi import FastAPI
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
import uvicorn
from firebaseHelper import getCollection, getCollectionByID, getCollectionByAttribute
from datetime import datetime, timezone
import threading
import firebase_admin
from firebase_admin import credentials, firestore
import requests
from concurrent.futures import ThreadPoolExecutor
import json
import uuid
import time


app = FastAPI()
start_chat = False
@app.get("/items/{cost_id}&{location_id}&{space_id}")
async def read_item(cost_id: int, location_id: int, space_id: int):
    # costs = {0: 'tuỳ chọn', 1: 'thấp', 2: 'trung bình', 3: 'cao'}
    # locations = {0: 'tuỳ chọn', 1: 'trong nhà', 2: 'ngoài trời'}
    # spaces = {0: 'tuỳ chọn', 1: 'ít người', 2: 'đông người'}
    docs = getCollection('locations')

    tags = []
    data = []
    for doc in docs:
        data.append(doc.to_dict())
        tags.append(doc.to_dict()['tags'])
    tags = [[int(j) for j in i.split('|')] for i in tags]

    scaler = StandardScaler()
    X = np.array(tags)
    elements = X[:]
    X = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=4, random_state=42).fit(X)
    test = [cost_id, location_id, space_id]
    result = kmeans.predict([test])[0]
    predictx = kmeans.predict(X)

    results = []
    for index, value in enumerate(predictx):
        if result == value:
            if elements[index][1] == 1 and test[1] == 2 or elements[index][1] == 2 and test[1] == 1:
                continue
            else:
                results.append(
                    {
                        'ID': str(data[index]['ID']),
                        'Name': str(data[index]['Name']),
                        'Address': str(data[index]['Address']),
                        'Category': str(data[index]['Category']),
                        'Description': str(data[index]['Description']),
                        'Giá': str(data[index]['Giá']),
                        'Loại': str(data[index]['Loại']),
                        'URL': str(data[index]['URL']),
                        'tags': str(data[index]['tags'])
                    }
                )
    return results

@app.get("/chat/")
async def getAllChat():
    docs = getCollection('chats')
    results = []
    for doc in docs:
        results.append(doc.to_dict()['_id'])
    return results

@app.get("/user/{user_id}")
async def getUserByID(user_id: str):
    docs = getCollectionByID('users', user_id)
    results = []
    for doc in docs:
        temp = doc.to_dict()['interest']
        user = doc.to_dict()
        user['interest'] = await read_item(temp[0], temp[1], temp[2])
        results.append(user)
    return results

db = firestore.client()
listening_threads = {}

# Hàm đóng gói
def create_callback(user_id):
    def callback(doc_snapshot, changes, read_time):
        on_snapshot(doc_snapshot, changes, read_time, user_id)
    return callback

def on_snapshot(doc_snapshot, changes, read_time, user_id):
    """
    Hàm callback được gọi khi tài liệu thay đổi.
    """
    results = []
    for doc in doc_snapshot:
        temp = doc.to_dict()
        results.append(temp)

    results = sorted(results, key=lambda x: x['createdAt'])
    if results[-1]['role'] == 'user':
        messages = []
        for result in results:
            messages.append({'role': result['role'], 'content': result['text']})

        url = 'http://0.tcp.ap.ngrok.io:14787/chat'
        if len(messages) != 0:
            response = requests.post(url, json=messages)
            content = json.loads(response.text)
            db_helper = firestore.client()
            collection_chat_ref = db_helper.collection('chats')
            chat_obj = {
                '_id': str(uuid.uuid4()),
                'conversationId': user_id,
                'createdAt': time.time() * 1000,
                'role': content['role'],
                'text': content['content'],
                'user':{
                    '_id': 'chatbot',
                    'avatar': 'https://res.cloudinary.com/dijcunmcx/image/upload/v1721467645/logo.png',
                    'name': 'TouristBot'
                }
            }
            collection_chat_ref.add(chat_obj)
            return response
    return {'status': 'Fail'}

def listen_for_changes(user_id):
    """
    Thiết lập lắng nghe các thay đổi trong Firestore cho user_id cụ thể.
    """
    global start_chat
    if start_chat == True:
        doc_ref = db.collection('chats').where('conversationId', '==', user_id)
        doc_watch = doc_ref.on_snapshot(create_callback(user_id))

@app.get("/start-listening/{user_id}")
async def start_listening(user_id: str):
    global start_chat
    start_chat = True
    if user_id in listening_threads:
        return {"message": "Already listening to changes for this user_id."}

    stop_event = threading.Event().clear
    
    thread = threading.Thread(target=listen_for_changes, args=(user_id,))
    thread.start()

    listening_threads[user_id] = thread

    return {"message": "Started listening for changes."}

@app.get("/stop-listening/{user_id}")
async def stop_listening(user_id: str):
    """
    Dừng lắng nghe thay đổi cho user_id cụ thể.
    """
    global start_chat
    start_chat = False
    if user_id not in listening_threads:
        return {"message": "Not listening for this user_id."}

    listening_threads.pop(user_id)

    return {"message": "Stopped listening for changes."}

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
