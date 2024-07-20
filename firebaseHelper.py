import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def getCollection(collection):
    if not firebase_admin._apps:
        cred = credentials.Certificate('touristbot-e8c3c-firebase-adminsdk-it19y-5cd6115996.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    collection_ref = db.collection(collection)
    docs = collection_ref.stream()
    return docs

def getCollectionByID(collection, ID):
    if not firebase_admin._apps:
        cred = credentials.Certificate('touristbot-e8c3c-firebase-adminsdk-it19y-5cd6115996.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    query = db.collection(collection).where('id', '==', ID).get()
    return query

def getCollectionByAttribute(collection, attribute, value):
    if not firebase_admin._apps:
        cred = credentials.Certificate('touristbot-e8c3c-firebase-adminsdk-it19y-5cd6115996.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    query = db.collection(collection).where(attribute, '==', value).get()
    return query