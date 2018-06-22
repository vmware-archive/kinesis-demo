import json
import boto3

access_key=""
secret_key=""

def tweets_processor(event, context):

    tweet = event['data']
    print tweet

    # we found a tweet that is of interest push the record to SNS for mobile notification
    client = boto3.client('sns', 
                           region_name='eu-west-1',
                           aws_access_key_id=access_key,
                           aws_secret_access_key=secret_key)
    response = client.publish(TargetArn="arn:aws:sns:eu-west-1:587264368683:kubeless-tweets", Message=json.dumps({'default': json.dumps(tweet)}),MessageStructure='json')
    return