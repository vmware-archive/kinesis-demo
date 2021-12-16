## WARNING: Kubeless is no longer actively maintained by VMware.

VMware has made the difficult decision to stop driving this project and therefore we will no longer actively respond to issues or pull requests. If you would like to take over maintaining this project independently from VMware, please let us know so we can add a link to your forked project here.

Thank You.

# AWS Kinesis streams as Kubeless trigger

Kubeless is a Kubernetes-native FaaS framework that lets you deploy functions without having to worry about the underlying infrastructure used for executing them. It is designed to be deployed on top of a Kubernetes cluster and take advantage of all the great Kubernetes primitives. Kubeless is built around the core concepts of functions, triggers, and runtimes. Triggers in Kubeless represent the event sources and associated functions to be executed on occurence of an event from a given event source. Kubeless supports a wide variety of event sources including AWS [Kinesis](https://aws.amazon.com/kinesis/) streams

Amazon Kinesis is a fully-managed streaming data service that makes it easy to collect, process, and analyze real-time, streaming data; it offers key capabilities to cost-effectively process streaming data at any scale. The unit of data stored by Kinesis Data Streams is a data record: a stream represents a group of data records. You can deploy functions in Kubeless and associate with an AWS Kinesis stream. Kubeless will run the functions in response to records being published to a Kinesis stream.

In the subsequent sections we will go through setting up Kubeless and enabling support for Kinesis stream as Kubeless trigger. We will go over steps to deploy a function in Kubeless that will be triggered in response to the records published to an AWS Kinesis stream.

## Example Scenario

Lets consider a real life scenario to illustrate the end-to-end picture and help you appreciate the power of Kinesis and Kubeless.

We will a use a social network feed to get real-time insights, in this example all the tweets being produced during the Kubecon conference. We will run through a scenario where we would like to get real-time notification of the mention of a topic of interest: kubeless :)

Lets see how to build a data processing pipeline by deploying Kubeless functions that are executed when records appear in an Amazon Kinesis stream.

## Setup Kubeless

Please follow the [installation steps](https://github.com/kubeless/kubeless/blob/master/docs/quick-start.md#installation) in the Kubeless quick start quide to deploy Kubeless on a functional Kubernetes cluster.

Once you have a working Kubeless setup please follow the [instructions](https://github.com/kubeless/kubeless/blob/master/docs/streaming-functions.md#aws-kinesis) to setup Kinesis trigger setup in Kubeless

## Setup a Kinesis Stream

Lets start by creating a Kinesis stream using the AWS web console to a create a data stream named `KubelessDemo`.

![Create Kinesis Strea,](./img/create-stream.png)

The snapshot above comes directly from the AWS management console. As you can see, there is very little configuration needed to get started with a stream.

## Settingup Data Producer

Now that we have a Kinesis stream to take the data in, we will use a simple Python program [streaming.py](https://github.com/kubeless/kinesis-demo/blob/master/streaming.py) that uses [boto3](https://github.com/boto/boto3) and [tweepy](https://github.com/tweepy/tweepy) to fetch in real time tweets with the hashtag #kubecon, and ingest the data into the KubelessDemo Kinesis stream. Run the following Python script locally:

```
$ python ./streaming.py
```

Script when run requests twitter API to notify for tweets that contain the hashtag `#kubelessonaws`. When twitter API notifies a tweet script pushes the data into `KubelessDemo` Kinesis stream

## Deploying the function

Now that we have a producer of data to fill up our Kinesis stream, lets deploy Kubeless function that sends an SNS mobile notification when the keyword “kubeless” appears in a tweet. To do we will use simple Python script [sns.py](https://github.com/kubeless/kinesis-demo/blob/master/sns.py) below and we deploy it as Kubeless function using Kubeless CLI.

```
kubeless function deploy tweets  --runtime python2.7 \
                                                     --handler sns.tweets_processor \
                                                     --from-file sns.py \
                                                     --dependencies requirements.txt
```

## Associating Kinesis stream as trigger

Now that the Kubeless function to push the tweet to SNS is deployed into Kubeless we need to associate Kinesis stream that we created as event source to trigger the function invocation.

First, Kubeless needs to be able poll the Kinesis stream to fetch the records. To do this, Kubeless need access to AWS credentials. Kubeless uses Kubenetes secrets to store AWS keys. Lets create a Kubernetes secret to store AWS access and secret keys from a user that has access to our Kinesis stream:

```
kubectl create secret generic ec2 \
--from-literal=aws_access_key_id=$AWS_ACCESS_KEY_ID \
--from-literal=aws_secret_access_key=$AWS_SECRET_ACCESS_KEY
```

Now that the function is deployed into Kubeless and a secret is available with AWS credential, Lets set up the Kinesis trigger that associates the deployed function with the KubelessDemo Kinesis stream that we created earlier. The Kubeless CLI has a subcommand kubeless trigger kinesis to do just that. Below is CLI command to create and associate a Kinesis trigger with deployed function:

```
kubeless trigger kinesis create kinesis-trigger --function-name tweets\
                                                                         --aws-region us-west-2 \
                                                                         --shard-id shardId-000000000000 \
                                                                         --stream KubelessDemo \
                                                                         --secret ec2
```

## See it in action

That’s it! At this point Kubeless will start polling for records in the Kinesis stream. When there are records to be processed, Kubeless will invoke the associated Kubeless functions. Kubeless will automatically scale up or scale down the resources it consumes (Kubernetes pods) as necessary to process the records in the stream.

The Python script filtering the Twitter stream, looking for #kubelessonaws, will push the tweet to Kinesis.


