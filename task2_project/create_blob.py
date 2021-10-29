import json
import boto3
import uuid
import os 
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')
s3res = boto3.resource("s3")

def handler(event, context):
    """
    the function  receive requests from clients to create new image item in blobs table 
    and generate presigned url from s3 bucket to be passed back to the client  
    """
     
     
     # global variables
    callback_url = ''
    file_name = ''
    error_message= ''
    presigned_upload_url = ''
    jpg_presigned_upload_url = ''
    png_presigned_upload_url =''
    
    try :
    
        bucket_name = os.environ.get('bucketName')          
        
        # create a table object
        table = dynamodb.Table('blobs')
            
        # generate unique id for the new blob item
        id = str(uuid.uuid4())[-11:]
        
       
        
        #check if the client has provided a callback url
        if 'callback_url' in event['body']:
            callback_url = event['body']['callback_url']
        print(event['body'])    
        
        # in case the design gets the filename before the request and put in the body   
        if 'file_name' in event['body'] and event['body']['file_name'] != '':
            print(event['body']['file_name'])
            file_name = event['body']['file_name']
            name, extension = os.path.splitext(file_name)
            supported_types = ['jpeg','jpg','png']
            print(extension)
            extension = extension.replace('.','').lower()
            if extension not in supported_types :
                error_message = 'the file type {} you provided is not supported please upload one of the supported types (image/jpeg,image/jpg,image/png) please retry with a supported file type'.format(extension)
                print(error_message + extension.lower())
            else :
                
                # create a new item in the blobs table with the optional callback url
                response = table.put_item(
                    Item={
                        'blob_id': id,
                        'callback_url': callback_url
                    
                            }
                        )
                #generate a presigned url for uploading  
                if extension == 'jpg':
                    extension = 'jpeg'
                content_type = 'image/' + extension   
                print(content_type)    
                presigned_upload_url = s3.generate_presigned_url('put_object',Params={
                        'Bucket': bucket_name,
                        #blob-upload-image
                        
                        'Key': id,
                        'ContentType': content_type
                        },
                        ExpiresIn=3600)
                
                    
            
        elif file_name == '' :    
        # generate a url for both cases and provide them both to the client
        # create a new item in the blobs table with the optional callback url
            response = table.put_item(
                Item={
                    'blob_id': id,
                    'callback_url': callback_url
                
                        }
                    )
            #generate a presigned url for uploading a JPG ,JPEG files formats        
            jpg_presigned_upload_url = s3.generate_presigned_url('put_object',Params={
                    'Bucket': bucket_name,
                    #blob-upload-image
                    
                    'Key': id,
                    'ContentType': 'image/jpeg'
                    },
                    ExpiresIn=3600)
            #generate a presigned url for uploading a PNG files formats                  
            png_presigned_upload_url = s3.generate_presigned_url('put_object',Params={
                    'Bucket': bucket_name,
                    #blob-upload-image
                    
                    'Key': id,
                    'ContentType': 'image/png'},
                    ExpiresIn=3600)        
                        
    except Exception as e:
        print(e)
        print('Error occured during the process')
        raise e
                
    body = {
        "presigned_upload_url" : presigned_upload_url ,   
        "jpg_presigned_upload_url" : jpg_presigned_upload_url,
        "png_presigned_upload_url" : png_presigned_upload_url,
         "error_message" : error_message
       
    }
    
    response = {
        "statusCode": 200,
        "body": json.dumps(body),
        
        
    }
    
    return response
    """
    return {
        "presigned-url": presigned_upload_url,
        "input": event
    }
    """