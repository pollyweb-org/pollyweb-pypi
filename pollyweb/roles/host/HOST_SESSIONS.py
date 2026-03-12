# 📚 HOST_FILE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from HOST_SESSION import HOST_SESSION
from pollyweb import LOG
from SESSION import SESSION
from MSG import MSG
from pollyweb import UTILS
from NLWEB import NLWEB
from PW_AWS.AWS import AWS


class HOST_SESSIONS():
    

    @classmethod
    def HOST(cls):
        return NLWEB.ROLES().HOST()


    @classmethod
    def _table(cls):
        return AWS.DYNAMO('SESSIONS', keys=['Broker', 'SessionID'])
    

    @classmethod
    def RequireSession(cls, msg:MSG=None, broker:str=None, sessionID:str=None) -> HOST_SESSION:
        '''👉 Finds the session on the Sessions table.

        Usage options:
        * GetSession(msg=${Header:{From},Body:{SessionID}})
        * GetSession(broker, sessionID)

        Exceptions:
        * Raises an exception if the session doesn't exist.
        '''

        if msg == None:
            UTILS.RequireArgs([broker, sessionID])
            UTILS.AssertIsUUID(sessionID)

        session = cls.GetSession(
            msg=msg, 
            broker=broker, 
            sessionID=sessionID)
    
        # Ensure it still exists.
        if session.IsMissingOrEmpty():
            domain = NLWEB.CONFIG().RequireDomain()
            LOG.RaiseValidationException(
                f'Session.ID=({broker}/{sessionID}) not found '\
                f'on table=SESSIONS of host=({domain})!')

        return session 


    @classmethod
    def GetSession(cls, msg:MSG=None, broker:str=None, sessionID:str=None) -> HOST_SESSION:
        '''👉 Finds the session on the Sessions table.

        Usage options:
        * GetSession(msg=${Header:{From},Body:{SessionID}})
        * GetSession(broker, sessionID)
        '''
        if msg != None:
            broker = msg.RequireFrom()
            sessionID = msg.RequireAtt('SessionID')
        
        UTILS.RequireArgs([broker, sessionID])
        session = cls._table().GetItem({
            'Broker': broker,
            'SessionID': sessionID
        })

        '''
        domain = NLWEB.CONFIG().RequireDomain()
        toPrint = [
            HOST_SESSION(s).RequireID()
            for s in cls._table().GetAll()
        ]
        LOG.Print(f'  HOST_SESSION.{domain=}, {toPrint=}')
        '''

        return HOST_SESSION(session)
    

    @classmethod
    def HandleCheckIn(cls, msg:MSG):
        session = cls.GetSession(msg)
        if session.IsMissingOrEmpty():
            cls._HandleCheckInNew(msg=msg)
        else:
            cls._HandleCheckInExisting(msg=msg, session=session)


    @classmethod
    def _HandleCheckInNew(cls, msg:MSG):
    
        # Verify if the locator is registered (except crud).
        locator = msg.RequireStr('Locator')
        if locator != 'crud':
            cls.HOST().LOCATORS().RequireLocator(
                code = msg.RequireStr('Code'), 
                locator = locator)
        
        # Register the session.
        session = HOST_SESSION({
            'Broker': msg.RequireFrom(),
            'SessionID': msg.RequireStr('SessionID'),
            'Code': msg.RequireStr('Code'),
            'Host': NLWEB.CONFIG().RequireDomain(),
            'Locator': msg.RequireStr('Locator'),
            'Language': msg.RequireStr('Language'),
            'SessionTime': UTILS.GetTimestamp(),
            'Status': 'CHECKING-IN',
            'Talk': '<placeholder>',
            'Binds': msg.ListStr('Binds'),
            'Tokens': msg.ListStr('Tokens'),
            'Queries': []
        })
        session.VerifyHostSession()

        # Save the session to the database.
        session = cls._table().Insert(session)
        session = HOST_SESSION(session)
        
        if locator != 'crud':
            session.CreateNewTalk()

        NLWEB.BEHAVIORS().HANDLER().TriggerPython(
            'OnNewSession@Host', session)


    @classmethod
    def _HandleCheckInExisting(cls, msg:MSG, session:HOST_SESSION):
        session.Match('Code', msg.RequireStr('Code'))
        session.Match('Locator', msg.RequireStr('Locator'))


    @classmethod
    def IncludeVault(cls, session:SESSION, talkerID:str, context:any):

        UTILS.RequireArgs([talkerID, session])
        UTILS.AssertIsType(session, SESSION)

        dbSession = cls.GetSession(
            broker= session.RequireBroker(),
            sessionID= session.RequireSessionID())

        if dbSession.IsMissingOrEmpty():

            # Register the session.
            dbSession = HOST_SESSION({
                "Broker": session.RequireBroker(),
                "SessionID": session.RequireSessionID(),
                #"Code": msg.RequireStr('Code'),
                "Host": session.RequireHost(),
                "Locator": session.RequireLocator(),
                #"Language": msg.RequireStr('Language'),
                #"SessionTime": UTILS.Timestamp(),
                #"Status": "CHECKING-IN",
                #"Talk": talk.RequireID(),
                "Queries": []
            })
            dbSession.VerifyHostSession()

            # Save the session to the database.
            dbSession = cls._table().Insert(dbSession)
            dbSession = HOST_SESSION(dbSession)

        # Get the talker's script from the host's database.
        talker = NLWEB.ROLES().HOST().TALKERS().RequireTalker(talkerID)

        # Create a new talk.
        talk = NLWEB.BEHAVIORS().TALKER().NewTalk(
            session= session,
            script= talker.RequireScript(),
            context= context)
        
        # Register the active talk in the session.
        dbSession['Talk'] = talk.RequireID()
        dbSession.UpdateItem()

        return talk
        
       