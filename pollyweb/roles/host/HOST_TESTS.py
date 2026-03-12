from PROMPT import PROMPT
from SESSION import SESSION
from TALK_EXEC import TALK_EXEC
from HOST import HOST
from PW_AWS.AWS_TEST import AWS_TEST
from PW_AWS.AWS import AWS
from MSG import MSG
from NLWEB import NLWEB
from pollyweb import LOG
from TALK import TALK


class HOST_TESTS(HOST, AWS_TEST):


    @classmethod
    def TestVerifySession(cls):
        host = 'any-host.org'

        cls.ResetAWS(host)
        
        cls.MOCKS().HOST().MockHost()

        brokerEvent = MSG({
            'Header':{ 'From':'any-broker.org' }, 
            'Body':{ 'SessionID':'<session-uuid>' }})
        cls.VerifySession(event=brokerEvent)

        walletEvent = MSG({
            'Header':{'From':'any-broker.org'}, 
            'Body':{'SessionID':'<session-uuid>'}
        })
        cls.VerifySession(event=walletEvent, fromWallet=True)
        with cls.AssertValidation():
            cls.VerifySession(event=walletEvent, fromPalmist=True)
        with cls.AssertValidation():
            cls.VerifySession(event=walletEvent, fromWallet=True, fromPalmist=True)
        
        palmistEvent = {
            'Body':{
                'Broker': 'any-broker.org', 
                'SessionID': '<session-uuid>'
            }}
        cls.VerifySession(event=palmistEvent, fromPalmist=True)
        with cls.AssertValidation():
            cls.VerifySession(event=palmistEvent)
        with cls.AssertValidation():
            cls.VerifySession(event=palmistEvent, fromWallet=True)
        with cls.AssertValidation():
            cls.VerifySession(event=palmistEvent, fromWallet=True, fromPalmist=True)


    @classmethod
    def TestAbandoned(cls):
        
        cls.ResetAWS()

        cls.MOCKS().HOST().MockHost()
        cls.MOCKS().DYNAMO('SESSIONS').MatchCount(1)

        cls.HandleAbandoned({
            'Header': {
                'From': 'any-broker.org',
                'To': 'any-host.org',
                'Subject': 'Abandoned@Host'
            },
            'Body': {
                "SessionID": "<session-uuid>"
            }
        })
        cls.MOCKS().DYNAMO('SESSIONS').MatchCount(0)


    @classmethod
    def TestCheckIn(cls):

        vault = 'any-vault.org'
        broker = 'any-broker.org'

        cls.ResetAWS()

        cls.MOCKS(vault).VAULT().MockVault()
        cls.MOCKS(vault).DYNAMO('BINDS').MatchCount(1)
        cls.MOCKS(vault).DYNAMO('SESSIONS').MatchCount(1)

        cls.MOCKS(broker).BROKER().MockBroker()

        e = {
            "Header": {
                "From": broker,
                "To": vault,
                "Subject": "CheckIn@Host"
            },
            "Body": {
                "SessionID": "61738d50-d507-42ff-ae87-48d8b9bb0e5a",
                "Code": "pollyweb.org/HOST",
                "Locator": "<locator>",
                "Language": "en-us",    
                "Binds": [
                    "<bind-uuid>"
                ],
                "Tokens": [
                    "125a5c75-cb72-43d2-9695-37026dfcaa48",
                    "bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc"
                ]
            }
        }
        
        cls.SetDomain(vault)
        
        cls.HandleCheckIn(e)
        cls.MOCKS(vault).DYNAMO('SESSIONS').MatchCount(2)

        cls.HandleCheckIn(e) # Support at-least-once
        cls.MOCKS(vault).DYNAMO('SESSIONS').MatchCount(2)


    @classmethod
    def TestCheckOut(cls):

        broker = 'any-broker.org'
        host = 'any-host.org'
        
        cls.ResetAWS()        

        cls.MOCKS(broker).BROKER().MockBroker()
        cls.MOCKS(host).HOST().MockHost()
        cls.MOCKS(host).DYNAMO('SESSIONS').MatchCount(1)

        cls.HandleCheckOut({
            'Header':{ 
                'From': broker,
                'To': host,
                'Subject': 'CheckOut@Host'
            }, 
            'Body':{ 
                'SessionID': '<session-uuid>' 
            }
        })

        cls.MOCKS(host).DYNAMO('SESSIONS').MatchCount(1)


    @classmethod
    def TestDownload(cls):

        host = 'any-host.org'
        broker = 'any-broker.org'
        cls.ResetAWS()

        cls.MOCKS(host).HOST().MockHost(host)
        
        resp = cls.HandleDownload({
            "Header": {
                "From": broker,
                "To": host,
                "Subject": "Download@Host"
            },
            "Body": {
                "SessionID": "<session-uuid>",    
                "FileID": "bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc"
            }
        })

        cls.SetDomain(host)
        cls.AssertEqual(resp, {
            'Name': 'any-file.pdf', 
            'Serialized': '<serialized>'
        })


    @classmethod
    def TestFound(cls):

        cls.ResetAWS()

        cls.MOCKS().HOST().MockHost()
        
        cls.HandleFound({
            "Header": {
                "To": "any-host.org",
                "Subject": "Found@Host"
            },
            "Body": {
                "Broker": "any-broker.org",
                "SessionID": '<session-uuid>',    
                "DeviceID": "MY-DEVICE",
                "Scanner": "airport.any-nation.org"
            }
        })


    @classmethod
    def TestUpload(cls):

        cls.ResetAWS()
        
        cls.MOCKS().HOST().MockHost()
                
        resp = cls.HandleUpload({
            "Header": {
                "From": "any-broker.org",
                "To": "any-host.org",
                "Subject": "Upload@Host"
            },
            "Body": {
                "SessionID": "<session-uuid>",        
                "Name": "a.jpg",
                "Serialized": "bisYfsHkJIyudS/O8FQOWpEdK"
            }
        })

        cls.AssertEqual(resp, None)


    @classmethod
    def TestTalker(cls):

        broker = 'any-broker.org'
        host = 'any-host.org'

        cls.ResetAWS()

        cls.MOCKS().BROKER().MockBroker(broker)
        cls.MOCKS().HOST().MockHost(host)

        cls.HandleTalker({
            "Header": {
                "From": "any-broker.org",
                "To": "any-host.org",
                "Subject": "Talker@Host"
            },
            "Body": {
                "SessionID": "<session-uuid>",        
                "Name": "a.jpg",
                "Serialized": "bisYfsHkJIyudS/O8FQOWpEdK"
            }
        })


    @classmethod
    def _mockAnswerExec(cls, arg):
        pass


    @classmethod
    def _mockSession(cls) -> SESSION:
        return SESSION.New(
            host= 'any-host.org',
            locator= 'any-locator',
            broker= 'any-broker.org',
            sessionID='<session-uuid>')


    @classmethod
    def _mockTalk(cls, session:SESSION) -> TALK:
        
        cls.MOCKS().SYNCAPI().MockSyncApi('any-host.org')
        
        script = '\n'.join([
            '# Order workflow.',
            '💬|Order:',
            '- SHARE|pollyweb.org/PROFILE/NAME/FRIENDLY',
            '- RUN|Items',
            '- CHARGE|{amount}',
            '- INFO|Wait...',
            '',
            'Items:',
            '- INT|Product code?',
            '- CONFIRM|{confirm}',
            '- REPEAT|Anything else?'
        ])

        talk = NLWEB.BEHAVIORS().TALKER().NewTalk(
            session= session,
            script= script)

        # We're not prepared to test the executions, so let's ignore that.
        TALK_EXEC.Exec = cls._mockAnswerExec

        NLWEB.ROLES().HOST().SESSIONS()._table().Insert({ 
            'ID': f'{session.RequireBroker()}/{session.RequireSessionID()}',
            'Broker': session.RequireBroker(),
            'SessionID': session.RequireSessionID(),
            'Locator': session.RequireLocator(),
            'Talk': talk.RequireID()
        })

        return talk


    @classmethod
    def TestReply(cls):
        
        cls.ResetAWS()

        session = cls._mockSession()
        talk = cls._mockTalk(session)

        prompt = PROMPT.New(
            format= 'INFO',
            message= 'dummy')

        talk.SavePrompt(
            prompt= prompt,
            session= session,
            stepID= '1.0')
        
        cls.HandleReply({
            "Header": {
                "From": "any-broker.org",
                "To": "any-host.org",
                "Subject": "Reply@Host"
            },
            "Body": {
                "SessionID": session.RequireID(),   
                "PromptID": prompt.RequirePromptID(),
                "Result": "OK",
                "Answer": '1'
            }
        })
        

    @classmethod
    def TestPrompted(cls):

        cls.ResetAWS()

        session = cls._mockSession()
        talk = cls._mockTalk(session)

        #cls.MOCKS(host).HOST().MockHost(host)

        prompt1 = PROMPT.New(
            format= 'INT',
            message= 'my-message',
            default= '123')

        talk.SavePrompt(
            prompt= prompt1,
            session= session,
            stepID= '1.0')
        
        resp = cls.HandlePrompted({
            "Header": {
                "From": 'any-broker.org',
                "To": 'any-host.org',
                "Subject": "Prompted@Host",
                "Correlation": "<correlation-uuid>"
            },
            "Body": {
                "SessionID": "<session-uuid>",    
                "PromptID": prompt1.RequirePromptID()
            }
        })

        resp.RemoveAtt('PromptID')
        cls.AssertEqual(resp, {
            'Format': 'INT',
            'Message': 'my-message',
            'Default': '123',
            'Results': ['OK', 'CANCEL']
        })


    @classmethod
    def TestAllHost(cls):
        LOG.Print('HOST_TESTS.TestAllHost() ==============================')

        cls.TestVerifySession()
        cls.TestAbandoned()        
        cls.TestCheckIn()
        cls.TestCheckOut()
        
        cls.TestPrompted()
        cls.TestDownload()
        cls.TestFound()
        
        cls.TestUpload()
        cls.TestTalker()
        
        cls.TestReply()
    