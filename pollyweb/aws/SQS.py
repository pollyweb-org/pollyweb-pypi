# 📚 SQS

from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from AWS_RETRY import RetryWithBackoff
from PW_UTILS.LOG import LOG
from SQS_QUEUE import SQS_QUEUE

import boto3

from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS
sqs = boto3.client("sqs")

class SQS(AWS_RESOURCE_POOL[SQS_QUEUE]):

    
    def IsSqsEvent(self, obj:any):
        ''' 👉 Indicates if the object is an SQS response.'''
        if obj == None:
            return False
        if 'Messages' in obj and 'ResponseMetadata' in obj:
            return True
        return False
    
    
    def ParseMessages(self, obj: any) -> list:
        ''' 👉 Returns the messages inside an SQS response.
        👉 https://stackoverflow.com/questions/58191688/how-to-parse-sqs-json-message-with-python
        {
            'Messages': [
                {
                    'MessageId': '37b13967-a92e-4b8b-8aef-32341a8e1e32',
                    'ReceiptHandle': 'xyz',
                    'MD5OfBody': '081f4bdad6fd3d53c88f165a884a39da',
                    'Body': '{"inputIDList":["1234","5678"],"eventID":"9337","scheduleEvent":false,"addToList":true,"listID":"7654","clientID":"123-ABC-456"}'
                }
            ],
            'ResponseMetadata': {
                'RequestId': '79dafe96-04d9-5122-8b2a-a89b79a76a46',
                'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'x-amzn-requestid': '79dafe96-04d9-5122-8b2a-a89b79a76a46',
                    'date': 'Tue, 01 Oct 2019 16:13:50 GMT',
                    'content-type': 'text/xml',
                    'content-length': '4792'
                },
                'RetryAttempts': 0
            }
        }
        '''

        if not self.IsSqsEvent(obj):
            return []

        ret = []
        for msg in ret['Messages']:
            body = self.FromJson(msg['Body'])
            ret.append(body)

        return ret
    

    @classmethod
    def Get(cls, 
        name:str,
        client= None,
        resource= None
    ) -> SQS_QUEUE:
        '''👉️ Returns a resource by name.'''

        LOG.Print(f'@: {name=}')

        # Validate the Queue name.
        UTILS.RequireString(name)
        if '.' in name:
            LOG.RaiseValidationException(
                f'A queue name cannot have a dot: {name}')
            
        try:
            resp = sqs.get_queue_url(QueueName= name)
            return SQS_QUEUE(
                pool= cls,
                meta= resp,
                client= sqs)
            
        except Exception as e:
            if 'NonExistentQueue' in str(e):
                LOG.Print(f'@: get_queue_url raised NonExistentQueue for {name=}')
                return None
            raise


    @classmethod
    def Ensure(cls, 
        name:str
    ):
        return super()._Ensure(
            name= name)
    

    @classmethod
    def List(cls, 
        client= None
    ) -> list[SQS_QUEUE]:
        '''👉️ List all queues.'''

        LOG.Print(f'@')

        if client == None:
            client = sqs

        # List all SQS queues
        response = STRUCT(client.list_queues(MaxResults=1000))
        ret:list[SQS_QUEUE] = []

        LOG.Print(f'@', response)

        for queue in response.ListStr('QueueUrls'):
            item = SQS_QUEUE(
                pool= cls,
                meta= { 'QueueUrl': queue },
                client= client)
            ret.append(item)

        return ret


    @classmethod
    @RetryWithBackoff(
        maxRetries=20, 
        initialDelay=0.1, 
        codes=['QueueDeletedRecently'])
    def Create(cls, 
        name:str
    ) -> SQS_QUEUE:
        '''👉️ Create a queue'''

        LOG.Print(f'@: {name=}')

        # Create the queue
        response = sqs.create_queue(
            QueueName= name)
        
        # Return the queue
        return SQS_QUEUE(
            meta= response,
            pool= cls,
            client= sqs)
    

    