import os
from helper.firebaseHelper import getCollection

docs = getCollection('chats')
for doc in docs:
    print("Data:")
    print(f'{doc.id} => {doc.to_dict()}')
