from ..utils import STRUCT
from ..utils import UTILS


class TOKEN(STRUCT):
    '''
    Example:
    {
        "ID": "7bcf138b-db79-4a42-9d36-2655f8ff1f7c",
        "Issuer": "example.com",
        "Code": "airlines.any-igo.org/SSR/WCH",
        "Version": "1.0.0",
        "QR": "...",
        "Issued": "2018-12-10T13:45:00.000Z",
        "Starts": "2018-12-10T13:45:00.000Z",
        "Expires": "2018-12-10T13:45:00.000Z"
    }
    '''


    @classmethod
    def New(cls, tokenID: str, issuer: str, code: str,
            version: str,
            qr: str,
            starts: str = '',
            expires: str = ''):
        issued = UTILS.GetTimestamp()
        starts_val = starts if starts else issued
        ret = cls({
            "TokenID": tokenID,
            "Issuer": issuer,
            "Code": code,
            "Version": version,
            "QR": qr,
            "Issued": issued,
            "Starts": starts_val,
            "Expires": expires,
        })
        ret.VerifyToken()
        return ret

    
    def MatchCode(self, code:str):
        self.Match('Code', code)


    def RequireCode(self):
        return self.RequireStr('Code')

    def RequireVersion(self):
        return self.RequireStr('Version')

    def RequireIssuer(self):
        return self.RequireStr('Issuer')

    def RequireTokenID(self): 
        return self.RequireUUID('TokenID')

    def RequireQR(self):
        return self.RequireStr('QR')
    
    def RequireIssued(self):
        return self.RequireTimestamp('Issued')

    def RequireStarts(self):
        return self.RequireTimestamp('Starts')

    def GetExpires(self):
        return self.GetTimestamp('Expires')


    def VerifyToken(self):
        self.RequireCode()
        self.RequireVersion()
        self.RequireIssuer()
        self.RequireTokenID()
        self.RequireQR()
        self.RequireIssued()
        self.RequireStarts()
        self.GetExpires()