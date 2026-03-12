# 🗄️ VAULT

def test():
    return 'this is VAULT test.'

from PW import PW
from PW_UTILS.HANDLER import HANDLER
from HOST import HOST
from HOST_SESSION import HOST_SESSION
from PW_AWS.ITEM import ITEM
from MSG import MSG
from PROMPT_SESSION import PROMPT_SESSION
from SESSION import SESSION
from pollyweb import UTILS
from pollyweb import STRUCT
from pollyweb import LOG
from VAULT_DISCLOSURE import VAULT_DISCLOSURE



class VAULT(HOST, HANDLER):
    ''' 🗄️ Holds user secrets.
    Docs: https://quip.com/IZapAfPZPnOD '''
    

    def __init__(self):    
        self.OnPython('VerifyCheckIn@Host', self._VerifyCheckIn)
        self.OnPython('VerifyPrompted@Host', self._VerifyWalletSignature)
        self.OnPython('VerifyDownload@Host', self._VerifyWalletSignature)
        self.OnPython('VerifyUpload@Host', self._VerifyWalletSignature)
        self.OnPython('OnNewSession@Host', self._OnNewSession)
        

    @classmethod
    def BINDS(cls):
        from VAULT_BIND import VAULT_BIND
        return VAULT_BIND()


    @classmethod
    def ONBOUND(cls):
        from VAULT_ONBOUND import VAULT_ONBOUND
        return VAULT_ONBOUND()
    

    @classmethod
    def _VerifyCheckIn(cls, msg:MSG):
        ''' 🏃 Throws an exception if the given BindIDs do not exist or are inconsistent.'''
        LOG.Print('🗄️ VAULT._VerifyCheckIn()')

        publicKey = None
        for bindID in msg.GetList('Binds'):

            # Get the bind.
            bind = cls.BINDS().RequireBind(
                broker= msg.RequireFrom(), 
                bindID= bindID)
            
            # Check if the Public Key is the same in all binds.
            if publicKey != None:
                bind.MatchPublicKey(publicKey)
            publicKey = bind.RequirePublicKey()
    

    @classmethod
    def _OnNewSession(cls, session:HOST_SESSION):

        # Infer the VaultID from one of the received session binds.
        for bindID in session.RequireBinds():
            
            # Get the bind from the database.
            bind = cls.BINDS().RequireBind(
                broker= session.RequireBroker(),
                bindID= bindID)
            
            # Set the VaultID in the session.
            vaultID = bind.GetVaultID()
            session.SetVaultID(vaultID)
            session.UpdateItem()

            # Break, we only need one.
            break


    @classmethod
    def _VerifyWalletSignature(cls, msg:MSG, session:ITEM):
        ''' 🏃 If the user is bound, check the signature with the public in the vault.'''
        LOG.Print('🗄️ VAULT._VerifyWalletSignature()')
        
        for bindID in session.GetList('Binds'):
            bind = cls.BINDS().RequireBind(
                broker=msg.RequireFrom(), 
                bindID=bindID)
            bind.VerifySignature(msg)
            break
    

    @classmethod
    def InvokeBound(cls, 
        source:str, 
        vault:str, 
        sessionID:str, 
        binds:list[any], 
        publicKey:str):

        ''' 🏃 Broker.Bound: 🐌 https://quip.com/oSzpA7HRICjq/-Broker-Binds#temp:C:DSD3f7309f961e24f0ebb5897e2f '''
        LOG.Print('🗄️ VAULT.InvokeBound()')

        UTILS.RequireArgs([source, vault, sessionID, binds, publicKey])
        UTILS.AssertIsType(binds, list)

        PW.BEHAVIORS().MESSENGER().Push(
            source= source,
            to= vault,
            subject= 'Bound@Vault',
            body= {
                "SessionID": sessionID,
                "PublicKey": publicKey,
                "Binds": binds
            })

    
    @classmethod
    def HandleBound(cls, event):
        ''' 
        🗄️🐌 https://quip.com/oSzpA7HRICjq/-Broker-Binds#temp:C:DSD3f7309f961e24f0ebb5897e2f 
        🗄️🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZf81764583b31439f999550159  
        Body:
          SessionID: 1af1f5eb-7256-4b1e-bae8-47de6bf2665e
          PublicKey: <publicKey>
          Binds:
            - ID: fe70386f-5dce-4463-b7ba-8e7c0095e65d
              Code: europa.eu/DISABILITY/CARD
        '''
        LOG.Print('🗄️ VAULT.HandleBound()', event)

        msg, session = cls.VerifySession(event)
                
        outcomes = cls.ONBOUND().Trigger(msg)
        
        # Verify
        outcomes.RequireStr(
            att= 'VaultID', 
            msg= 'No VaultID returned by the Bound@Vault handler.')

        # Add to 🪣 Binds
        for bind in msg.Structs('Binds'):
            cls.BINDS().Upsert(
                broker= msg.RequireFrom(),
                bindID= bind.RequireAtt('ID'),
                publicKey= msg.RequireAtt('PublicKey'),
                code= bind.RequireAtt('Code'),
                confirmed= outcomes.RequireBool('Confirmed'),
                vaultID= outcomes.RequireAtt('VaultID'))

        # Continue the conversation.
        session.ContinueTalk(msg)


    @classmethod
    def InvokeContinue(cls, source:str, vault:str, token:str):
        ''' 📦🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZ67394972376e4fb8979d41209 '''
        PW.BEHAVIORS().MESSENGER().Push(
            source= source,
            to= vault, 
            subject= 'Continue@Vault',
            body= {
                "Continue": token
            })


    @classmethod
    def HandleContinue(cls, event):
        ''' 📦🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZ67394972376e4fb8979d41209 
        "Body": {
            "Continue": "6704488d-fb53-446d-a52c-a567dac20d20"
        }
        '''
        #msg, session = cls.VerifySession(event)
        pass


    @classmethod
    def InvokeDisclose(cls, language:str, session:PROMPT_SESSION, vault:str, bindID:str):
        ''' 👱🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZa3f3ba7f94154a2fbd520e931 '''
        LOG.Print(f'👱➡️🗄️ VAULT.InvokeDisclose()')

        session.VerifySession()

        PW.WALLET().CallDomain(
            domain= vault,
            subject= 'Disclose@Vault',
            body= {
                "SessionID": session.RequireSessionID(),
                "Consumer": session.RequireHost(),
                "Language": language,
                "BindID": bindID,
            })


    @classmethod
    def HandleDisclose(cls, event):
        ''' 👱🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZa3f3ba7f94154a2fbd520e931 
        "Header": {
            "From": "any-broker.org"
        },
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",
            "Consumer": "any-coffee-shop.com",
            "Language": "en-us",
            "BindID": "793af21d-12b1-4cea-8b55-623a19a28fc5"
        }
        '''
        LOG.Print('🗄️ VAULT.HandleDisclose()', event)

        # ⛔ Discloses to vaults are done with the consumer's session, do don't verify the session!
        msg = MSG(event)
        # ⛔ msg, session = cls.VerifySession(event, fromWallet= True)

        msg.MatchSubject('Disclose@Vault')

        # Loop the binds to disclose.
        bindID = msg.RequireUUID('BindID')

        # Validate the user’s signature in the Msg
        broker = msg.RequireFrom()
        bind = cls.BINDS().RequireBind(
            broker= broker,
            bindID= bindID)            
        bind.VerifySignature(msg)

        # Verify if 📡 Consumer is trustable
        consumer = msg.RequireStr('Consumer')
        code = bind.RequireCode()
        PW.ROLES().GRAPH().VerifyTrust(
            domain= consumer,
            code= code, 
            context= 'CONSUMER')
        
        # Ask any additional question to the user (e.g., OTP):
        # -> Add to 🪣 Disclosures
        # -> Call 🐌 Prompt: 🤵📎 Broker. Prompt

        # Get the user data.
        args = {
            'VaultID': bind.GetVaultID(),
            'Code': code,
            'Language': msg.RequireStr('Language'),
            'Data': '',
            'Token': None
        }
        args = cls.Trigger('OnDisclose@Vault', args)
        args.RequireAtt('Data')

        # Send details to 📡 Consumer:
        # -> 🐌 Consume: 📡 Consumer
        PW.ROLES().CONSUMER().InvokeConsume(
            source= 'Disclose@Vault',
            consumer= consumer,
            broker= broker,
            sessionID= msg.RequireUUID('SessionID'),
            code= code,
            version= args.RequireStr('Version'),
            data= args.RequireAtt('Data'),
            token= args.GetAtt('Token'))  # For now, we're not sending large data sets.


    @classmethod
    def InvokeSuppress(cls, to:str, consumer:str, sessionID:str, source:str):
        ''' 🤵🏃 https://quip.com/IZapAfPZPnOD#temp:C:PDZeda25d5a05a3470a994e6689d '''
        PW.BEHAVIORS().MESSENGER().Push(
            to= to,
            subject= 'Suppress@Vault',
            source= source,
            body= {
                "Consumer": consumer,
                "SessionID": sessionID
            })


    @classmethod
    def HandleSuppress(cls, event):
        ''' 🤵🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZeda25d5a05a3470a994e6689d 
        "Body": {
            "SessionID": "<session-uuid>",
            "Consumer": "airline.any-business.org"
        }
        '''
        LOG.Print('🗄️ VAULT.HandleSuppress()', event)

        msg, session = cls.VerifySession(event)
        
        # If the session is tracked, stop it - e.g.: 
        #   GIVEN a vault that is a palm reader 
        #     AND the palm reader is actively looking for the session’s user
        #    WHEN suppressed 
        #    THEN stop searching for it, and stop sending findings to the host.
        cls.Trigger('OnSupress@Vault', event)
        
        # Remove the session from 🪣 Disclosures
        # If the session is not found on disclosures, just discard the message.
        disclosure = VAULT_DISCLOSURE.GetDisclosure(msg)
        if not disclosure.IsMissingOrEmpty():
            disclosure.Delete()


    @classmethod
    def InvokeUnbind(cls, source:str, vault:str, bindID: str):
        PW.BEHAVIORS().MESSENGER().Push(
            to= vault,
            subject= 'Unbind@Vault',
            source= source,
            body= {
                "BindID": bindID
            })


    @classmethod
    def HandleUnbind(cls, event):
        ''' 🤵🐌 https://quip.com/IZapAfPZPnOD#temp:C:PDZ7c06cfb34057465cadb320937 
        "Body": {
            "BindID": "793af21d-12b1-4cea-8b55-623a19a28fc5"
        }
        '''
        msg = MSG(event)

        bind = cls.BINDS().RequireBind(
            broker=msg.RequireFrom(), 
            bindID= msg.RequireAtt('BindID'))
        
        bind.Delete()


    @classmethod
    def RunTalkerProcedure(
        cls, talkerID:str, procedure:str, 
        session:SESSION, context:any):

        LOG.Print(
            '🗄️ VAULT.StartTalk()', 
            f'{talkerID=}', f'{procedure=}',
            'session=', session,
            'context=', context)

        # Validations.
        UTILS.RequireArgs([talkerID, procedure, session])
        UTILS.AssertIsType(session, SESSION)
        session.VerifySession()

        # Create a talk for the Vault.
        talk = PW.ROLES().HOST().SESSIONS().IncludeVault(
            session= session,
            talkerID= talkerID,
            context= context)

        # Get the procedure's details.
        step = talk.GetTalkProcedure(procedure)

        # Execute the procedure.
        talk.Exec(step)