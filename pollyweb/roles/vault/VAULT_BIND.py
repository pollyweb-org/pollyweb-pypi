# 📚 VAULT_BIND

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.ITEM import ITEM
from MSG import MSG
from pollyweb import UTILS
from PW_AWS.AWS import AWS


class VAULT_BIND(ITEM):
    ''' 🪣 https://quip.com/IZapAfPZPnOD#temp:C:PDZ669f275089004e74b3004d236 
    {
        "Broker": "any-broker.org",
        "BindID": "793af21d-12b1-4cea-8b55-623a19a28fc5",
        "PublicKey": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDH+wPrKYG1KVlzQUVtBghR8n9dzcShSZo0+3KgyVdOea7Ei7vQ1U4wRn1zlI5rSqHDzFitblmqnB2anzVvdQxLQ3UqEBKBfMihnLgCSW8Xf7MCH+DSGHNvBg2xSNhcfEmnbLPLnbuz4ySn1UB0lH2eqxy50zstxhTY0binD9Y+rwIDAQAB",
        "Code": "airlines.any-igo.org/SSR/WCHR/CRED",
        "Confirmed": True,
        "VaultID": None
    }
    '''

    
    @staticmethod
    def _table():
        return AWS.DYNAMO('BINDS', keys=['Broker', 'BindID'])
    

    @staticmethod
    def RequireBind(broker:str, bindID:str) -> VAULT_BIND:
        '''👉 Gets the bind.
        * Throws an exception if not found.'''
        item = VAULT_BIND._table().Require({
            'Broker': broker, 
            'BindID': bindID
        })

        return VAULT_BIND(item)
    

    @staticmethod
    def Upsert(broker:str, bindID:str, publicKey:str, code:str, confirmed:bool, vaultID:str) -> VAULT_BIND:

        ##LOG.Print(f'VAULT_BIND.Upsert(broker={broker}, bindID={bindID}, publicKey={publicKey}, code={code}, confirmed={confirmed}, vaultID={vaultID})')

        UTILS.RequireArgs([broker, bindID, publicKey, code, confirmed, vaultID])

        obj = {
            "Broker": broker,
            "BindID": bindID,
            "PublicKey": publicKey,
            "Code": code,
            "Confirmed": confirmed,
            "VaultID": vaultID
        }
        VAULT_BIND._table().Upsert(obj)
         

    def GetVaultID(self):
        return self.GetAtt('VaultID')

    def RequirePublicKey(self):
        return self.RequireStr('PublicKey')
     
    def RequireCode(self):
        return self.RequireStr('Code')

    def MatchPublicKey(self, publicKey:str):
        self.Match('PublicKey', publicKey)


    def VerifySignature(self, msg:MSG):
        '''👉 Calls the VerifySignature of the message, 
        with the public key of the bind.'''
        publicKey = self.RequirePublicKey()
        msg.VerifySignature(publicKey)
         
