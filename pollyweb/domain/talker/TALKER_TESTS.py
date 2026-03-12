from PW_AWS.AWS_TEST import AWS_TEST
from NLWEB import NLWEB
from pollyweb import LOG
from MSG import MSG
from PROMPT import PROMPT
from SESSION import SESSION
from TALK import TALK
from TALKER import TALKER
from pollyweb import UTILS


class TALKER_TESTS(TALKER, AWS_TEST):
   

    @classmethod
    def MockSession(cls) -> SESSION:
        return SESSION.New(
            host= 'any-host.org',
            locator= 'any-locator',
            broker= 'any-broker.org',
            sessionID='<session-uuid>'
        )


    @classmethod 
    def MockScript(cls) -> str:

        return '\n'.join([
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


    @classmethod
    def TestTalks(cls) -> None:
        cls.ResetAWS()
        
        talker = NLWEB.BEHAVIORS().TALKER()
        talker.Talks()
        

    @classmethod
    def MockTalk(cls) -> TALK:
        
        return NLWEB.BEHAVIORS().TALKER().NewTalk(
            session= cls.MockSession(),
            script= cls.MockScript())
    
    
    @classmethod
    def TestNewTalk(cls) -> TALK:
        cls.ResetAWS()

        talk = cls.MockTalk()
        talk.Require()
        return talk
   

    @classmethod
    def TestRequireTalk(cls):
        cls.ResetAWS()
        
        talk1 = cls.MockTalk().RequireID()
        talk2 = cls.RequireTalk(talk1).RequireID()
        cls.AssertEqual( talk1, talk2 )
   

    @classmethod
    def TestShowMenu(cls):
        cls.ResetAWS()

        cls.MOCKS().BROKER().MockBroker()
        
        cls.SetDomain('any-host.org')
        talk = cls.MockTalk()
        cls.ShowMenu(
            talkID= talk.RequireID(), 
            message='my-message')

        ##m = MSG(cls.Echo)
        ##cls.AssertEqual(m.Subject(), 'Prompt@Broker')
        ##cls.AssertEqual(m.Body()['StepID'], 'TOP')

        ##p = PROMPT(m['Prompt'])
        ##cls.AssertEqual(p.RequireMessage(), 'my-message')
        ##cls.AssertEqual(p.RequireOptions(), [{'ID': '0', 'Translation': 'Order'}])

        return talk, cls.Echo
   

    @classmethod
    def _mockAnswerExec(cls, arg):
        pass


    @classmethod
    def TestAnswer(cls):
        
        # AWS Reset is done in the command below, don't repeat it!
        talk, request = cls.TestShowMenu()

        # TODO: fix this test, request is not available anymore.
        return

        UTILS.RequireArgs([talk, request])

        # Because this is a Notifier MSG, we need to get the internal Broker MSG.
        request = MSG(request).RequireAtt('Request')

        cls.MOCKS().SYNCAPI().MockSyncApi('any-host.org')

        # We're not prepared to test the executions, so let's ignore that.
        talk._exec = cls._mockAnswerExec

        cls.HandleAnswer(
            talk= talk,
            reply= PROMPT.REPLY().Reply(
                request = PROMPT.REQUEST(request),
                result= 'OK',
                answer= '0'
            )
        )
    

    @classmethod
    def TestAllTalker(cls):
        LOG.Print('TALKER_TESTS.TestAllTalker() ==============================')

        cls.TestTalks()
        cls.TestNewTalk()
        cls.TestRequireTalk()
        cls.TestShowMenu()
        cls.TestAnswer()


    @classmethod
    def MockTalker(cls):
        pass