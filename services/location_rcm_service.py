import requests
import numpy as np
import random
import heapq
from sklearn.linear_model import Ridge
from helper.firebaseHelper import getCollection, get_firestore_client
from model.location import Location
import joblib
from enum import Enum
from dotenv import load_dotenv

load_dotenv()
db = get_firestore_client()

def recommend(user_id):
    try:
        posts = db.collection('rates').where('userId', '==', user_id)
        if len(list(posts.stream())) < 5: return {"status": "OK", "data": []}
        data = getCollection('locations')
        ids = []
        X = []
        for i in data:
            temp = i.to_dict()
            ids.append(temp['ID'])
            X.append([int(i) for i in temp['tags'].split('|')])
        X_map = {}
        fill_rates = {}
        for index, value in enumerate(ids):
            X_map[value] = X[index]
            fill_rates[value] = -1
        # ==================TU========================
        for i in posts.stream():
            temp = i.to_dict()
            post_id = temp['locationId']
            rate = temp['rating']
            fill_rates[post_id] = rate #fill fill_rates[post_id] = rate
        # =====================================================
        y_train = []
        X_train = []
        for i in fill_rates.items():
            if i[1] != -1:
                y_train.append(i[1])
                X_train.append(X_map[int(i[0])])
        clf = Ridge(alpha=0.01, fit_intercept  = True)
        clf.fit(X_train, y_train)
        for i in fill_rates.items():
            if i[1] == -1:
                y_pred = round(clf.predict([X_map[i[0]]])[0])
                if y_pred > 5:
                    y_pred = 5
                if y_pred < 1:
                    y_pred = 1
                fill_rates[i[0]] = y_pred 
        
        top_4_keys = heapq.nlargest(4, fill_rates, key=fill_rates.get)
        results = []
        for i in top_4_keys:
            x = db.collection('locations').where('ID', '==', i)
            for j in x.stream():
                temp = j.to_dict()
                if str(temp['Loại']) == "nan":
                    temp['Loại'] = 'None'
                results.append(temp)
        return {"status": "OK", "data": results}
    except:
        return {"status": "OK", "data": []}
    
def getLocationByID():
    
    pass

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