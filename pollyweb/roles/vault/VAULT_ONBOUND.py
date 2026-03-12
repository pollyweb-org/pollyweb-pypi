from PW_DOMAIN import CODE
from PW import PW
from MSG import MSG
from pollyweb import STRUCT


class VAULT_ONBOUND(STRUCT):


    @classmethod
    def Trigger(cls, msg:MSG): 

        MSG.AssertClass(msg)

        outcomes = { 
            'Message': msg,
            'VaultID': None,   # The ID of the wallet's owner on the vault's database.
            'Confirmed': False # The need for an additional 2-step verification.
        }
        
        outcomes = PW.BEHAVIORS().HANDLER().TriggerLambdas(
            event= 'OnBound@Vault', 
            payload= outcomes,
            required= True)
        
        return STRUCT(outcomes)
    

    def RequireMessage(self):
        return MSG(self.RequireStruct('Message'))


    def RequireBinds(self):
        return self.RequireMessage().RequireStructs('Binds')


    def IsVaultBind(self): 
        '''👉 Does the message contain a bind to pollyweb.org/VAULT/BIND?'''
        for bind in self.RequireBinds():
            if bind.RequireStr('Code') == CODE.CODES().BIND():
                return True
        return False
    

    def RegisterWallet(self):
        ''' 👉️ Inserts a wallet into the wallets table and returns the wallet ID.'''
        walletID = PW.BEHAVIORS().CRUD().WALLETS().Insert(
            publicKey= self.RequireMessage().RequireStr('PublicKey'),
            binds= self.RequireBinds())
        return walletID