from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RETRY import RetryWithBackoff
from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from pollyweb.utils.LOG import LOG
from pollyweb.utils.PRINTABLE import PRINTABLE
from SNS_TOPIC import SNS_TOPIC
from pollyweb.utils.STRUCT import STRUCT

import json

import boto3
sqs = boto3.client("sqs")

class SQS_QUEUE(AWS_RESOURCE_ITEM):
    
    
    def __init__(self, 
        pool,
        meta:str, 
        client
    ) -> None:
        '''👉️ Initializes.'''
        
        struct = STRUCT(meta)

        self.Url = struct.RequireStr('QueueUrl')
        ''' The URL of the queue. 
        e.g.: https://sqs.us-west-2.amazonaws.com/997532394226/rteasd
        '''

        self.Name = self.Url.split('/')[-1]
        self.Region = self.Url.split('.')[1]
        self.AccoundId = self.Url.split('/')[-2]
        
        self.Arn = f'arn:aws:sqs:{self.Region}:{self.AccoundId}:{self.Name}'
        
        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool, 
            client= client,
            arn= self.Arn,
            name= self.Name)     

        # Override to add the other properties.
        PRINTABLE.__init__(self, lambda: {
            'Arn': self.Arn,
            'Name': self.Name,
            'Url': self.Url,
            'Region': self.Region,
            'AccountId': self.AccoundId
        })

        LOG.Print(f'@', self)
   

    def _Delete(self):
        '''👉️ Delete the queue.'''
        LOG.Print(f'@ URL={self.Url}', self)
        sqs.delete_queue(QueueUrl= self.Url)
                
               
    def Send(self, msg):
        ''' 👉 Sends a message to the SQS Queue. '''
        body= msg
        if isinstance(msg, STRUCT):
            body= msg.Obj()
            
        resp = sqs.send_message(
            QueueName= self.Url,
            MessageBody= json.dumps(body))
        
        code = resp['ResponseMetadata']['HTTPStatusCode']
        if code != 200:
            LOG.RaiseException('Error sending to the queue.')
        return resp
    

    def Exists(self):
        '''👉️ Returns True if the queue exists.'''
        # Overide the default Exists method, because it has cache.
        try:
            sqs.get_queue_url(QueueName= self.Name)
            return True
            
        except Exception as e:
            if 'NonExistentQueue' in str(e):
                return False
            raise
    

    def SubscribeSnsTopic(self, topic: SNS_TOPIC):
        '''👉️ Subscribes to the topic.'''

        LOG.Print(self.SubscribeSnsTopic, 
            topic, self)

        return topic.Subscribe(
            protocol= 'sqs',
            endpoint= self.Arn)
    

    def TriggerLambda(self, 
        fn: LAMBDA_FUNCTION_REAL,
        batchSize: int= 1
    ) -> None:
        '''👉️ Triggers the lambda.'''
        LOG.Print(self.TriggerLambda, fn, self)

        # Map the event source.
        fn.AddEventSource(
            sourceArn= self.Arn,
            batchSize= batchSize)
        
        