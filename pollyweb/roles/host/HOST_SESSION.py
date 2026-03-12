# 📚 HOST_FILE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from pollyweb import LOG

from QUERY import CONSUMER_QUERY

from SESSION import SESSION

from TOKEN import TOKEN
from pollyweb import STRUCT
from PW_AWS.ITEM import ITEM
from MSG import MSG
from pollyweb import UTILS
from NLWEB import NLWEB


class HOST_SESSION(ITEM):
    ''' 🪣 https://quip.com/s9oCAO3UR38A#temp:C:TDD20456e042b3f43d49a73e0f92 
    {
        "Broker": "any-domain.com",
        "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",
        "Code": "pollyweb.org/THING",
        "Host": "any-host.org",
        "Locator": "MY-THING-ID"
        "Language": "en-us",
        "SessionTime": "2018-12-10T13:45:00.000Z",
        "Status": "CHECKING-OUT",
        "Talk": None,
        "Queries": [{
            "Code": "...",
            "Vaults": [
                
            ]
        }]
    }
    '''


    @classmethod
    def HOST(cls):
        return NLWEB.ROLES().HOST()
    

    def AddQuery(self, query:CONSUMER_QUERY):
        
        UTILS.AssertIsType(query, CONSUMER_QUERY)
        query.VerifyConsumerQuery()

        # Add the query codes to the session.
        code = query.RequireCode()
        self.AppendToAtt('Queries', code)

        self.UpdateItem()


    def AddTokens(self, tokens:list[TOKEN]):
        UTILS.RequireArgs(tokens)

        # Add the token to the session.
        for token in tokens:
            token.VerifyToken()
            self.AppendToAtt('Tokens', token)

        self.UpdateItem()


    def RequireLanguage(self):
        return self.RequireStr('Language')

    def RequireQueries(self) -> list[STRUCT]:
        return self.ListStr('Queries', require=True)
    
    def RequireBinds(self) -> list[str]:
        return self.ListStr('Binds', require=True)
    
    def RequireBroker(self) -> str:
        return self.RequireStr('Broker')
    
    def RequireSessionID(self) -> str:
        return self.RequireStr('SessionID')
        
    def RequireHost(self) -> str:
        return self.RequireStr('Host')

    def RequireCode(self) -> str:
        '''👉 Code that started the session.'''
        return self.RequireStr('Code')
    
    def RequireLocator(self) -> str:
        '''👉 Locator that started the session.'''
        return self.RequireStr('Locator')

    def HasTalk(self) -> bool:
        return self.ContainsAtt('Talk')

    def RequireTalk(self) -> str:
        return self.RequireStr('Talk')
    

    def VerifyQuery(self, code:str) -> None:
        ''' Verify if this code was asked for in this session.'''
        
        UTILS.AssertIsAnyValue(
            value= code, 
            options= self.RequireQueries(), 
            msg= 'Verify if this code was asked for in this session.')


    def CreateNewTalk(self):
    
        # Verify if the locator is registered.
        locator = self.HOST().LOCATORS().RequireLocator(
            code = self.RequireCode(), 
            locator = self.RequireLocator())

        # Get the talker of the locator.
        talkerID = locator.RequireTalker()
        talker = self.HOST().TALKERS().RequireTalker(talkerID)
        
        # Create a new talk.
        talk = NLWEB.BEHAVIORS().TALKER().NewTalk(
            session= self.ToInterface(),
            script= talker.RequireScript())
        
        # Update the session with the new talk.
        self["Talk"] = talk.RequireID()
        self.UpdateItem()


        
        
    def VerifyHostSession(self):
        '''👉️ Checks for Broker, SessionID, Host, and Locator.'''
        self.RequireBroker()
        self.RequireLocator()
        self.RequireSessionID()
        self.RequireHost()


    def ShowTalker(self):
        LOG.Print(f'🤗 HOST.SESSION.ShowTalker()', self)

        if self.RequireLocator() == 'crud':
            # Crud behaviour.
            NLWEB.BEHAVIORS().CRUD().ShowMenu(
                session= self.ToInterface())
        else:
            # Normal talk.
            talkID = self.RequireTalk()
            UTILS.RequireArgs(talkID)
            
            NLWEB.BEHAVIORS().TALKER().ShowMenu(
                talkID= talkID, 
                message='How can I help?')


    def ToInterface(self) -> SESSION:
        return SESSION.New(
            host= NLWEB.CONFIG().RequireDomain(),
            locator= self.RequireLocator(),
            broker= self.RequireBroker(),
            sessionID= self.RequireSessionID())
    

    def ContinueTalk(self, msg:MSG) -> None:
        LOG.Print('🤗 HOST.SESSION.ContinueTalk()', msg)

        if not self.HasTalk():
            LOG.Print(
                '🤗 HOST.SESSION.ContinueTalk:', 
                'No talk available, quitting.')
            return
        
        LOG.Print('🤗 HOST.SESSION.ContinueTalk:', 'Continuing the talk...')
        talkID = self.RequireTalk()
        talk = NLWEB.BEHAVIORS().TALKER().RequireTalk(talkID= talkID)
        talk.HandleContinue(msg)


    def SetVaultID(self, vaultID):
        self['VaultID'] = vaultID

    def RequireVaultID(self):
        return self.RequireAtt('VaultID')