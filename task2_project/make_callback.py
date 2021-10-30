import json
from requests import post

def handler(event, context):
    """
    get the results of recognition job and depending on the status of the job
    callback the client with the results..
    """  
    try:    
        for record in event['Records']:
            #check that the event is modify and not insert to be sure that the recognition job has been ended 
            if record['eventName'] == 'MODIFY' :
                
                print(record['dynamodb']['NewImage'])
                if record['dynamodb']['NewImage'] is not None:
                    callback_url = ''
                    
                    #check the existence of callback url 
                    if 'callback_url' in record['dynamodb']['NewImage']:
                        callback_url = record['dynamodb']['NewImage']['callback_url']['S']
                    payload = {}
                    
                #if the the job has not finished successfully send and error message to the client
                    if record['dynamodb']['NewImage']['isProcessed']['S'] == 'N' and callback_url != '':
                        error_message = record['dynamodb']['NewImage']['error_message']['S']
                        print(error_message)
                        payload = {"error_message" : error_message }
                        call_back_response = post(callback_url, json=payload) 
                        print(call_back_response)
                    
                    #if the the job has  finished successfully send the results to the client    
                    elif record['dynamodb']['NewImage']['isProcessed']['S'] == 'Y' and callback_url != '' :
                        
                        labels = record['dynamodb']['NewImage']['rekog_response']['L']
                        for label in labels:
                            for key, value in label['M'].items():
                                payload[key] = value['S']
                        print(payload)
                        call_back_response = post(callback_url, json=payload) 
                        print(call_back_response)
                    
                    #if the client has not provided a callback url will do nothing
                    else :
                        pass
    except Exception as e:
        print(e)
        print('Error occured during the process')
        raise e    
    
    
    
 
   
