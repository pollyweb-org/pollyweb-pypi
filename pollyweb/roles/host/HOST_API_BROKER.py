# 🤗 HOST

from pollyweb import LOG
from NLWEB import NLWEB
from MSG import MSG
from pollyweb import STRUCT
from pollyweb import UTILS


from HOST_API_BASE import HOST_API_BASE

# ✅ DONE
class HOST_API_BROKER(HOST_API_BASE):
    ''' 🤗 https://quip.com/s9oCAO3UR38A/-Host \n
    Events:
     * OnCheckOut@Host (optional)
    '''
    

    @classmethod
    def InvokeAbandoned(cls, source:str, to:str, sessionID:str):
        LOG.Print('🤗 HOST.InvokeAbandoned()')

        UTILS.RequireArgs([source, to, sessionID])
        UTILS.AssertIsType(to, str)
        UTILS.AssertIsType(sessionID, str)

        NLWEBB.BEHAVIORS().MESSENGER().Push(
            source=source, 
            to=to,
            subject= 'Abandoned@Host',
            body= { "SessionID": sessionID })
        

    @classmethod
    def HandleAbandoned(cls, event):
        ''' 🤵🐌 https://quip.com/s9oCAO3UR38A#temp:C:TDDbb2a3e48828a473b84c296777 
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48"
        }
        '''
        LOG.Print('🤗 HOST.HandleAbandoned()', event)

        msg, session = cls.VerifySession(event)
        msg.MatchSubject('Abandoned@Host')

        session.Delete()


    @classmethod
    def InvokeCheckIn(
            cls, source:str, to:str, 
            language:str, sessionID:str, 
            binds:list[str], tokens:list[str], 
            code:str, locator:str) -> STRUCT:
        ''' 🤵🚀 https://quip.com/s9oCAO3UR38A#temp:C:TDDf29b75b2d0214f9a87224b338 '''

        UTILS.RequireArgs([source, to, language, sessionID, code, locator])

        body = { 
            "Code": code,
            "Locator": locator,
            "Language": language,
            "SessionID": sessionID,
            "Binds": binds,
            "Tokens": tokens
        }
    
        NLWEB.BEHAVIORS().SYNCAPI().Invoke(
            to=to,
            subject= 'CheckIn@Host',
            body= body)
        
        
    @classmethod
    def HandleCheckIn(cls, event):
        ''' 🤵🚀 https://quip.com/s9oCAO3UR38A#temp:C:TDDf29b75b2d0214f9a87224b338 
        "Body": {
            "SessionID": "61738d50-d507-42ff-ae87-48d8b9bb0e5a",
            "Code": "pollyweb.org/THING",
            "Locator": "MY-THING-ID",
            "Language": "en-us",    
            "Binds": [
                "125a5c75-cb72-43d2-9695-37026dfcaa48",
                "bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc"
            ],
            "Tokens": [
                "125a5c75-cb72-43d2-9695-37026dfcaa48",
                "bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc"
            ]
        }
        '''
        LOG.Print('🤗 HOST.HandleCheckIn()', event)

        msg = MSG(event)
        msg.MatchSubject('CheckIn@Host')

        NLWEB.BEHAVIORS().HANDLER().TriggerPython('VerifyCheckIn@Host', msg)

        cls.SESSIONS().HandleCheckIn(msg)


    @classmethod
    def InvokeCheckOut(cls, source:str, to:str, sessionID:str):
        NLWEB.BEHAVIORS().MESSENGER().Push(
            source=source, 
            to=to,
            subject= 'CheckOut@Host',
            body= { "SessionID": sessionID })
        

    @classmethod
    def HandleCheckOut(cls, event):
        ''' 🤵🐌 https://quip.com/s9oCAO3UR38A#temp:C:TDD7b2a9a988f404282af7a63ff9 
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48"
        }
        '''
        LOG.Print('🤗 HOST.HandleCheckOut()', event)

        msg, session = cls.VerifySession(event)
        msg.MatchSubject('CheckOut@Host')

        goodbye = cls.Trigger('OnCheckOut@Host', {
            'CheckOut': event, 
            'Goodbye': True
        })
        goodbye = STRUCT(goodbye)

        if goodbye.RequireBool('Goodbye') == True: 
            
            goodbye = STRUCT(goodbye)
            NLWEB.ROLES().BROKER().InvokeGoodbye(
                source= 'CheckOut@Host',
                session= session.ToInterface(),
                message= goodbye.GetStr('Message'))
        
