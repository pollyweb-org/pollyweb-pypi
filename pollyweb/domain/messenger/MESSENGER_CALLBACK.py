from __future__ import annotations
from PW_AWS.ITEM import ITEM
from pollyweb import UTILS
from PW_AWS.AWS import AWS


class MESSENGER_CALLBACK(ITEM):
    '''
    Example:
        ID: <uuid>,
        Domain: any-vault.org,
        Handler: fnHandler,
        Context: {...}
    '''

    @classmethod
    def _table(cls):
        return AWS.DYNAMO('CALLBACKS')
    

    @classmethod
    def RequireCallback(cls, correlation):
        UTILS.AssertIsUUID(correlation, require=True)
        ret = cls._table().Require(correlation)
        return cls(ret)


    @classmethod 
    def Insert(cls, correlation:str, domain:str, handler:str, context:dict):

        UTILS.RequireArgs([domain])

        # Store to DynamoDB.
        ret = {
            'ID': correlation,
            'Domain': domain,
            'Handler': handler,
            'Context': context
        }

        # Store for a day.
        ret = cls(ret)
        ret.VerifyCallback()
        cls._table().Insert(ret, days=1)

        # Return the callback.
        return ret
    

    def RequireDomain(self):
        return self.RequireStr('Domain')
    
    def RequireHandler(self):
        return self.RequireStr('Handler')
    
    def RequireContext(self):
        return self.RequireStruct('Context')
    

    def VerifyCallback(self):
        self.RequireDomain()
        self.RequireContext()
        self.RequireHandler()