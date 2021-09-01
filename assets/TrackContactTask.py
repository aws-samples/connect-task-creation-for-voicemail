import json
from pprint import pprint
import boto3

def lambda_handler(event, context):
    put_contactID(event['Details']['Parameters']['ContactID'],'false',event['Details']['Parameters']['ANI'],event['Details']['Parameters']['EmpID'])


def put_contactID(ContactID, isTaskCreated, ANI, EmployeeID, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('TrackingTask')
    response = table.put_item(
        Item={
            'ContactID': ContactID,
            'isTaskCreated': isTaskCreated,
            'ANI' : ANI,
            'EmployeeID' :EmployeeID
        }
    )
    print(response)
    return response