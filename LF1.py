from botocore.vendored import requests
import json
import os
import time
import dateutil.parser
import logging
import datetime
import urllib
import sys
import boto3
# import argparse
# import pprint


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
API_KEY = '6voUcyijsJmFFLn1PR6V0VsbcJ_csdc6xO08dV_F3bbhPZaWAiTky7GaCSa8oIQP-ohM7j3WsIKU2P_Lme_Yw_Wb7Yl-zxTUZv4eVS-33yzngIpIV5pgPHMQOZiNXHYx'
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {
    'Authorization': 'Bearer %s' % API_KEY
}

# # Defaults for our simple example.
# DEFAULT_TERM = 'dinner'
# DEFAULT_LOCATION = 'San Francisco, CA'
# SEARCH_LIMIT = 3


# def request(host, path, api_key, url_params=None):
#     """Given your API_KEY, send a GET request to the API.
#     Args:
#         host (str): The domain host of the API.
#         path (str): The path of the API after the domain.
#         API_KEY (str): Your API Key.
#         url_params (dict): An optional set of query parameters in the request.
#     Returns:
#         dict: The JSON response from the request.
#     Raises:
#         HTTPError: An error occurs from the HTTP request.
#     """
#     url_params = url_params or {}
#     url = '{0}{1}'.format(host, quote(path.encode('utf8')))
#     headers = {
#         'Authorization': 'Bearer %s' % api_key,
#     }

#     print(u'Querying {0} ...'.format(url))

#     response = requests.request('GET', url, headers=headers, params=url_params)

#     return response.json()


# def search(api_key, params, location):
#     """Query the Search API by a search term and location.
#     Args:
#         term (str): The search term passed to the API.
#         location (str): The search location passed to the API.
#     Returns:
#         dict: The JSON response from the request.
#     """

#     url_params = {
#         'term': 'dinner',
#         'location': params['location'].replace(' ', '+'),
#         'open_at':params['open_at'],
#         'radius':1000,
#         'sort_by':'rating',
#         'categories':params['categories'],
#         'limit': SEARCH_LIMIT
#     }
#     return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)



# def query_api(params, location):
#     """Queries the API by the input values from the user.
#     Args:
#         term (str): The search term to query.
#         location (str): The location of the business to query.
#     """
#     response = search(API_KEY, params, location)

#     businesses = response.get('businesses')

#     if not businesses:
#         print(u'No businesses for {0} in {1} found.'.format(term, location))
#         return

#     business_id = businesses[0]['id']

#     print(u'{0} businesses found, querying business info ' \
#         'for the top result "{1}" ...'.format(
#             len(businesses), business_id))
#     response = get_business(API_KEY, business_id)

#     print(u'Result for business "{0}" found:'.format(business_id))
#     pprint.pprint(response, indent=2)


try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def lambda_handler(event, context):
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    return dispatch(event)

def dispatch(intent_request):

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GreetingIntent':
        return greet(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you(intent_request)
    elif intent_name == 'DiningSuggestionsIntent':
        return suggest_places(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')

def greet(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitIntent',
            'message': {
                'contentType': 'PlainText',
                'content': 'Hi there, how can I help?'
            }
        }
    }
    return response

def thank_you(intent_request):
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    return close(
            session_attributes,
            'Fulfilled',
            {
                'contentType': 'PlainText',
                'content': 'Thank you. Hope you enjoyed our service.'
            }
        )

def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': {'contentType':'PlainText', 'content':message}
        }
    }

    return response

