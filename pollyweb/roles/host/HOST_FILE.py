# 📚 HOST_FILE

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.ITEM import ITEM
from pollyweb import UTILS
from pollyweb import LOG


class HOST_FILE(ITEM):
    ''' 🪣 https://quip.com/s9oCAO3UR38A#temp:C:TDD026a3fce1988455796a1a4621 
    {
        ID: bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc
        Broker: any-broker.org
        SessionID: 125a5c75-cb72-43d2-9695-37026dfcaa48
        Name": a.jpg
        Serialized: bisYfsHkJIyudS/O8FQOWpEdK
        URL: "https://..."
    }
    '''


    def RequireFileID(self, msg:str=None) -> str:
        '''👉 The ID of the file.'''
        return self.RequireStr('ID', msg=msg)

    def RequireName(self, msg:str=None) -> str:
        '''👉 The name of the file.'''
        if not self.IsMissingOrEmpty('Name'):
            ret = self.RequireStr('Name', msg=msg)
        else:
            url = self.GetURL()
            ret = UTILS.OS().File(url).GetName()

        LOG.Print('🤗📄 HOST.FILE.RequireName: returning=', ret)
        return ret
    
    def RequireBroker(self, msg:str=None) -> str:
        '''👉 The broker that created the file, if not shared.'''
        return self.RequireStr('Broker', msg=msg)
    
    def RequireSessionID(self, msg:str=None) -> str:
        '''👉 The session where the file was created, if not shared.'''
        return self.RequireUUID('SessionID', msg=msg)
    
    def GetSerialized(self) -> str:
        '''👉 The serialized content of the file.'''
        return self.GetStr('Serialized')        
    
    def RequireSerialized(self, msg:str=None) -> str:
        '''👉 The serialized content of the file.'''
        return self.RequireStr('Serialized', msg=msg)        
    
    def GetURL(self) -> str:
        '''👉 The external location of the file.'''
        return self.GetStr('URL')  
    
    def RequireURL(self, msg:str=None) -> str:
        '''👉 The external location of the file.'''
        return self.RequireStr('URL', msg=msg)  
    
    def MatchSession(self, broker:str, sessionID:str):
        if not self.IsMissingOrEmpty('SessionID'):
            self.Match('Broker', broker)
            self.Match('SessionID', sessionID)


    def VerifyFile(self):
        
        if not self.IsMissingOrEmpty('SessionID'):
            self.RequireBroker(msg='Session files require the broker.')
            self.RequireSessionID()

        if self.IsMissingOrEmpty('Serialized'):
            self.RequireURL(msg='External files require an URL.')
        else:
            self.RequireSerialized(msg='Non-external files required serialized content.')
            self.RequireName(msg='Serialized files require a name.')


    def Export(self):
        LOG.RaiseException('HOST_FILE.Export() not yet implemented.')