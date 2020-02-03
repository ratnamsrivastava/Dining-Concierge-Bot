# importing the requests library
import requests
import json
from decimal import *
import boto3
import datetime


def remove_empty_values(dictionary):
    new_dict = {}
    for key, value in dictionary.items():
        if type(value) is dict:
            new_dict[key] = remove_empty_values(value)
        elif value:
            new_dict[key] = value
    return new_dict

def upload_es(id,cuisine):
    elasticSearch_EndPoint = "https://search-restaurants-55grpnszb6kdmcc2ns453mqu3m.us-east-1.es.amazonaws.com/restaurantsmll/restaurantmll/"+id
    data={
        "id":id,
        "cuisine":cuisine
     }
    headers = {
        'Content-Type': "application/json"}

    r = requests.post(url=elasticSearch_EndPoint, headers=headers, data=json.dumps(data))
    print(r.status_code)


# api-endpoint
URL = "https://api.yelp.com/v3/businesses/search"

dynamodb = boto3.resource('dynamodb')

for i in range(0, 1000, 50):

        # location given here
        term = "Restaurants"
        location = "New York"
        #mexican done , chinese done
        categories = "japanese"
        limit = 50
        sort_by = "rating"
        offset = i
        headers = {'Authorization': 'Bearer 6voUcyijsJmFFLn1PR6V0VsbcJ_csdc6xO08dV_F3bbhPZaWAiTky7GaCSa8oIQP-ohM7j3WsIKU2P_Lme_Yw_Wb7Yl-zxTUZv4eVS-33yzngIpIV5pgPHMQOZiNXHYx'}
        # defining a params dict for the parameters to be sent to the API
        PARAMS = {'term': term, 'location': location, 'categories': categories, 'limit':limit, 'sort_by':sort_by, 'offset':offset }

        # sending get request and saving the response as response object
        r = requests.get(url=URL,headers=headers, params=PARAMS)

        # extracting data in json format
        data = r.json()


        #with open('data.json',
        #         'w') as f:
        #   json.dump(data, f)
        table = dynamodb.Table('yelp-restaurants2')

        for business in data['businesses']:
            id=business['id']
            timestamp=str(datetime.datetime.now())
            cuisine=categories
            name=business['name']
            location= str(business['location'])
            coordinates=str(business['coordinates'])
            rating = str(business['rating'])
            review_count = str(business['review_count'])

            Item_put = {
                'id': id,
                'cuisine': categories,
                'timestamp': timestamp,
                'name': name,
                'location': location,
                'coordinates': coordinates,
                'rating': rating,
                'num_reviews': review_count,

            }



            table.put_item(Item=remove_empty_values(Item_put))
            upload_es(id,categories)

            print("put successful")
