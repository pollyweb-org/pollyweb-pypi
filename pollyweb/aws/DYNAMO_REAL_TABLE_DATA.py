# 📚 DYNAMO

from DYNAMO_BASE import DYNAMO_BASE_TABLE
from LOG import LOG


class DYNAMO_REAL_TABLE_DATA(DYNAMO_BASE_TABLE):
    '''👉 Real implementation of a Dynamo table (data only).'''


    def Name(self) -> str:   
        '''👉 Returns the name of the table.'''
        return self.RequireStr('Name')


    def Table(self) -> str:   
        '''👉 Returns the table resource from boto3.'''
        return self.RequireAtt('Table')


    def __init__(self, alias:str, name:str, table:any) -> None:
        super().__init__(alias=alias)
        self._name = name
        self._table = table
        self.SetAtt('Name', name)
        self.SetAtt('Table', table)


    def query(self, IndexName:str, KeyConditionExpression:str) -> dict[str,any]: 
        resp = self._table.query(
            IndexName= IndexName,
            KeyConditionExpression= KeyConditionExpression)
        
        if 'Items' not in resp:
            LOG.RaiseException('Items is missing from the query response!')
        
        return resp
    

    def update_item(
        self, 
        Key:dict[str,any], 
        UpdateExpression:str, 
        ExpressionAttributeValues:dict,
        ExpressionAttributeNames:dict,
        ConditionExpression:str
    ):
        ''' 👉 https://www.tecracer.com/blog/2021/07/implementing-optimistic-locking-in-dynamodb-with-python.html'''

        self._table.update_item(
            Key = Key, 
            UpdateExpression = UpdateExpression, 
            ExpressionAttributeValues = ExpressionAttributeValues,
            ExpressionAttributeNames = ExpressionAttributeNames,
            ConditionExpression = ConditionExpression)
        

    def get_item(self, Key:dict[str,any]) -> dict[str,any]:
        return self._table.get_item(self, Key=Key)
    

    def delete_item(self, Key:dict[str,any]):
        return self._table.delete_item(self, Key=Key)
    

    def scan(
        self, 
        IndexName:str=None, 
        ExclusiveStartKey:dict[str,any]=None,
        FilterExpression:str=None,
        TimestampColumn:str= 'Timestamp'
    ) -> dict[str, any]:
        
        return self._table.scan(
            IndexName= IndexName,
            ExclusiveStartKey= ExclusiveStartKey,
            FilterExpression= FilterExpression)
    

