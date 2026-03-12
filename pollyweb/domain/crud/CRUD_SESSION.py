from CRUD_BASE import CRUD_BASE
from NLWEB import NLWEB
from HOST_SESSION import HOST_SESSION
from pollyweb import UTILS


class CRUD_SESSION(CRUD_BASE):


    def __init__(self, session:HOST_SESSION=None) -> None:
        self._session = session


    @classmethod
    def FromHostSession(cls, session:HOST_SESSION):
        return cls(session)
    

    def HostSession(self):
        ret = self._session
        UTILS.Require(ret, 'No HOST_SESSION was given!')
        return ret
    
    def RequireSessionID(self):
        return self.HostSession().RequireSessionID()
    
    def ToInterface(self):
        return self.HostSession().ToInterface()
    
    def RequireLanguage(self):
        return self.HostSession().RequireLanguage()


    def InvokeGoodbye(self):
        return NLWEB.ROLES().BROKER().InvokeGoodbye(
            source= 'Session@Crud',
            session= self.ToInterface())
    

    def RequireWallet(self):
        ''' 👉 Returns the wallet of the given session.'''
        session = self.HostSession()
        walletID = session.RequireVaultID()
        wallet = self.WALLETS().RequireWallet(walletID)
        return wallet
    

    def RequireWalletEntity(self, entityName:str):
        ''' 👉 Returns the wallet's data for a given entity configuration.'''
        wallet = self.RequireWallet()
        return wallet.RequireEntity(entityName)

