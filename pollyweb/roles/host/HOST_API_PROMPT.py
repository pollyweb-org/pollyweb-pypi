# 🤗 HOST

from pollyweb import LOG
from NLWEB import NLWEB
from PROMPT import PROMPT
from TALK_PROMPTS import TALK_PROMPTS
from pollyweb import UTILS
from NLWEB import NLWEB
from PROMPT_REPLY import PROMPT_REPLY
from PROMPT_SESSION import PROMPT_SESSION
from pollyweb import UTILS

from HOST_API_BASE import HOST_API_BASE


# ✅ DONE
class HOST_API_PROMPT(HOST_API_BASE):


    @classmethod
    def InvokePrompted(cls, host:str, sessionID:str, promptID:str) -> PROMPT:

        LOG.Print(
            '🤗 HOST.InvokeAppendix()', 
            f'domain= {NLWEB.CONFIG().RequireDomain()}',
            f'{host=}',
            f'{sessionID=}',
            f'{promptID=}')
        
        UTILS.RequireArgs([host, sessionID, promptID])
        UTILS.AssertIsUUID(sessionID)
        UTILS.AssertIsUUID(promptID)

        from WALLET import WALLET
        ret = WALLET.GetWallet().CallDomain(
            domain= host,
            subject= 'Prompted@Host',
            body= {
                "SessionID": sessionID,
                "PromptID": promptID
            })
        
        LOG.Print('🤗 HOST.InvokePrompted: returned prompt=', ret)
        
        ret = PROMPT(ret)
        ret.VerifyPrompt()

        return ret


    @classmethod
    def HandlePrompted(cls, event:dict) -> PROMPT:
        ''' 👱🚀 
        Header:
            From: any-broker.org
        Body: 
            SessionID: <uuid>    
            PromptID: <uuid>    
        '''
        LOG.Print('🤗 HOST.HandlePrompted()', event)

        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('Prompted@Host')

        # Validate the wallet's signature on inherited vaults.
        NLWEB.BEHAVIORS().HANDLER().TriggerPython('VerifyPrompted@Host', msg, session)

        # Get the prompt from the database.
        prompt = TALK_PROMPTS.HandlePrompted(
            msg=msg, 
            session=session)
        
        return prompt
        


    @classmethod
    def InvokeDownload(cls, host:str, sessionID:str, fileID:str):

        LOG.Print(
            '🤗 HOST.InvokeDownload()', 
            f'domain= {NLWEB.CONFIG().RequireDomain()}',
            f'{host=}',
            f'{sessionID=}',
            f'{fileID=}')
        
        from WALLET import WALLET
        
        UTILS.AssertIsUUID(sessionID)
        UTILS.AssertIsUUID(fileID)

        ret = WALLET.GetWallet().CallDomain(
            domain= host,
            subject= 'Download@Host',
            body= {
                "SessionID": sessionID,
                "FileID": fileID
            })
        
        LOG.Print('🤗 HOST.InvokeDownload: returned file=', ret)
        
        return ret


    @classmethod
    def HandleDownload(cls, event):
        ''' 👱🚀 https://quip.com/s9oCAO3UR38A#temp:C:TDD828d0b17f0fa414ba67fa5eab 
        "Header": {
            "From": "any-broker.org"
        },
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",    
            "FileID": "bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc"
        }
        '''
        LOG.Print('🤗 HOST.HandleDownload()', event)

        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('Download@Host')

        # Validate the wallet's signature on inherited vaults.
        NLWEB.BEHAVIORS().HANDLER().TriggerPython('VerifyDownload@Host', msg, session)

        # Get the file.
        fileID = msg.RequireUUID('FileID')
        file = cls.FILES().RequireFile(fileID)

        # Validate the session of the file.
        file.MatchSession(
            broker= msg.RequireFrom(),
            sessionID= session.RequireSessionID())

        # Return the file info.
        ret = {
            "Name": file.RequireName()
        }

        serialized = file.GetSerialized()
        if not UTILS.IsNoneOrEmpty(serialized):
            ret["Serialized"] = file.GetSerialized()

        url = file.GetURL()
        if not UTILS.IsNoneOrEmpty(url):
            ret["URL"] = file.GetURL()

        return ret
            


    @classmethod
    def InvokeTalker(cls, source:str, to:str, sessionID:str):
        LOG.Print('🤵🐌🤗 HOST.InvokeTalker()', 
                  f'{source=}', f'{to}', f'{sessionID}')

        UTILS.RequireArgs([source, to, sessionID])
        UTILS.AssertIsUUID(sessionID)

        NLWEB.BEHAVIORS().MESSENGER().Push(
            source=source, 
            to=to,
            subject= 'Talker@Host',
            body= { "SessionID": sessionID })
        

    @classmethod
    def HandleTalker(cls, event):
        ''' 🤵🐌 https://quip.com/s9oCAO3UR38A#temp:C:TDD7f08c68ca48949f19d0efc9bf 
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48"
        }
        '''
        LOG.Print('🤗 HOST.HandleTalker()', event)

        msg, session = cls.VerifySession(event)
        msg.MatchSubject('Talker@Host')

        session.ShowTalker()
        

    @classmethod
    def HandleUpload(cls, event):
        ''' 👱🚀 https://quip.com/s9oCAO3UR38A#temp:C:TDD35cfdaff99ec49bbb6bbba1f0 
        "Header": {
            "From": "any-broker.org"
        },
        "Body": {
            "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",        
            "Name": "a.jpg",
            "Serialized": "bisYfsHkJIyudS/O8FQOWpEdK"
        }
        '''
        LOG.Print('🤗 HOST.HandleUpload()', event)

        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('Upload@Host')

        msg.RequireStr('Name')
        msg.RequireStr('Serialized')

        NLWEB.BEHAVIORS().HANDLER().TriggerPython('VerifyUpload@Host', msg, session)

        cls.FILES().Insert(
            broker = msg.RequireFrom(),
            serialized = msg.RequireStr('Serialized'),
            sessionID = msg.RequireStr('SessionID'),
            name = msg.RequireStr('Name'))


    @classmethod
    def InvokeReply(cls, session:PROMPT_SESSION, reply:PROMPT_REPLY, domain:str):

        LOG.Print(
            '🤗 HOST.InvokeReply()', 
            f'domain= {NLWEB.CONFIG().RequireDomain()}',
            f'session=', session, 
            f'reply=', reply)
        
        from WALLET import WALLET
        
        session.VerifySession()
        reply.VerifyReply()

        body = reply.Copy()
        body["SessionID"] = session.RequireSessionID()

        WALLET.GetWallet().CallDomain(
            subject= 'Reply@Host',
            body= body,
            # The prompt could have come from a vault,
            #   so don't send to the session host;
            #   send it to the prompter instead.
            domain= domain)


    @classmethod
    def HandleReply(cls, event):
        ''' 👱🐌  
        Header:
            From: any-broker.org
        Body: 
            SessionID: 125a5c75-cb72-43d2-9695-37026dfcaa48        
            Result: OK
            Answer: [W,C]
            Request: <correlation-uuid>
        '''
        LOG.Print('🤗 HOST.HandleReply()', event)

        msg, session = cls.VerifySession(event, fromWallet=True)
        msg.MatchSubject('Reply@Host')

        NLWEB.BEHAVIORS().HANDLER().TriggerPython(
            'VerifyUpload@Host', msg, session)

        reply = PROMPT_REPLY(msg.Body())
        reply.VerifyReply()

        if session.RequireLocator() == 'crud':
            NLWEB.BEHAVIORS().CRUD().HandleAnswer(
                session= session,
                reply=reply)
        else:
            NLWEB.BEHAVIORS().TALKER().HandleAnswer(
                talk= session.RequireTalk(),
                reply= reply)
