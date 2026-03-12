from PW_AWS.AWS import AWS
from SESSION import SESSION
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_WALLET_SESSIONS:


    @classmethod
    def _Table(cls): 
        return AWS.DYNAMO('WALLET_SESSIONS')
       

    @classmethod
    def GetSession(cls, id:str):
        session = cls._Table().GetItem(id)

        if not session.IsMissingOrEmpty():
            UTILS.Require(session)
            return session
        
        # Does not exist.
        session = {
            'ID': id,
            'CreatedOn': UTILS.GetTimestamp()
        }
        session = cls._Table().Upsert(session, days=1)
        UTILS.Require(session)
        return session