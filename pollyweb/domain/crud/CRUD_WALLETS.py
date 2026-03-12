from CRUD_WALLET import CRUD_WALLET
from PW_AWS.AWS import AWS
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_WALLETS():
    

    @classmethod
    def ITEMS(cls):
        from CRUD_WALLET_ITEMS import CRUD_WALLET_ITEMS
        return CRUD_WALLET_ITEMS()
    
    
    @classmethod
    def SESSIONS(cls):
        from CRUD_WALLET_SESSIONS import CRUD_WALLET_SESSIONS
        return CRUD_WALLET_SESSIONS()
    
    
    @classmethod
    def _Table(cls):
        return AWS.DYNAMO('WALLETS')
    

    @classmethod
    def RequireWallet(cls, walletID:str):
        UTILS.AssertIsUUID(walletID, require=True)
        ret = cls._Table().Require(walletID)
        return CRUD_WALLET(ret)
    

    @classmethod
    def Insert(cls, publicKey:str, binds:list):
        ''' 👉️ Inserts a wallet into the wallets table and returns the wallet ID.'''
        
        # Verify inputs.
        UTILS.RequireArgs([publicKey, binds])
        UTILS.AssertIsList(binds, require=True)

        # Build the entity.
        walletID = UTILS.UUID() 
        wallet = STRUCT({
            'ID': walletID,
            'PublicKey': publicKey,
            'Binds': binds
        })

        # Verify.
        wallet.RequireStructs('Binds')

        # Insert.
        cls._Table().Insert(wallet)

        # Return.
        return walletID