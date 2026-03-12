# 📡 CONSUMER

from TOKEN import TOKEN
from PW import PW
from PROMPT_SESSION import PROMPT_SESSION
from SESSION import SESSION
from MSG import MSG
from HOST import HOST
from PW_UTILS.HANDLER import HANDLER
from pollyweb import UTILS
from PW_DOMAIN import CODE
from pollyweb import LOG


class CONSUMER(HOST, HANDLER):
    ''' 📡 https://quip.com/UbokAEferibV/-Consumer '''
    

    @classmethod
    def QUERIES(cls): 
        from QUERY import CONSUMER_QUERY
        return CONSUMER_QUERY()


    @classmethod
    def Query(cls, session:SESSION, message:str, code:str): 
        '''🤵🐌 Requests queries on a session. 
        * codes: [{code:message}]'''

        LOG.Print('📡 CONSUMER.Query()',
                  f'{message=}', f'{code=}', 
                  'session=', session)
                  
        UTILS.RequireArgs([session, message, code])
        
        UTILS.AssertIsType(session, SESSION)
        UTILS.AssertIsType(code, str)
        session.VerifySession()
        CODE.Verify(code)

        # Verify if the session is active.
        host_session = PW.ROLES().HOST().SESSIONS().RequireSession(
            broker= session.RequireBroker(),
            sessionID= session.RequireID()
        )

        # Compile the query codes.
        query = cls.QUERIES().New(
            code= code, 
            message= message)

        # Add the query codes to the session.
        host_session.AddQuery(query)

        # Query the broker.
        PW.ROLES().BROKER().InvokeQuery(
            source= 'Query@Consumer',
            session= session,
            query= query)


    @classmethod
    def InvokeConsume(
            cls, source:str, consumer:str, broker:str, sessionID:str, 
            code:str, version:str, data:any, token:str=None):
        '''
        🗄️🐌 CONSUMER.CONSUME() 

        Docs: 
        - https://quip.com/UbokAEferibV#temp:C:Yfbbd64684ba1df4ea683cf4e49b

        Args:
        - `source` (string): sender of the message, informative only.
        - `consumer` (hostname): destination domain.
        - `broker` (hostname): session owner.
        - `sessionID` (uuid): session ID.
        - `code` (string): type of data shared.
        - `version` (string): version of the code's schema.
        - `data` (object): content shared.
        - `token` (uuid): token to ask for more data.
        '''
        
        LOG.Print(
            '📡 CONSUMER.InvokeConsume()',
            f'{source=}', f'{consumer=}', f'{broker=}', f'{sessionID=}', 
            f'{code=}', f'{version=}', f'{token=}', 
            f'data=', data)

        UTILS.RequireArgs([source, consumer, broker, sessionID, code, version, data])
        UTILS.AssertIsUUID(sessionID)
        CODE.Verify(code)

        body= {
            "Session": {
                "Broker": broker,
                "SessionID": sessionID
            },
            "Shared": {
                "Code": code,
                "Version": version,
                "UserData": data
            }
        }
        if token != None:
            body['More'] = token
    
        PW.BEHAVIORS().MESSENGER().Push(
            source= source,
            to= consumer,
            subject= 'Consume@Consumer',
            body= body)


    @classmethod
    def HandleConsume(cls, event):
        '''🗄️🐌 https://quip.com/UbokAEferibV#temp:C:Yfbbd64684ba1df4ea683cf4e49b
        "Body": {
            "Session": {
                "Broker": "any-broker.org",
                "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48"
            },
            "Shared": {
                "Code": "airlines.any-igo.org/SSR/WCH",
                "Version": "1.0",
                "UserData": "..."
            },
            "More": "6704488d-fb53-446d-a52c-a567dac20d20"
        }'''

        LOG.Print('📡 CONSUMER.HandleConsume()', event)

        msg = MSG(event)
        msg.MatchSubject('Consume@Consumer')

        # Verify if the session is valid.
        session = PW.ROLES().HOST().SESSIONS().RequireSession(
            broker= msg.RequireDeepStr('Session.Broker'),
            sessionID= msg.RequireUUID('Session.SessionID', noHierarchy=False))

        # Verify if this code was asked for in this session.
        code = msg.RequireDeepStr('Shared.Code')
        session.VerifyQuery(code)

        # Verify if the 🗄️ Vault is trustable for the code.
        vault = msg.RequireFrom()
        PW.ROLES().GRAPH().VerifyTrust(
            domain= vault,
            context= 'VAULT',
            code= code)

        # Consume the information.
        cls.TriggerLambdas('OnConsume@Consumer', payload=event)
        cls.ContinueConsume(event)

        # Continue the conversation.
        session.ContinueTalk(msg)


    @classmethod
    def ContinueConsume(cls, event):
        '''👉 Ask for more, if there's more.'''

        LOG.Print('📡 CONSUMER.ContinueConsume()', event)

        msg = MSG(event)

        if not msg.IsMissingOrEmpty('More'):
            
            PW.ROLES().VAULT().InvokeContinue(
                source= 'HandleConsume@Consumer',
                vault= msg.RequireFrom(),
                token= msg.RequireUUID('More'))


    @classmethod
    def InvokeVerify(cls, session:PROMPT_SESSION, tokens:list[TOKEN]):
        '''👱🐌 https://quip.com/UbokAEferibV#temp:C:Yfb44ecdc30a739496d9d77b5874'''

        LOG.Print('📡 CONSUMER.HandleVerify()', 
                  'session=', session,
                  'tokens=', tokens)

        session.VerifySession()

        PW.WALLET().CallDomain(
            domain= session.RequireHost(),
            subject= 'Verify@Consumer',
            body= {
                "SessionID": session.RequireSessionID(),
                "Tokens": tokens
            })


    @classmethod
    def HandleVerify(cls, event):
        '''👱🐌 https://quip.com/UbokAEferibV#temp:C:Yfbfe8bb19958054f949358da566
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",
            "Tokens": [{
                "Code": "airlines.any-igo.org/SSR/WCH",
                "Version": "1.0.0",
                "Issuer": "example.com",
                "TokenID": "7bcf138b-db79-4a42-9d36-2655f8ff1f7c",
                "QR": "..."
            }]
        }'''

        LOG.Print('📡 CONSUMER.HandleVerify()', event)

        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('Verify@Consumer')

        # Get and validate the tokens.
        tokens= TOKEN.FromStructs(
            structs= msg.RequireStructs('Tokens')
        )
        for token in tokens:
            token.VerifyToken()

        session.AddTokens(tokens)

        PW.BEHAVIORS().HANDLER().TriggerPython('OnVerify@Consumer', session, tokens)
        cls.TriggerLambdas('OnVerify@Consumer', payload=event)

        # Continue the conversation.
        session.ContinueTalk(msg)


    @classmethod
    def InvokeWontShare(cls, session:PROMPT_SESSION, code:str):
        '''👱🐌 '''

        LOG.Print('📡 CONSUMER.InvokeWontShare()', 
                  f'{code=}'
                  'session=', session)

        session.VerifySession()
        CODE.Verify(code)

        PW.WALLET().CallDomain(
            domain= session.RequireHost(),
            subject= 'WontShare@Consumer',
            body= {
                "SessionID": session.RequireSessionID(),
                "Code": code
            })


    @classmethod
    def HandleWontShare(cls, event):
        '''👱🐌 
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",
            "Code": "airlines.any-igo.org/SSR/WCH"
        }'''
        
        LOG.Print('📡 CONSUMER.HandleWontShare()', event)
                  
        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('WontShare@Consumer')

        # Continue the conversation.
        session.ContinueTalk(msg)