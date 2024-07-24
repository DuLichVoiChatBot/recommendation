import firebase_admin
from firebase_admin import credentials, firestore
import os

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate('./core/touristbot-e8c3c-firebase-adminsdk-it19y-5cd6115996.json')
        firebase_admin.initialize_app(cred)
initialize_firebase()

def getCollection(collection):
    db = firestore.client()
    collection_ref = db.collection(collection)
    docs = collection_ref.stream()
    return docs

def getCollectionByID(collection, ID):
    db = firestore.client()
    query = db.collection(collection).where('id', '==', ID).get()
    return query

def getCollectionByAttribute(collection, attribute, value):
    db = firestore.client()
    query = db.collection(collection).where(attribute, '==', value).get()
    return query

def get_firestore_client():
    return firestore.client()