def suggest_places(intent_request):
    slots = intent_request['currentIntent']['slots']
    cuisine_type = slots['Cuisine']
    people_count = slots['PeopleCount']
    city = slots['Location']
    date = slots['Date']
    # phone='+17323971296'
    phone = str(slots['Phone'])
    # time = int(datetime.datetime.strptime(slots['Time']))
    time_open = slots['Time']
    if phone[:2] != '+1':
        phone = '+1'+phone
    print(date, time_open)

    # print(date)
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    if intent_request['invocationSource'] == 'DialogCodeHook':
        validation_result = validate_suggest_place(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            # print(validation_result['message'])
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        return delegate(session_attributes, intent_request['currentIntent']['slots'])
    request_time = str(int(time.mktime(datetime.datetime.strptime((date+' '+time_open), '%Y-%m-%d %H:%M').timetuple())))
    PARAMETERS={'term':'dinner',
                'limit':5,
                'open_at':request_time,
                'radius':1000,
                'sort_by':'best_match',
                'categories':cuisine_type,
                'location':city}
    # url = '{0}{1}'.format(API_HOST, quote(SEARCH_PATH.encode('utf8')))
    # print(url)
    # print(PARAMETERS)
    # response= requests.api.request('GET', url= url, params= PARAMETERS, headers= HEADERS)
    # print(response)
    # response=requests.api.get(url='http://www.google.com')
    # print(response, 'Hi')
    # business_data = response.json()
    # print(business_data)

    # record = []
    # for b in business_data['businesses']:
    #     biz_rating = b['rating']
    #     biz_name = b['name']
    #     biz_location = b['location'].get('address1')
    #     record.append(biz_name+' at '+biz_location+', with rating: '+('{}'.format(biz_rating)))
    #     print(record)
    # message = ' \n '.join(record)
    # print(type(message))

    # return {
    #     "sessionAttributes":{},
    #     "dialogAction":{
    #         "type":"Close",
    #         "fulfillmentState":"Fulfilled",
    #         "message":{
    #             "contentType":"PlainText",
    #             "content": record
    #         }
    #     }
    # }
    sqsmessage= cuisine_type+' '+phone
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/628420004148/assignment2'
    response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': cuisine_type
                },
                'phone': {
                    'DataType': 'String',
                    'StringValue': phone

                }
              },
            MessageBody=(
               sqsmessage
               )
              )
    """
    if cuisine_type:
        sqs = boto3.client('sqs')
        queue_url = 'https://sqs.us-east-1.amazonaws.com/628420004148/assignment2'
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageAttributes={
                'cuisine': {
                    'DataType': 'String',
                    'StringValue': 'french'
                    },
                'phone': {
                    'DataType': 'String',
                    'StringValue': '+17323971296'

                }

            },
           MessageBody=(
               'Information about current NY Times fiction bestseller for '
               'week of 12/11/2016.'
               )

)
"""
    return close(
        session_attributes,
        'Fulfilled',
        'I have sent my suggestions to the following phone number: \n'+phone
    )

def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n

def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland']
    return city.lower() in valid_cities

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def isvalid_cuisine_type(cuisine_type):
    cuisines = ['japanese', 'chinese', 'indian', 'italian']
    return cuisine_type.lower() in cuisines

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_suggest_place(slots):
    v_city = slots['Location']
    v_date = slots['Date']
    v_time = slots['Time']
    v_peoplecount = safe_int(slots['PeopleCount'])
    v_cuisine_type = slots['Cuisine']

    if v_city and not isvalid_city(v_city):
        return build_validation_result(
            False,
            'Location',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(pickup_city)
        )

    if v_date:
        if not isvalid_date(v_date):
            return build_validation_result(False, 'Date', 'I did not understand the data you provided. Can you please tell me what date are you planning to go?')
        if datetime.datetime.strptime(v_date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'Date', 'Suggestions cannot be made for date earlier than today.  Can you try a different date?')

    if v_peoplecount is not None and v_peoplecount < 1 and v_peoplecount > 20:
        return build_validation_result(
            False,
            'PeopleCount',
            'Total number of people going should be between 1 and 20.  Can you provide a different count of people?'
        )

    if v_cuisine_type and not isvalid_cuisine_type(v_cuisine_type):
        return build_validation_result(
            False,
            'Cuisine',
            'I did not recognize that cuisine.  What cuisine would you like to try?  '
            'Popular cuisines are Japanese, Indian, or Italian')

    return {'isValid': True}

def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }

def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }
