# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from MSG import MSG
from PW_AWS.ITEM import ITEM
from PW_AWS.AWS import AWS
from pollyweb import UTILS


class PUBLISHER_SUBSCRIBER(ITEM):    
    ''' 🪣 https://quip.com/sBavA8QtRpXu#temp:C:IEKc08ac410e2ed414780eb190c8
    {
        "ID": "any-domain.com",
        "Filter": {}
    }'''
    

    @classmethod
    def _table(cls):
        return AWS.DYNAMO('SUBSCRIBERS')
    

    @classmethod
    def New(cls, domain:str, filter:dict):
        item = {
            "ID": domain,
            "Filter": filter
        }
        return item
    

    @staticmethod
    def RequireSubscriber(msg:MSG) -> PUBLISHER_SUBSCRIBER:
        domain = msg.RequireFrom()
        item = PUBLISHER_SUBSCRIBER._table().Require(domain)
        return PUBLISHER_SUBSCRIBER(item)
    

    @classmethod
    def AllSubscribers(cls) -> list[PUBLISHER_SUBSCRIBER]:
        table = PUBLISHER_SUBSCRIBER._table()
        return [
            PUBLISHER_SUBSCRIBER(s) 
            for s in table.GetAll()
        ]
    

    @classmethod
    def Upsert(cls, msg:MSG):
        ''' 👉 Inserts or updates a domain. '''

        filter = msg.GetStruct('Filter', default={})

        subscriber = cls.New(
            domain= msg.RequireFrom(),
            filter= filter)
        
        PUBLISHER_SUBSCRIBER._table().Upsert(subscriber)
    

    def Domain(self) -> str:
        return self.RequireID()
    