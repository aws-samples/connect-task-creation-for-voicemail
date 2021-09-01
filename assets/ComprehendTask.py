from pprint import pprint
import boto3
import os
 
def lambda_handler(event, context):
    
    contactID = event['Records'][0]['dynamodb']['NewImage']['contactId']['S'];
    eventName=event['Records'][0]['eventName'];
    #create_presigned_url('ac-kinesis-video-stream-transcription','recordings/01c1ae2a-b945-42e1-b966-c661222f993e_2020-12-18T19:26:29.032+0000_AUDIO_FROM_CUSTOMER.wav')
    #get_Entities(event['Records'][0]['dynamodb']['NewImage']['contactTranscriptFromCustomer']['S'])
    #if eventName == 'INSERT':
        #put_contactID(contactID, "false")
 
    if eventName == 'MODIFY':
        print('ComprehendMedicalTask() event is: ', event)
        new_image = event['Records'][0]['dynamodb']['NewImage']
        old_image = event['Records'][0]['dynamodb']['OldImage']
        #trigger lambda only once, after combined audio file is created
        #if ( 'combinedAudio' in new_image and 'combinedAudio' not in old_image):
        if ( ('mergeStatus' in new_image) and (new_image['mergeStatus']['S'] == 'Complete') ):
            if ( 'audioFromCustomer' in new_image and 'contactTranscriptFromCustomer' in new_image ):
                contactID = new_image['contactId']['S'];
                responseFromDB = get_isTaskCreated(contactID)
                if responseFromDB['isTaskCreated'] == 'false':
                    urlToRecording = new_image['audioFromCustomer']['S'];
                    contactTranscriptFromCustomer = new_image['contactTranscriptFromCustomer']['S'];
                    #ANI = new_image['customerPhoneNumber']['S']
                    #employID = new_image['']
                    callStartTaskLambda(
                        create_presigned_url('ac-kinesis-video-stream-transcription',split_at(urlToRecording,'/',3)[1]),
                        contactTranscriptFromCustomer,
                        get_Entities(contactTranscriptFromCustomer),
                        get_KeyPhrase(contactTranscriptFromCustomer),
                        responseFromDB['ANI'],
                        responseFromDB['EmployeeID'])
                    update_contactID(contactID,'true')
            else:
                print('ERROR: ComprehendMedicalTask() triggered on MODIFY with missing attributes...DO NOTHING')
        else:
            print('ComprehendMedicalTask() triggered on MODIFY but Contact Summary is NOT done yet...DO NOTHING')
   
def create_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',Params={'Bucket': bucket_name,'Key': object_name},ExpiresIn=expiration)
    print(response)
    return response
 
def split_at(s, delim, n):
    r = s.split(delim, n)[n]
    return s[:-len(r)-len(delim)], r 
    
def get_isTaskCreated(contactID, dynamodb=None):   
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('TrackingTask')
        response = table.get_item(Key={'ContactID': contactID})
        print('get_isTaskCreated() response: ', response['Item'])
    return response['Item']
   
def update_contactID(contactID, isTaskCreated, dynamodb=None):
    print('update_contactID() for contactID: {0} to {1}'.format(contactID, isTaskCreated))
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('TrackingTask')
        response = table.update_item(
            Key= {
            'ContactID':  contactID
            },
            ExpressionAttributeNames= { "#PName": "isTaskCreated" },
        ExpressionAttributeValues= {
            ":PValue":  isTaskCreated
        },
        UpdateExpression= "SET #PName = :PValue",
        ReturnValues= "ALL_NEW"
        )
        print('update_contactID() response from DB is: {}'.format(response))
 
def put_contactID(ContactID, isTaskCreated, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('TrackingTask')
        response = table.put_item(
           Item={
                'ContactID': ContactID,
                'isTaskCreated': isTaskCreated,
            }
        )
        print(response)
    return response
   
 
def get_KeyPhrase(contactTranscriptFromCustomer):
    store_list = []
    client = boto3.client('comprehend')
    response = client.detect_key_phrases(Text=contactTranscriptFromCustomer,LanguageCode='en')
    print (response)
    for item in response['KeyPhrases']:
        store_list.append(item['Text'])
    print(store_list)
    return store_list
   
        
def get_Entities(contactTranscriptFromCustomer):
    store_list = []
    client = boto3.client('comprehendmedical')
    response = client.detect_entities_v2(Text=contactTranscriptFromCustomer)
    for item in response['Entities']:
        if len(item['Traits']) != 0:
            if item['Traits'][0]['Name'] == 'SYMPTOM':
                store_list.append(item['Text'])
    print(store_list)
    print (response)
    return store_list
   
def callStartTaskLambda(urlToRecording,contactTranscriptFromCustomer,entities, keyphrase, ANI, EmployeeID):
    print('callStartTaskLambda() is called')
    print('urlToRecording: {0}, contactTranscriptFromCustomer: {1}, entities: {2}, keyphrase: {3}, ANI: {4}, EmployeeID: {5}'.format(
        urlToRecording, contactTranscriptFromCustomer, entities, keyphrase, ANI, EmployeeID))
        
    client = boto3.client('lambda')
    
    taskReferences = {
        'urlToRecording': {
            'Value': urlToRecording,
            'Type': 'URL'
        }
    }
    
    symptoms = ''
    if len(entities) == 0:
        #make sure we dont pass '' to Task, which would be bad parameter
        symptoms = 'NONE'
    else:
        symptoms = ' '.join(entities)
        """
        for  entity in entities:
            if symptoms == '':
                symptoms = entity
            else:
                symptoms = symptoms + ', ' + entity
        """
    
    keyphrases = ''
    if len(keyphrase) == 0:
        #make sure we dont pass '' to Task, which would be bad parameter
        keyphrases = 'NONE'
    else:
        keyphrases = ' '.join(keyphrase)
        """
        for phrase in keyphrase:
            if (keyphrases == ''):
                keyphrases = phrase
            else:
                keyphrases = keyphrases + ', ' + phrase
        """
    
    taskAttributes = {
        'SYMPTOM': symptoms,
        'KEYPHRASE': keyphrases,
        'ANI': ANI,
        'EmployeeID': EmployeeID
    }
    taskName = 'Task for EmployeeID: {0} with ANI: {1}'.format(EmployeeID, ANI)
    taskDescripton = contactTranscriptFromCustomer
    
    print('taskName is: {}'.format(taskName))
    print('taskAttributes is: {}'.format(taskAttributes))
    print('taskReferences is: {}'.format(taskReferences))
    print('taskDescripton is: {}'.format(taskDescripton))

    connectClient = boto3.client('connect')

    respBody = ''
    
    try:
        response = connectClient.start_task_contact(
            InstanceId = os.environ['INSTANCE_ID'],
            ContactFlowId = os.environ['CONTACT_FLOW_ID'],
            #PreviousContactId = "some-previous-contact-id",
            Attributes = taskAttributes,
            Name = taskName,
            References = taskReferences,
            Description = taskDescripton
            #ClientToken = event['clientToken']
        )
        print('start_task_contact() response is: ', response)
        respBody = response['ContactId']
    except Exception as e:
        print('Exception on start_task_contact: ', e)
        return {
            'statusCode': 500,
            'body': e
        }
        
    return {
        'statusCode': 200,
        'body': {'ContactId': respBody}
    }
    #responseFromChild = json.load(response['Payload'])
    #print(responseFromChild)