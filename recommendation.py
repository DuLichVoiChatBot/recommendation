from fastapi import FastAPI
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
import uvicorn

app = FastAPI()

costs = {0: 'tuỳ chọn', 1: 'thấp', 2: 'trung bình', 3: 'cao'}
locations = {0: 'tuỳ chọn', 1: 'trong nhà', 2: 'ngoài trời'}
spaces = {0: 'tuỳ chọn', 1: 'ít người', 2: 'đông người'}

data = pd.read_excel('data_touristbot.xlsx')
list_location = data['Name']
IDs = data['ID']

tags = data['tags']
tags = [[int(j) for j in i.split('|')] for i in tags]

scaler = StandardScaler()
X = np.array(tags)
elements = X[:]
X = scaler.fit_transform(X)
kmeans = KMeans(n_clusters=4, random_state=42).fit(X)

@app.get("/items/{cost_id}&{location_id}&{space_id}")
async def read_item(cost_id: int, location_id: int, space_id: int):
    test = [cost_id, location_id, space_id]
    result = kmeans.predict([test])[0]
    predictx = kmeans.predict(X)
    results = []
    for index, value in enumerate(predictx):
        if result == value:
            if elements[index][1] == 1 and test[1] == 2 or elements[index][1] == 2 and test[1] == 1:
                continue
            else:
                results.append({'id': str(IDs[index]) , 'name':list_location[index]})
    return {"suggested_locations": results}

if __name__ == "__main__":
    uvicorn.run(
        app,  # Truyền đối tượng FastAPI
        host="0.0.0.0",
        port=8000
    )
