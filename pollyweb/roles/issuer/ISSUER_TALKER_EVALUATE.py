
from PW import PW
from TALKER_EVALUATE_BASE import TALKER_EVALUATE_BASE
from pollyweb import UTILS


class ISSUER_TALKER_EVALUATE(TALKER_EVALUATE_BASE):


    def IssueToken(self, 
        code:str, version:str, starts:str=None, expires:str=None):

        UTILS.RequireArgs([code, version])
        UTILS.MatchTimestamp(starts)
        UTILS.MatchTimestamp(expires)

        session = self.RequireSession()
            
        cred = PW.ROLES().ISSUER().Issue(
            broker= session.RequireBroker(),
            sessionID= session.RequireSessionID(),
            code= code,
            version= version,
            starts= starts,
            expires= expires)
        
        return cred.RequireTokenID()
        