import json
import boto3
import os
import io
import logging
import matplotlib.pyplot as plt
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from botocore.exceptions import ClientError

print('Loading function')


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    result= ""
    SENDER = "chenfeng@wustl.edu"
    logger.info('## ENVIRONMENT VARIABLES')
    logger.info(os.environ)
    logger.info('## EVENT')
    logger.info(event)
    logger.info('## RESULT')
    logger.info(result)
    SENDER= "chenfeng@wustl.edu"
    newData = event['Records'][0]['dynamodb']['NewImage']['Payload']['M']['state']['M']['reported']['M']['state']['M']
    list0=[]
    list1=[]
    list2=[]
    list3=[]
    list4=[]
    for item in newData:
        newItem = newData[item]
        for nextItem in newItem["L"]:
            if(len(list0)==min(len(list0),len(list1),len(list2),len(list3),len(list4))):
                list0.append(nextItem['N'])
            elif(len(list1)==min(len(list0),len(list1),len(list2),len(list3),len(list4))):
               list1.append(nextItem['S'])
            elif(len(list2)==min(len(list0),len(list1),len(list2),len(list3),len(list4))):
               list2.append(nextItem['S'])
            elif(len(list3)==min(len(list0),len(list1),len(list2),len(list3),len(list4))):
               list3.append(nextItem['S'])
            elif(len(list4)==min(len(list0),len(list1),len(list2),len(list3),len(list4))):
               list4.append(nextItem['S'])
    plt.plot(list0,list1)
    plt.xlabel('time')
    plt.ylabel('movement reading')
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('analysisbucket33333')
    bucket.put_object(Body=img_data, ContentType='image/png', Key='image/1.png')
    plt.plot(list0,list2)
    plt.xlabel('time')
    plt.ylabel('movement reading')
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('analysisbucket33333')
    bucket.put_object(Body=img_data, ContentType='image/png', Key='image/2.png')
    plt.plot(list0,list3)
    plt.xlabel('time')
    plt.ylabel('movement reading')
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('analysisbucket33333')
    bucket.put_object(Body=img_data, ContentType='image/png', Key='image/2.png')
    plt.plot(list0,list4)
    plt.xlabel('time')
    plt.ylabel('movement reading')
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('analysisbucket33333')
    bucket.put_object(Body=img_data, ContentType='image/png', Key='image/2.png')
    object_acl = s3.ObjectAcl('analysisbucket33333','image/2.png')
    response = object_acl.put(ACL='public-read')
    plt.close()
    # Replace recipient@example.com with a "To" address. If your account 
    # is still in the sandbox, this address must be verified.
    RECIPIENT = "kevin.vancleave@wustl.edu"
    
    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"
    
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-west-2"
    
    # The subject line for the email.
    SUBJECT = "Your Action report with " + str(len(list0)) + " datapoints" 
    
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = result
                
    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>https://analysisbucket33333.s3-us-west-2.amazonaws.com/image/2.png
    </body>
    </html>
                """            
    
    # The character encoding for the email.
    CHARSET = "UTF-8"
    
    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)
    
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
    return 'Successfully processed {} records.'.format(len(event['Records']))