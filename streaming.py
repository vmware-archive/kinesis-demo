#!/usr/bin/env python

import os
import json

import boto3
import tweepy

consumer_key = os.getenv("consumer_key")
consumer_secret = os.getenv("consumer_secret")

access_token = os.getenv("access_token")
access_token_secret = os.getenv("access_token_secret")

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

kinesis_client = boto3.client('kinesis')

class KinesisStreamProducer(tweepy.StreamListener):
        
    def __init__(self, kinesis_client):
        self.kinesis_client = kinesis_client

    def on_data(self, data):
        tweet = json.loads(data)
        self.kinesis_client.put_record(StreamName='kubeless', Data=tweet["text"], PartitionKey="key")
        print("Publishing record to the stream: ", tweet)
        return True
        
    def on_error(self, status):
        print("Error: " + str(status))

def main():
    mylistener = KinesisStreamProducer(kinesis_client)
    myStream = tweepy.Stream(auth = auth, listener = mylistener)
    myStream.filter(track=['#kubelessonaws'])

if __name__ == "__main__":
    main()

