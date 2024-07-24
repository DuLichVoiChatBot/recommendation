import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('touristbot-e8c3c-firebase-adminsdk-it19y-5cd6115996.json')
firebase_admin.initialize_app(cred)

# Khởi tạo Firestore client
db = firestore.client()

# Tham chiếu đến một collection
collection_ref = db.collection('locations')

# Reference to the collection
collection_ref = db.collection('your-collection-name')

# Data to insert
data = {
    'field1': 'value1',
    'field2': 'value2',
    # Add more fields as needed
}

# Add a document to the collection
collection_ref.add(data)
