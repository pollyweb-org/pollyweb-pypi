# 🃏 ISSUER

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from pollyweb import UTILS
from pollyweb import STRUCT
from PW import PW
from SESSION import SESSION
from VAULT import VAULT
from MSG import MSG
from ISSUER_TOKEN import ISSUER_TOKEN
from VAULT_BIND import VAULT_BIND
from PW_DOMAIN import CODE



# ✅ DONE
class ISSUER(VAULT):
    ''' 🃏 Issuer: 
    * https://quip.com/a167Ak79FKlt/-Issuer 
    
    Tables:
    * `Tokens`: list of tokens issued by the issuer.
    '''
    
    @classmethod
    def _getDomainName(cls) -> str:
        return PW.CONFIG().RequireDomain()



    @classmethod
    def Issue(
            cls, 
            broker:str, 
            code:str, version:str, sessionID:str, 
            starts:str=None, 
            expires:str=None
            ) -> ISSUER_TOKEN:
        '''👉️ Creates a new token.'''

        UTILS.RequireArgs([broker, code, version, sessionID])
        UTILS.AssertIsUUID(sessionID)
        UTILS.MatchTimestamp(starts)
        UTILS.MatchTimestamp(expires)
        CODE.Verify(code)
        
        token = ISSUER_TOKEN.New(
            issuer= cls._getDomainName(),
            code= code,
            version= version,
            sessionID= sessionID,
            broker= broker,
            starts= starts,
            expires= expires)
        
        return token
    

    @classmethod
    def Offer(cls, source:str, session:SESSION, code:str, tokenID:str):
        '''👉️ Gets the token and offers it to a Broker.'''

        UTILS.RequireArgs([source, session, code, tokenID])
        session.VerifySession()

        token = ISSUER_TOKEN.RequireToken(tokenID)
        token.MatchCode(code)
        token.MatchBroker(session.RequireBroker())

        PW.ROLES().BROKER().InvokeOffer(
            source= source,
            session= session,
            token= token.ToInterface())

    
    @classmethod
    def Revoke(cls, source:str, session:SESSION, tokenID:str):
        '''👉️ Gets the token and revokes it.'''

        UTILS.RequireArgs([source, session, tokenID])
        session.VerifySession()

        # Get the token.
        token = ISSUER_TOKEN.RequireToken(tokenID)
        token.MatchBroker(session.RequireBroker())

        # Ask the broker to delete the token.
        PW.ROLES().BROKER().InvokeRevoke(
            source= source,
            session= session,
            tokenID= tokenID)

        # Remove the token from the database.
        token.Delete()


    @classmethod
    def InvokeToken(cls, sessionID:str, issuer:str, tokenID:str) -> STRUCT:
        ''' 👱🚀 Download the token QR from the Issuer.
        * https://quip.com/a167Ak79FKlt#temp:C:TMB24db6408284b4de5a52bcdfec
        '''
        UTILS.RequireArgs([issuer, tokenID, sessionID])
        UTILS.AssertIsUUID(tokenID)
        UTILS.AssertIsUUID(sessionID)

        content = PW.WALLET().CallDomain(
            domain= issuer,
            subject= 'Token@Issuer',
            body= {
                "SessionID": sessionID,
                "TokenID": tokenID
            })

        qr = content.RequireStr('QR')
        UTILS.AssertIsType(qr,str)
        
        return qr


    @classmethod
    def HandleToken(cls, event):
        ''' 👱🚀 https://quip.com/a167Ak79FKlt#temp:C:TMB24db6408284b4de5a52bcdfec
        "Header": {
            "From": "any-broker.org"
        },
        "Body": {
            "SessionID": "<session-uuid>",
            "TokenID": "7bcf138b-db79-4a42-9d36-2655f8ff1f7c"
        }'''
        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('Token@Issuer')
        
        # Get and verify the token.
        tokenID = msg.RequireStr('TokenID')
        token = ISSUER_TOKEN.RequireToken(tokenID)
        token.MatchSession(session)
        
        # Return the token.
        return {
            'QR': token.RequireQR()
        }


    @classmethod
    def HandleStatus(cls, event):
        ''' ✨🐌 https://quip.com/a167Ak79FKlt#temp:C:TMB8f357a70c63849e68a76518f5
        "Body": {
            "Locator": "ace79fcb-fa93-4544-bbe3-644b31df03db"
        }'''
        msg = MSG(event)

        # Get the token.
        tokenID = msg.RequireStr('Locator')
        token = ISSUER_TOKEN.RequireToken(tokenID)

        # Verify the trust.
        PW.ROLES().GRAPH().VerifyTrust(
            domain= msg.RequireFrom(),
            context= 'CONSUMER',
            code= token.RequireCode())

        # Return the status.
        return {
            'IsActive' : token.IsActive()
        }
    

    @classmethod
    def InvokeAccepted(cls, source:str, issuer:str, sessionID:str, tokenID:str) -> None:
        UTILS.RequireArgs([source, issuer, sessionID, tokenID])
        UTILS.AssertIsUUID(sessionID)
        UTILS.AssertIsUUID(tokenID)

        PW.BEHAVIORS().MESSENGER().Push(
            to= issuer,
            subject= 'Accepted@Issuer',
            source= source,
            body= {
                "SessionID": sessionID,
                "TokenID": tokenID
            })


    @classmethod
    def HandleAccepted(cls, event) -> None:
        ''' 🤵🐌
        "Body": {
            "SessionID": "<session-uuid>",
            "TokenID": "<token-uuid>"
        }
        '''
        msg, session = cls.VerifySession(event)
        msg.MatchSubject('Accepted@Issuer')

        # Get and verify the token.
        tokenID = msg.RequireStr('TokenID')
        token = ISSUER_TOKEN.RequireToken(tokenID)
        token.MatchSession(session)
        
        # Continue the conversation.
        session.ContinueTalk(msg)
            