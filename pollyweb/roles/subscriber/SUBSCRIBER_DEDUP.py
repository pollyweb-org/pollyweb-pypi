# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.AWS import AWS
from UPDATE import UPDATE
from MSG import MSG
from PW_AWS.ITEM import ITEM


# ✅ DONE
class SUBSCRIBER_DEDUP(ITEM):
    ''' 🪣 https://quip.com/9ab7AO56kkxY#temp:C:ISd04f7e560d00b442f9efed03f1
    {
        "Publisher": "any.publisher.com",
        "UpdateID": "8e8cb55b-55a8-49a5-9f80-439138e340a2", 
        "Domain": "example.com",
        "SentAt": "2018-12-10T13:45:00.000Z",
        "TTL": "2018-12-12T00:00:00.000Z"
    }
    '''

    @classmethod
    def _table(cls):
        return AWS.DYNAMO('DEDUPS', keys=['Domain', 'Correlation'])
    

    @classmethod
    def Upsert(cls, msg:MSG) -> bool:
        '''👉 Inserts of updates the record, returning True if it was saved to DynamoDB.'''

        msg.VerifyHeader()

        update = UPDATE.FromMsg(msg)
        update.GetAtt('Publisher', set=msg.RequireFrom())
        update.Verify()
        
        if cls._table().GetItem(update).IsMissingOrEmpty():
            cls._table().Upsert(update, days=1)
            return True
        else:
            return False


    @staticmethod
    def Stream(event:any) -> list[SUBSCRIBER_DEDUP]:
        ##LOG.Print(f'SUBSCRIBER_DEDUP.Stream({event=})')
        return [
            SUBSCRIBER_DEDUP(struct)
            for struct in AWS.DYNAMO().ParseStream(event)
        ]
        
            
    def RequireDomain(self) -> str:
        return self.RequireStr('Domain')