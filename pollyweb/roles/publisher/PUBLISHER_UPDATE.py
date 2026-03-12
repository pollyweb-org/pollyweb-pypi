# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations


from pollyweb import UTILS
from MSG import MSG
from PW_AWS.ITEM import ITEM
from PW_AWS.AWS import AWS



class PUBLISHER_UPDATE(ITEM):    
    ''' 🪣 https://quip.com/sBavA8QtRpXu#temp:C:IEKd7992eec103b489a81b2576ca
    {
        "ID": "8e8cb55b-55a8-49a5-9f80-439138e340a2", 
        "Domain": "example.com",
        "SentAt": "2018-12-10T13:45:00.000Z",
        "Correlation": "125a5c75-cb72-43d2-9695-37026dfcaa48"
    }'''


    @staticmethod
    def _table():
        return AWS.DYNAMO('UPDATES')

    
    def New(self, msg:MSG) -> PUBLISHER_UPDATE:
        self.Obj({
            'ID': UTILS.UUID(),
            'Domain': msg.RequireFrom(),
            'SentAt': msg.GetTimestamp(),
            'Correlation': msg.RequireCorrelation()
        })
        return self
    

    @staticmethod
    def Insert(update:any):
        PUBLISHER_UPDATE._table().Insert(update)
    

    def UpdateID(self):
        return self.RequireID()
    

    def Domain(self):
        return self.RequireStr('Domain')
    

    def GetTimestamp(self):
        return self.RequireTimestamp('SentAt')