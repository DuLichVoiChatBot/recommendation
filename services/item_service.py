import numpy as np
import joblib
import requests
import threading
import uuid
import time
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from helper.firebaseHelper import getCollection, getCollectionByID, get_firestore_client
from services.location_rcm_service import recommend_items
from dotenv import load_dotenv
import os

load_dotenv()
def train():
    docs = getCollection('locations')
    tags = [doc.to_dict()['tags'] for doc in docs]
    tags = [[int(j) for j in i.split('|')] for i in tags]

    scaler = StandardScaler()
    X = np.array(tags)
    X = scaler.fit_transform(X)
    kmeans = KMeans(n_clusters=4, random_state=42).fit(X)
    joblib.dump(kmeans, './data/model.pkl')

    return kmeans

def get_data_recommendation():
    docs = getCollection('locations')
    tags = []
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        data.append(doc_dict)
        tags.append(doc_dict['tags'])
    tags = [[int(j) for j in i.split('|')] for i in tags]
    X = np.array(tags)
    return X, data

def getUserByID(user_id: str):
    docs = getCollectionByID('users', user_id)
    results = []
    for doc in docs:
        temp = doc.to_dict()['interest']
        user = doc.to_dict()
        user['interest'] = recommend_items(temp[0], temp[1], temp[2])
        results.append(user)
    return results

db = get_firestore_client()
listening_threads = {}
start_chat = False

def create_callback(user_id):
    def callback(doc_snapshot, changes, read_time):
        on_snapshot(doc_snapshot, changes, read_time, user_id)
    return callback

def getdataggmap(tourist_name):
    url = os.getenv('SEARCH_MAP') + tourist_name
    response = requests.request("GET", url)

    return response.json()

def on_snapshot(doc_snapshot, changes, read_time, user_id):
    results = [doc.to_dict() for doc in doc_snapshot]
    results = sorted(results, key=lambda x: x['createdAt'])
    if results and results[-1]['role'] == 'user':
        messages = [{'role': result['role'], 'content': result['text']} for result in results]
        url = os.getenv('SERVER_LLM_URL')
        if messages:
            response = requests.post(url, json=messages)
            content = response.json()
            collection_chat_ref = db.collection('chats')
            map_urls = content['map_urls']
            
            chat_obj = {
                '_id': str(uuid.uuid4()),
                'conversationId': user_id,
                'createdAt': time.time() * 1000,
                'role': content['role'],
                'text': content['content'],
                'user': {
                    '_id': 'chatbot',
                    'avatar': os.getenv('BOT_AVATAR'),
                    'name': 'TouristBot'
                }
            }
            collection_chat_ref.add(chat_obj)

            # for i in map_urls:
            #     if i['tourist_name']:
            #         tourist_name = i['tourist_name']
            #         location_infors = getdataggmap(tourist_name)
            #         for location_infor in location_infors:
            #             chat_obj = {
            #                 '_id': str(uuid.uuid4()),
            #                 'conversationId': user_id,
            #                 'createdAt': time.time() * 1000,
            #                 'role': content['role'],
            #                 'text': location_infor['name'],
            #                 'user': {
            #                     '_id': 'chatbot',
            #                     'avatar': os.getenv('BOT_AVATAR'),
            #                     'name': 'TouristBot'
            #                 },
            #                 'address': location_infor['address'],
            #                 'location': location_infor['location']
            #             }
            #             collection_chat_ref.add(chat_obj)

            return response
    return {'status': 'Fail'}

def listen_for_changes(user_id):
    if start_chat:
        print("Having messages!")
        doc_ref = db.collection('chats').where('conversationId', '==', user_id)
        doc_ref.on_snapshot(create_callback(user_id))

def start_listening(user_id: str):
    global start_chat
    start_chat = True
    if user_id in listening_threads:
        return {"message": "Already listening to changes for this user_id."}

    stop_event = threading.Event().clear()
    thread = threading.Thread(target=listen_for_changes, args=(user_id,))
    thread.start()
    listening_threads[user_id] = thread
    return {"message": "Started listening for changes."}

def stop_listening(user_id: str):
    global start_chat
    start_chat = False
    if user_id not in listening_threads:
        return {"message": "Not listening for this user_id."}
    listening_threads.pop(user_id)
    return {"message": "Stopped listening for changes."}
