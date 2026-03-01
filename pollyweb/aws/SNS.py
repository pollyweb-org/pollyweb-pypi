# 📚 SNS


from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from pollyweb.utils.LOG import LOG
from SNS_TOPIC import SNS_TOPIC
from pollyweb.utils.STRUCT import STRUCT

import boto3
sns = boto3.client("sns")
sns_client = sns

class SNS(AWS_RESOURCE_POOL[SNS_TOPIC]):
    

    @classmethod
    def RegisterFirebase(cls, 
        name:str, 
        serverKey:str,
        failureFeedbackRoleArn:str = None,
        successFeedbackRoleArn:str = None,
        eventEndpointCreated:str = None,
        eventEndpointDeleted:str = None,
        eventEndpointUpdated:str = None,
        eventDeliveryFailure:str = None
    ):
        ''' 👉 Register a mobile app with the SNS.

        :param name: A name for the SNS platform application
        :param serverKey: Firebase server key obtained from Firebase Console
        :return: Platform application ARN
        '''
        # Create or update the platform application
        response = sns_client.create_platform_application(
            Name=name,
            Platform='GCM',  # GCM is still used for Firebase in AWS SNS API
            Attributes={
                'PlatformCredential': serverKey,
                #'FailureFeedbackRoleArn': failureFeedbackRoleArn,  # Replace with your role ARN
                #'SuccessFeedbackRoleArn': successFeedbackRoleArn,  # Optional, replace with your role ARN if you're using it
                'SuccessFeedbackSampleRate': '100',  # Optional, specify the sample rate for success feedback
                #'EventEndpointCreated': eventEndpointCreated,  # Use for successful delivery notifications (optional)
                #'EventEndpointDeleted': eventEndpointDeleted,  # Use for deleted endpoint notifications (optional)
                #'EventEndpointUpdated': eventEndpointUpdated,  # Use for updated endpoint notifications (optional)
                #'EventDeliveryFailure': eventDeliveryFailure,  # Use this for failure feedback
            })
        
        # Retrieve and print the platform application ARN
        platform_application_arn = response['PlatformApplicationArn']
        LOG.Print(f"Platform Application ARN: {platform_application_arn}")

        return platform_application_arn


    @classmethod
    def SendToPush(cls, engine, tokenID, data):
        return True
    

    @classmethod
    def CreateTopic(cls, name:str):
        '''👉️ Creates a topic.'''
        LOG.Print(f"Creating topic: {name}")
        response = sns.create_topic(Name=name)
        topicArn = response['TopicArn']
        LOG.Print(f"Topic ARN: {topicArn}")
        return topicArn
    





    @classmethod
    def Ensure(cls, 
        name:str
    ):
        return super()._Ensure(
            name= name)
    

    @classmethod
    def List(cls, 
        client= None
    ) -> list[SNS_TOPIC]:
        '''👉️ List all topics.'''
        LOG.Print(f'@')

        if client == None:
            client = sns

        # List all SNS topics
        response = STRUCT(client.list_topics())
        ret:list[SNS_TOPIC] = []

        LOG.Print(f'@', response)

        for topic in response.RequireList('Topics'):
            item = SNS_TOPIC(
                pool= cls,
                meta= topic,
                client= client)
            ret.append(item)

        return ret


    @classmethod
    def Create(cls, 
        name:str
    ) -> SNS_TOPIC:
        '''👉️ Create a topic'''

        LOG.Print(f'@: {name=}')

        # Create the queue
        response = sns.create_topic(
            Name= name)
        
        # Return the queue
        return SNS_TOPIC(
            meta= response,
            pool= cls,
            client= sns)