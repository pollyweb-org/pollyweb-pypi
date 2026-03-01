# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from pollyweb import STRUCT



class SESSION(STRUCT):
    ''' 👉 Info about a session.
    {
        "Host": "any-host.org",
        "Locator": "website",
        "Broker": "any-broker.org",
        "SessionID": "61738d50-d507-42ff-ae87-48d8b9bb0e5a"
    }
    '''

    @staticmethod
    def New(host:str, locator:str, broker:str, sessionID:str) -> SESSION:
        return SESSION({
            "Host": host,
            "Locator": locator,
            "Broker": broker,
            "SessionID": sessionID
        })
    

    def RequireHost(self) -> str:
        return self.RequireStr('Host')
    

    def RequireLocator(self) -> str:
        return self.RequireStr('Locator')


    def RequireBroker(self) -> str:
        return self.RequireStr('Broker')

    
    def RequireSessionID(self) -> str:
        return self.RequireStr('SessionID')
    

    def RequireID(self) -> str:
        return self.RequireStr('SessionID')
    

    def VerifySession(self):
        '''👉 Verifies if the required properties are set.'''
        self.RequireHost()
        self.RequireLocator()
        self.RequireBroker()
        self.RequireSessionID()
