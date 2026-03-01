# 📚 DYNAMO


from pollyweb.utils.LOG import LOG

import boto3
from botocore.exceptions import ClientError

from pollyweb.utils.UTILS import UTILS


class DYNAMO_REAL_CLIENT():
    '''👉 Real implementation of Dynamo.'''


    myDynamoClient= None

    @classmethod
    def client(cls):
        '''👉 Returns the Dynamo client.'''
        if not DYNAMO_REAL_CLIENT.myDynamoClient:
            DYNAMO_REAL_CLIENT.myDynamoClient = boto3.client('dynamodb')
        return DYNAMO_REAL_CLIENT.myDynamoClient 


    def __init__(self, client=None) -> None:
        if client:
            DYNAMO_REAL_CLIENT.myDynamoClient = client


    @classmethod
    def GetTableNames(cls) -> list[str]:
        '''👉 List all DynamoDB tables.'''
        LOG.Print(f'🪣 DYNAMO.DEPLOY.GetTableNames()')
        ret = cls.client().list_tables()['TableNames']

        LOG.Print(f'🪣 DYNAMO.DEPLOY.GetTableNames.return: {ret=}')
        return ret
    

    @classmethod
    def GetTableDetails(cls) -> dict[str, dict[str, str]]:
        '''👉 List all DynamoDB tables, including name, status, stram, and ttl.'''
        LOG.Print(f'🪣 DYNAMO.CLIENT.GetTableDetails()')
        ret = cls.client().list_tables()
        tables = []
        for name in ret['TableNames']:
            LOG.Print(f'🪣 DYNAMO.CLIENT.GetTableDetails[{name}]...')
            details = cls.client().describe_table(TableName=name)
            tables.append(details['Table'])
        
        # Return a dictionary with the table name as the key.
        ret = UTILS.DictFromList(tables, key= lambda x: x['TableName'])
        LOG.Print(f'🪣 DYNAMO.DEPLOY.GetTableDetails.return:', ret)
        return ret