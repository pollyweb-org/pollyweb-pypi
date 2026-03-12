# 📚 RECEIVER (part of SYNCAPI)

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.ITEM import ITEM
from PW_AWS.AWS import AWS
from pollyweb import UTILS


class SYNCAPI_RECEIVER_MAP(ITEM):
    '''
    {
      "ID": "method@ator",
      "Target": "any-function-name",
      "IgnoreValidation": "True"
    }
    '''


    @classmethod
    def New(cls, subject:str, handler:str, ignoreValidation:bool=False) -> None:
        UTILS.RequireArgs([subject, handler, ignoreValidation])

        item = {
            "ID": subject,
            "Target": handler,
            "IgnoreValidation": ignoreValidation
        }
        
        cls.Table().Upsert(item)



    @classmethod
    def Table(cls): 
        return AWS.DYNAMO('MAP')
    

    @classmethod
    def RequireMap(cls, method:str) -> SYNCAPI_RECEIVER_MAP:
        '''👉 Item lookup.'''
        item = cls.Table().Require(method)
        # Note: don't require... cannot remember why not :(
        ret =  SYNCAPI_RECEIVER_MAP(item)
        ret.Require()    
        return ret
    

    def Handler(self) -> str:
        '''👉 Name the Lambda function to execute.'''
        return self.RequireStr('Target')
    

    def IgnoreValidation(self) -> bool:
        '''👉 Asks the receiver not to validate the signature of the message.
        This is so wallets can send messages on behalf of their brokers.
        Those messages will be validated by the recipients against the wallet's publicKey previously stored.'''
        return self.RequireBool('IgnoreValidation')