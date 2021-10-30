import json
import boto3
import urllib.parse


s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
rekognition = boto3.client('rekognition')



def handler(event, context):

    """
    the function is triggered when new file is uploaded (created) in the bucket and accordingly starts 
    image recognition process and update the dynamodb table with the results of the process    
    """
     

    # create a table object
    table = dynamodb.Table('blobs')
    
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    try:
    
        # get the uploaded object from the event and check for the content type before calling recognition 
        s3_response = s3.get_object(Bucket=bucket, Key=key)
        content_type = s3_response['ContentType']
        print("CONTENT TYPE: " + content_type)
        print("key" + key)
        
        supported_types = ['image/jpeg','image/jpg','image/png']
        error = ''
        rekog_response = {}
        
        if content_type.lower() not in supported_types:
            error = 'the file type {} you uploaded is not supported please upload one of the supported types (image/jpeg,image/jpg,image/png)'.format(content_type)
        else :
            rekog_response = rekognition.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':key}}, MaxLabels=4)
            print(rekog_response)
             
             
        labels = [{label['Name'] : str(round(label['Confidence'],2))} for label in rekog_response['Labels']]
        
        
        #update blob item with results of rekognition
        blobs_upd_resp = table.update_item(
        Key={
            'blob_id': str(key),
        },
        UpdateExpression="set rekog_response=:r, isProcessed=:p,  error_message=:e",
        ExpressionAttributeValues={
            ':r': labels,
            ':p': 'Y',
            ':e': error
        },
        ReturnValues="ALL_NEW"
    )        
    
        print(blobs_upd_resp)
      
    except Exception as e:
        print(e)
        print('Error occured during the process')
        raise e
    
   
    
    

   
