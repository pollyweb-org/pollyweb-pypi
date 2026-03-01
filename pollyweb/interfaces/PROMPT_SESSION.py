  

from SESSION import SESSION
from ..utils import STRUCT   


class PROMPT_SESSION(STRUCT):
    '''👉 Visual info about the session to the wallet.
    Example:
    {
        "SessionID": "1313c5c6-4038-44ea-815b-73d244eda85e",
        "Broker": "any-broker.org",
        "Host": "any-host.org",
        "HostTranslation": "Any Host",
        "SmallIcon": "https://...",
        "BigIcon": "https://...",
        "Code": "pollyweb.org/HOST", 
        "Locator": "SALON"
    }
    '''

    @staticmethod 
    def New(obj:dict):
        ret = PROMPT_SESSION(obj)
        ret.VerifySession()
        return ret
    

    def RequireHost(self):
        return self.RequireStr('Host')

    def RequireHostTranslation(self):
        return self.RequireStr('HostTranslation')

    def RequireLocator(self):
        return self.RequireStr('Locator')

    def RequireSessionID(self):
        '''👉 Returns the session's UUID.'''
        return self.RequireUUID('SessionID')
    
    def RequireBroker(self):
        return self.RequireStr('Broker')


    def VerifySession(self):
        self.Require()
        self.RequireHost()
        self.RequireHostTranslation()
        self.RequireLocator()
        self.RequireSessionID()
        self.RequireBroker()


    def ToInterface(self) -> SESSION:
        ret = SESSION.New(
            host= self.RequireHost(),
            locator= self.RequireLocator(),
            broker= self.RequireBroker(),
            sessionID= self.RequireSessionID())
        
        ret.VerifySession()
        return ret