# Task2 Image Recognition
A project for using AWS AI image recognition service using the API and serverless architecture

1. This project is built, tested and deployed using serverless framework , the project folder is ready for deployment with just
using the "sls deploy" command .

2. the project is composed of 3 Lambda functions .py files and the serverless.yml file with all the required resources .

3. The **resources** are as follows :

 <br/> -- 2 Api Gateway resources endpoints each with a specific method type (POST & GET) 
	 <br/> -- The **POST** method is used to invoke the lambda function 
		 <br/> -- **createBlob** : which is simply responsible for receiving the api request to create a new blob item in "blobs" dynamo db table with new generated blob_id        (primary_key)
			and also the (optional) callback url from the api request body that the client should have already provided if any, also the function 
			call the s3 api "generate_presigned_url" function which generates a url for the client with expiry time to upload their file with the required authorization,
			the function takes the client method which is "put_object" in our case and the method params (the bucket name,file key and content type), and finally return the 
			presigned url to the client .
      
 >  **Important notes here** :  I tried to make this design as flexible as possible so i have deviated slighty in this function from the required design , but still serve the same requirement ,simply the 
 >  S3 api function takes the content type of the upload file ,when tried to not use it and generated the url without it to make the url able to be used for any file type for more flexibility ,the api returned "signature doesn't match error" ,which means the file type is important for the signature ,so used 2 approaches here to overcome this issue ,first gave the client the ability to pass the filename in the request body and from the name  extract the content type and generate the url accordingly ,if the client doesn't manage to pass the filename ,so the second approach will work which will generate 2 urls and pass them back to the client one will serve "(jpeg","jpg") files and the other for "png" files,and after testing all the possible cases with and without the filename and even when passing wrong file type ,the function handles all of them as expected .

-- The **S3 Bucket** to be used as the storage for the upload file and also to trigger lambda function
   <br/> **processBlob** : this function is triggered using the s3 bucket when new object is created in the bucket to start the image recognition job, where the function call the AWS Rekognition service using boto3 "detect_labels" function and get the results and save it in a dictionary and update the blobs dynamo table with the results of the AI service and also put an error message in the table for the client to read it in case of bad file provided,which might not happen because the previous steps will not allow wrong types to be uploaded ,but just to catch any case if the design of the first steps changed and allowed different file types.
   
   -- **The DynamoDb table "blobs"**, which has all the blob items created with their results from recognition job, also this table is used then to trigger a lambda function
      <br/>-- **callbackClient** : this function is triggered using the dynamo table and it handles the output from the job based on the 'isprocessed' attribute in the table                 if it's yes indicating the success of the job , it will send the results of the job to the client in a readable way, if not will send and error message in the                 post request body which will post the those results to the client on the callback url provided by the client from the beginning,and if no url found it will do                 nothing.
      
  -- Finally the **Api endpoint with GET method** ,which will be availablle to the client to request the data of the uploaded item by id from the dynamo db table.
  
  > I have tested all the test cases provided for the task and also tested wrong type files for the cycle starting from requesting a presigned url up to receiving the results on the callback url ,used **Postman** for testing the POST and PUT operations of the file to the bucket and also for the GET request of the blob item from the table ,also used **Pipedream Requestbin** for the callback url setup and testing and receiving the results from lambda function "callbackClient"
   
  > Finally please use the bucket variable when using sls deploy command with some specific bucket name in order to avoid 
    duplication of bucket names in AWS ,i already used a bucket on the serverless template as a default value but you also can 
	override this value using the variable on the cmd example: 
	"sls deploy --bucket custom-bucket-name"
   
  
