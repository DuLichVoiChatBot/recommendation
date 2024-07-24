import numpy as np
import joblib
import requests
import threading
import uuid
import time
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from model.location import Location
from helper.firebaseHelper import getCollection, getCollectionByID, get_firestore_client
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

def create_dict_item(location):
    return {
        'ID': location.ID,
        'Name': location.Name,
        'Address': location.Address,
        'Category': location.Category,
        'Description': location.Description,
        'Giá': location.Price,
        'Loại': location.Type,
        'URL': location.Url,
        'tags': location.Tags
    }

def recommend_items(cost_id: int, location_id: int, space_id: int):
    kmeans = joblib.load('./data/model.pkl')
    elements, data = get_data_recommendation()
    test = [cost_id, location_id, space_id]
    result = kmeans.predict([test])[0]
    predictx = kmeans.predict(elements)

    results = []
    for index, value in enumerate(predictx):
        if result == value:
            if (elements[index][1] == 1 and test[1] == 2) or (elements[index][1] == 2 and test[1] == 1):
                continue
            location = Location(
                str(data[index]['ID']),
                str(data[index]['Name']),
                str(data[index]['Address']),
                str(data[index]['Category']),
                str(data[index]['Description']),
                str(data[index]['Giá']),
                str(data[index]['Loại']),
                str(data[index]['URL']),
                str(data[index]['tags'])
            )
            results.append(create_dict_item(location))

    return results

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
            chat_obj = {
                '_id': str(uuid.uuid4()),
                'conversationId': user_id,
                'createdAt': time.time() * 1000,
                'role': content['role'],
                'text': content['content'],
                'user': {
                    '_id': 'chatbot',
                    'avatar': 'https://res.cloudinary.com/dijcunmcx/image/upload/v1721467645/logo.png',
                    'name': 'TouristBot'
                }
            }
            collection_chat_ref.add(chat_obj)
            return response
    return {'status': 'Fail'}

def listen_for_changes(user_id):
    if start_chat:
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
