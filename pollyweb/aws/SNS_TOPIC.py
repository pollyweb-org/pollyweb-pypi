from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT

import boto3
sns = boto3.client("sns")


class SNS_TOPIC(AWS_RESOURCE_ITEM):
    
    def __init__(self, 
        pool,
        meta:dict, 
        client
    ) -> None:
        '''👉️ Initializes.'''
        
        struct = STRUCT(meta)
        self.Arn = struct.RequireStr('TopicArn')
        self.Name = self.Arn.split(':')[-1]

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool, 
            client= client,
            arn= self.Arn,
            name= self.Name)        
        

    def _Delete(self):
        '''👉️ Delete the queue.'''
        LOG.Print(f'@ URL={self.Arn}', self)
        sns.delete_topic(TopicArn= self.Arn)


    def Subscribe(self, protocol:str, endpoint:str):
        '''👉️ Subscribes to the topic.'''

        LOG.Print(f'@ Protocol={protocol}, Endpoint={endpoint}', 
            f'{protocol=}', f'{endpoint=}', self)

        if protocol not in ['lambda', 'sqs', 'sms', 'email']:
            LOG.RaiseException(f'Invalid protocol: {protocol}')

        resp = sns.subscribe(
            TopicArn= self.Arn,
            Protocol= protocol,
            Endpoint= endpoint)
        
        code = resp['ResponseMetadata']['HTTPStatusCode']
        if code != 200:
            LOG.RaiseException('Error subscribing to the topic.')

        return resp