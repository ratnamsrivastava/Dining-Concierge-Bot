import json
import boto3
from botocore.vendored import requests
queue_url='https://sqs.us-east-1.amazonaws.com/628420004148/assignment2'
sqs = boto3.resource('sqs')
sqs2 = boto3.client('sqs')

queue = sqs.get_queue_by_name(QueueName='assignment2')
sns = boto3.client('sns')
client = boto3.client('dynamodb')

host = 'search-restaurants-55grpnszb6kdmcc2ns453mqu3m.us-east-1.es.amazonaws.com' # For example, search-mydomain-id.us-west-1.es.amazonaws.com
#index = 'restaurants'  #Old
index = 'predictions'
url = 'https://' + host + '/' + index + '/_search'

def lambda_handler(event, context):
    # TODO implement
    for message in queue.receive_messages(MaxNumberOfMessages=1):
        reserve=message.body
        print(reserve)
        words= message.body.split()
        cuisine=words[0]
        number = words[1]
        receipt_handle = message.receipt_handle
    #cuisine = 'indian'
    #number='+16469751486'
    #number='+17323971296'


    #Hit the ElasticSearch URL
    PARAMETERS={'q':cuisine,'size':5000}
    r= requests.api.request('GET', url= url, params= PARAMETERS)
    x= json.loads(r.text)
    n=x['hits']['total']
    id=[]
    for i in range(0,n):
        if x['hits']['hits'][i]['_source']['rank']<4:
            id.append(x['hits']['hits'][i]['_id'])

    #Get values from DynamoDb
    db = client.batch_get_item(
    RequestItems={
        'yelp-restaurants2': {
            'Keys': [
                {
                    'id': {
                        'S': id[0]
                    },
                },
                {
                    'id': {
                        'S': id[1]
                    },
                },
                {
                    'id': {
                        'S': id[2]
                    },
                }
            ]
        }
    })
    name=[]
    address=[]
    for i in range(0,3):
        name.append(db['Responses']['yelp-restaurants2'][i]['name']['S'])
        a=db['Responses']['yelp-restaurants2'][i]['location']['S']
        a=a.replace("'", '"')
        a=a.replace("None", '""')
        y = json.loads(a)
        address.append(y['display_address'][0]+', '+y['display_address'][1])
    message='Hello! Here are my '+ cuisine+' restaurant suggestions.\n'
    for i in range(0,3):
        message += "{}. ".format(i+1) +name[i]+" ,located at "+address[i]+"\n"
    print message

    #SNS Part
    sns.publish(PhoneNumber = number, Message=message)
    sqs2.delete_message(
        QueueUrl=queue_url,
        ReceiptHandle=receipt_handle
        )


    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
