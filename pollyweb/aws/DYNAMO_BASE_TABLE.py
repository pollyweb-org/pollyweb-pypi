# 📚 DYNAMO

from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT


class DYNAMO_BASE_TABLE(STRUCT):
    '''👉 Interface for a Dynamo table.'''

    ICON = '🪣'


    def RequireAlias(self) -> str:
        '''👉 Returns the alias.'''
        return self.RequireStr('Alias')

        

    def __init__(self, alias) -> None:
        super().__init__({
            'Alias': alias
        })
        self._alias = alias
        

    def query(self, IndexName:str, KeyConditionExpression:str) -> dict[str,any]: 
        '''👉 Returns a subset of items.
        * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/query.html
        '''
        LOG.RaiseException('Please override!')
    

    def update_item(
            self, 
            Key:dict[str,any], 
            UpdateExpression:str, 
            ExpressionAttributeValues:dict,
            ExpressionAttributeNames:dict,
            ConditionExpression:str) -> None:
        '''👉 Updates a table item.
        * https://www.tecracer.com/blog/2021/07/implementing-optimistic-locking-in-dynamodb-with-python.html
        * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/update_item.html
        '''
        LOG.RaiseException('Please override!')
    

    def get_item(self, Key:dict[str,any]):
        '''👉 Returns an item.
        * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/get_item.html
        * https://www.fernandomc.com/posts/ten-examples-of-getting-data-from-dynamodb-with-python-and-boto3/
        '''
        LOG.RaiseException('Please override!')
    
    
    def delete_item(self, Key:dict[str,any]) -> dict[str,dict[str,any]]:
        '''👉 Deletes and returns {ResponseMetadata:{HTTPStatusCode}}'''
        LOG.RaiseException('Please override!')
    

    def scan(
        self, 
        IndexName:str= None, 
        ExclusiveStartKey:dict[str,any]= None,
        FilterExpression:str= None,
        TimestampColumn:str= 'Timestamp'
    ) -> dict[str, any]:
        '''👉 Scans and returns {Items:[], LastEvaluatedKey}
        * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html
        '''
        LOG.RaiseException('Please override!')
    


    def OnStream(self, event) -> None:
        '''👉 Placeholder for a streaming event'''
        pass

