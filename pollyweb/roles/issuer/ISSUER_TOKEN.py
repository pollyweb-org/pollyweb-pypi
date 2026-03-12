# 📚 ISSUER

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.ITEM import ITEM 
from pollyweb import UTILS
from TOKEN import TOKEN
from PW_AWS.AWS import AWS
from HOST_SESSION import HOST_SESSION
from PW_DOMAIN import CODE


class ISSUER_TOKEN(TOKEN, ITEM):
    ''' 🪣 https://quip.com/a167Ak79FKlt#temp:C:TMB43a977fd430c4e29b7201228a
    {
        "ID": "7bcf138b-db79-4a42-9d36-2655f8ff1f7c",
        "Code": "airlines.any-igo.org/SSR/WCHR/CRED",
        "Version": "1",
        "Broker": "any-broker.org",
        "QR": "🤝airlines.any-igo.org/SSR/WCHR/CRED,1,health.any-nation.org,...",
        "Issued": "2018-12-10T13:45:00.000Z",
        "Starts": "2018-12-10T13:45:00.000Z",
        "Expires": "2018-12-10T13:45:00.000Z",
        "Revoked": "2018-12-10T13:45:00.000Z"
    }
    '''


    @classmethod
    def _table(cls):
        return AWS.DYNAMO('TOKENS')
    

    @classmethod
    def RequireToken(cls, tokenID:str) -> ISSUER_TOKEN:
        item = cls._table().Require(tokenID)
        return ISSUER_TOKEN(item)
    
    
    @staticmethod
    def New(
            sessionID:str, issuer:str, code:str, version:str,
            broker:str, starts:str=None, expires:str=None
            ) -> ISSUER_TOKEN:
        
        UTILS.RequireArgs([issuer, code, version, sessionID, broker])
        UTILS.AssertIsUUID(sessionID)
        UTILS.MatchTimestamp(starts)
        UTILS.MatchTimestamp(expires)
        CODE.Verify(code)

        tokenID = UTILS.UUID()
        c = TOKEN.New(
            issuer= issuer,
            tokenID= tokenID,
            code= code,
            version= version,
            qr= f"🤝{code},{version},{issuer},...",
            starts= starts, 
            expires= expires)

        ret = ISSUER_TOKEN(c)
        ret.Merge({
            "ID": tokenID,
            "SessionID": sessionID,
            "Broker": broker,
            "Revoked": None
        })

        ISSUER_TOKEN._table().Insert(ret)
        return ret
        

    def RequireTokenID(self): 
        return self.RequireUUID('ID')


    def IsActive(self) -> bool:
        if self.Revoked():
            raise False
        start = self.RequireStarts()
        end = self.GetExpires()
        if not UTILS.IsNowBetween(start, end):
            return False
        return True
        

    def Revoke(self):
        self.Revoked(UTILS.GetTimestamp())
        self.UpdateItem()


    def Revoked(self, set:str=None) -> str:
        ret = self.RequireAtt('Revoked', set=set)

    
    def SessionID(self) -> str:
        return self.RequireStr('SessionID')
    

    def MatchBroker(self, broker:str):
        self.Match('Broker', broker)


    def ToInterface(self):
        ret = TOKEN({
            "TokenID": self.RequireTokenID(),
            "Issuer": self.RequireIssuer(),
            "Code": self.RequireCode(),
            "Version": self.RequireVersion(),
            "QR": self.RequireQR(),
            "Issued": self.RequireIssued(),
            "Starts": self.RequireStarts(),
            "Expires": self.GetExpires()
        })
        
        ret.VerifyToken()

        return ret
    

    def MatchSession(self, session:HOST_SESSION):
        
        self.Match(
            att= 'SessionID', 
            value= session.RequireSessionID())
        
        self.MatchBroker(
            broker= session.RequireBroker())