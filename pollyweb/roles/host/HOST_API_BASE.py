# 🤗 HOST

from pollyweb import LOG
from PW_UTILS.HANDLER import HANDLER
from MSG import MSG


# ✅ DONE
class HOST_API_BASE(HANDLER):
    ''' 🤗 https://quip.com/s9oCAO3UR38A/-Host \n
    Events:
     * OnCheckOut@Host (optional)
     * HandleFound@Host (required)
    '''


    @classmethod
    def QR(cls, qr):
        from HOST_QR import HOST_QR
        return HOST_QR(qr)


    @classmethod 
    def SESSIONS(cls):
        from HOST_SESSIONS import HOST_SESSIONS
        return HOST_SESSIONS()


    @classmethod 
    def TALKERS(cls):
        from HOST_TALKERS import HOST_TALKERS
        return HOST_TALKERS()
    
    
    @classmethod
    def ASSETS(cls):
        from HOST_ASSET import HOST_ASSET
        return HOST_ASSET()
    
    
    @classmethod
    def FILES(cls):
        from HOST_FILES import HOST_FILES
        return HOST_FILES()
    
    
    @classmethod
    def LOCATORS(cls):
        from HOST_LOCATOR import HOST_LOCATOR
        return HOST_LOCATOR()



    @classmethod
    def VerifySession(cls, event, fromWallet:bool=False, fromPalmist:bool=False):
        '''👉 Verifies if the session exists.
        * Returns the message and the session item.
        
        Usage: 
        * msg, session = self.VerifySession(event)

        Exceptions:
        * Raises an exception if the session doesn't exist.
        '''

        if fromWallet and fromPalmist:
            LOG.RaiseValidationException('Wallet and Palmist? Dude, make up your mind!')
        
        msg = MSG(event)

        if fromWallet:
            broker = msg.RequireFrom()
        elif fromPalmist:
            broker = msg.RequireAtt('Broker')
        else:
            broker = msg.RequireFrom()
        
        session = cls.SESSIONS().RequireSession(
            broker= broker, 
            sessionID= msg.RequireUUID('SessionID'))
        
        return msg, session


