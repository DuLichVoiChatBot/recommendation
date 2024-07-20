from fastapi import FastAPI
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
import uvicorn
from firebaseHelper import getCollection, getCollectionByID

app = FastAPI()

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
        results.append(doc.to_dict())
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

if __name__ == "__main__":
    uvicorn.run(
        app,  # Truyền đối tượng FastAPI
        host="0.0.0.0",
        port=8000
    )
