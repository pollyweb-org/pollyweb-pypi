# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from UPDATE import UPDATE
from MSG import MSG
from PW_AWS.ITEM import ITEM
from PUBLISHER_UPDATE import PUBLISHER_UPDATE
from PW_AWS.AWS import AWS


class PUBLISHER_DOMAIN(ITEM):
    ''' Used for replays

    Properties:
    * ID: the domain name.
    * UpdateID: ID of the last update to the domain.
    * Timestamp: the moment of the last update to the domain.

    Example:
    {
        "ID": "any-domain.com",
        "SentAt": "2018-12-10T13:45:00.000Z",
        "UpdateID": <uuid>,
        "Correlation": <uuid>
    }'''


    @staticmethod
    def _table():
        return AWS.DYNAMO('DOMAINS')
    

    @staticmethod
    def GetDomain(msg:MSG) -> PUBLISHER_DOMAIN:
        domain = msg.RequireFrom()
        item = PUBLISHER_DOMAIN._table().GetItem(domain)
        # Note: don't verify existance.
        return PUBLISHER_DOMAIN(item)
    
    
    @staticmethod
    def Upsert(update:PUBLISHER_UPDATE) -> PUBLISHER_DOMAIN:
        '''👉 Insert or update the domain with the latest UpdateID/Timestamp.'''
        domain = {
            'ID': update.Domain(),
            'UpdateID': update.UpdateID(),
            'SentAt': update.GetTimestamp(),
        }
        PUBLISHER_DOMAIN._table().Upsert(domain)
        return domain


    def GetTimestamp(self) -> str:
        return self.RequireTimestamp('SentAt')
    

    def Domain(self) -> str:
        return self.RequireID()
    

    def UpdateID(self) -> str:
        return self.RequireStr('UpdateID')
    

    def Correlation(self) -> str:
        return self.RequireUUID('Correlation')
    

    def ToUpdate(self) -> UPDATE:
        '''👉 Creates an UPDATE struct from the item.'''
        domain = self
        update = UPDATE.New(
            domain= domain.Domain(),
            updateID= domain.UpdateID(),
            timestamp= domain.GetTimestamp(),
            correlation= domain.Correlation()
        )
        return update
        
    

    @staticmethod
    def GetPageFromTimestamp(
        timestamp:str, 
        exclusiveStartKey:str=None, 
        timestampColumn:str= 'Timestamp'
    ):
        ''' 👉 Returns paginated items from DynamoDB.\n
        Usage:
        * domains, last = ().GetPageFromTimestamp(timestamp, start)
        '''

        ##LOG.Print(f'PUBLISHER.GetPageFromTimestamp(timestamp={timestamp}, exclusiveStartKey={exclusiveStartKey})')
        page = PUBLISHER_DOMAIN._table().GetPageFromTimestamp(
            timestamp= timestamp,
            exclusiveStartKey= exclusiveStartKey,
            timestampColumn= timestampColumn)
        ##LOG.Print(f'PUBLISHER.GetPageFromTimestamp().page={page}')

        lastEvaluatedKey = None
        if 'LastEvaluatedKey' in page:
            lastEvaluatedKey = page['LastEvaluatedKey']

        items = [
            PUBLISHER_DOMAIN(item)
            for item in page['Items']
        ]

        return items, lastEvaluatedKey
        