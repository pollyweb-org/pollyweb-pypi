# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

import json
from typing import Union

from pollyweb import UTILS
from PW_AWS.ITEM import ITEM
from MSG import MSG
from PW_AWS.AWS import AWS


class PUBLISHER_TOKEN(ITEM):    
    ''' 🪣 https://quip.com/sBavA8QtRpXu#temp:C:IEK3e519726b3b04dedbfbcb11e4 
    {
        "ID": "61738d50-d507-42ff-ae87-48d8b9bb0e5a",
        "LastEvaluatedKey": "{\"ID\": \"any-domain.com\"}",
        "SentAt": "2000-01-01T00:00:00.000Z",
        "Domain": "subscriber.com"
    }
    '''


    @staticmethod
    def _table():
        return AWS.DYNAMO('TOKENS')
    

    @staticmethod
    def RequireToken(msg:MSG) -> PUBLISHER_TOKEN:
        '''👉 Gets the token from table and checks if it belongs to the calling domain.'''
        table = PUBLISHER_TOKEN._table()
        
        item = table.Require(msg.RequireStr('Token'))
        
        # Check if the token belongs to this domain.
        token = PUBLISHER_TOKEN(item)
        token.MatchDomain(msg.RequireFrom())

        return token
    
    
    @staticmethod
    def Insert(lastEvaluatedKey:dict, timestamp:str, domain:str) -> PUBLISHER_TOKEN:

        UTILS.RequireArgs([lastEvaluatedKey, timestamp, domain])
        UTILS.ParseTimestamp(timestamp)

        self = PUBLISHER_TOKEN()

        self.Obj({
            'ID': UTILS.UUID(),
            'LastEvaluatedKey': json.dumps(lastEvaluatedKey),
            'SentAt': timestamp,
            'Domain': domain
        })

        return self
        
    

    def LastEvaluatedKey(self) -> any:
        return json.loads(self.RequireAtt('LastEvaluatedKey'))


    def GetTimestamp(self) -> str:
        return self.RequireTimestamp('SentAt')


    def MatchDomain(self, domain:str):
        self.Match('Domain', domain)
    