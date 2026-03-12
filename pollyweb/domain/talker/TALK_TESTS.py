from PROMPT import PROMPT
from PROMPT_REPLY import PROMPT_REPLY
from TALK import TALK
from PW_AWS.AWS_TEST import AWS_TEST
from SESSION import SESSION
from pollyweb import LOG
from TALKER_STEP import TALKER_STEP


class TALK_TESTS(TALK, AWS_TEST):
    

    @classmethod
    def MockSession(cls):
        return SESSION.New(
            host= 'any-host.org',
            locator= 'any-locator',
            broker= 'any-broker.org',
            sessionID='<session-uuid>')


    @classmethod
    def TestNew(cls):
        session = cls.MockSession()
        talk = cls.New(session= session)
        talk.Require()
        return talk
    

    @classmethod
    def TestSession(cls):
        talk = cls.TestNew()
        session = talk.RequireSession()
        cls.AssertEqual(session.RequireHost(), 'any-host.org')
        

    @classmethod
    def TestBroker(cls):
        talk = cls.TestNew()
        cls.AssertEqual(talk.RequireBroker(), 'any-broker.org')
    

    @classmethod
    def TestHost(cls):
        talk = cls.TestNew()
        cls.AssertEqual(talk.RequireHost(), 'any-host.org')
    

    @classmethod
    def TestSessionID(cls):
        talk = cls.TestNew()
        cls.AssertEqual(talk.RequireSessionID(), '<session-uuid>')
    

    @classmethod
    def TestGroups(cls):
        talk = cls.TestNew()
        cls.AssertEqual(talk.Groups(), [])


    @classmethod
    def _initParseScript(cls, lines:list[str]|str): 
        if lines is list[str]:
            lines = '\n'.join(lines)
        return cls.TestNew().ParseScript(lines)
    

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
    def TestParseScript(cls): 

        # Test single line script.
        talk = cls._initParseScript([
            '💬|Order:'
        ])
        cls.AssertEqual(len(talk.Groups()), 1)
        cls.AssertEqual(talk.Groups()[0].Title(), 'Order')

        # Test multi line script.
        talk = cls._initParseScript([
            '💬|Order:',
            '- SHARE|pollyweb.org/PROFILE/NAME/FRIENDLY',
            '- RUN|Items',
            '- CHARGE|{amount}',
            '- INFO|Wait...'
        ])
        cls.AssertEqual(len(talk.Groups()), 1)

        # Test a group.
        order = talk.Groups()[0]
        cls.AssertEqual(order.Title(), 'Order')
        cls.AssertEqual(order.Type(), 'TOP')
        cls.AssertEqual(len(order.Steps()), 4)
        
        # Test a step.
        share = order.Steps()[0]
        cls.AssertEqual(share.Format(), 'SHARE')
        cls.AssertEqual(share.FirstArg(), 'pollyweb.org/PROFILE/NAME/FRIENDLY')

        # Test a charge.
        charge = order.Steps()[2]
        cls.AssertEqual(charge.Obj(), {'ID': '0.2', 'Type': 'STEP', 'Parts': ['CHARGE', '{amount}']})
        cls.AssertEqual(charge.Format(), 'CHARGE')
        cls.AssertEqual(charge.FirstArg(), '{amount}')
        
        # Test a complex script with 2 groups.
        script = cls.MockScript()
        talk = cls._initParseScript(script)
        cls.AssertEqual(len(talk.Groups()), 2)
        cls.AssertEqual(talk.Groups()[0].Title(), 'Order')
        cls.AssertEqual(talk.Groups()[1].Title(), 'Items')
        cls.AssertEqual(talk.Groups()[1].Type(), 'PROC')

        return talk
    

    @classmethod
    def TestGetTalkGroup(cls):
        talk = cls.TestParseScript()

        cls.AssertEqual( talk.GetTalkGroup('0').Title(), 'Order' ) 
        cls.AssertEqual( talk.GetTalkGroup('1').Title(), 'Items' )

        with cls.AssertValidation():
            talk.GetTalkGroup('0.0') # Not a group.

        with cls.AssertValidation():
            talk.GetTalkGroup('9.0') # Invalid index.
    

    @classmethod
    def TestGetTalkProcedure(cls):
        talk = cls.TestParseScript()

        cls.AssertEqual( talk.GetTalkProcedure('Items').Title(), 'Items' ) 

        with cls.AssertValidation():
            talk.GetTalkProcedure('Order')
    

    @classmethod
    def TestGetTalkStep(cls):
        talk = cls.TestParseScript()

        cls.AssertEqual( talk.GetTalkStep('0.0').Format(), 'SHARE' ) 
        cls.AssertEqual( talk.GetTalkStep('0.2').Format(), 'CHARGE' )
        cls.AssertEqual( talk.GetTalkStep('0').Type(), 'TOP' )

        # Don't allow PROCs.
        cls.AssertEqual( len(talk.Groups()), 2 )
        with cls.AssertValidation():
            talk.GetTalkStep('1') 

        # Verify the step index inside the group.
        with cls.AssertValidation():
            talk.GetTalkGroup('0.9') # Invalid step index.


    @classmethod
    def TestParseTalkStep(cls):

        talk = cls.TestNew()
        step = TALKER_STEP({
            "ID": "0.2",
            "Type": "STEP",
            "Parts": []
        })

        def Verify(line:str, options=None, default=None, error=None):

            LOG.Print('TALK_TESTS.Verify()',
                f'{line=}', f'{error=}')
            
            # Prepare the given.
            parts = line.split('|')
            step["Parts"] = parts

            # Check the prompt's format.  
            given = None          
            if error:
                with cls.AssertValidation(error):
                    given = talk._parseStep(step)
                    LOG.Print('Should have raised an error!', 'given=', given)
                return
            else:
                given = talk._parseStep(step)

            # Prepare the expect.
            expect:PROMPT = PROMPT.New(
                format= parts[0], 
                message= 'msg',
                options= options,
                default= default)

            # Find differences.
            cls.AssertEqual(
                given= given.RemoveAtt('PromptID'),
                expect= expect.RemoveAtt('PromptID'))


        Verify('ONE|msg|Ignore,Call', options= ['Ignore','Call'])
        
        Verify('INT|msg|123', default= '123')
        Verify('INT|msg|123.23', error='INT default invalid!')
        Verify('INT|msg|x', error='INT default invalid!')
        
        Verify('QUANTITY|msg|123', default= '123')
        Verify('QUANTITY|msg|123.23', error='QUANTITY default invalid!')
        Verify('QUANTITY|msg|x', error='QUANTITY default invalid!')

        Verify('AMOUNT|msg|123', default= '123')
        Verify('AMOUNT|msg|123.23', default= '123.23')
        Verify('AMOUNT|msg|x', error='AMOUNT default invalid!')

        Verify('EAN|msg|123', error='EAN default invalid!')
        Verify('OTP|msg|123', error='OTP default invalid!')
        Verify('RATE|msg|123', error='RATE default invalid!')
        

    @classmethod
    def TestIndex(cls):
        talk = cls.TestNew()
        talk.SetIndex('x')
        cls.AssertEqual(talk.SetIndex(), 'x')


    @classmethod
    def TestGetNext(cls):
        '''
        0)   💬|Order:
        0.0) - SHARE|pollyweb.org/PROFILE/NAME/FRIENDLY
        0.1) - RUN|Items
        0.2) - CHARGE|{amount}
        0.3) - INFO|Wait...
        1)   Items:
        1.0) - INT|Product code?
        1.1) - CONFIRM|{confirm}
        1.2) - REPEAT|Anything else?
        '''
    
        talk = cls.TestParseScript()

        talk._Initialize()

        # On the top menu, choose ORDERS
        next = talk.GetNext(None, answer='Order').StepID()
        cls.AssertEqual(next, '0.0')

        # 1.0) - INT|Product code?
        # On product code, give a number.
        next = talk.GetNext('1.0', answer='<not a number>!' ).StepID()
        cls.AssertEqual(next, '1.1' )

        # On INFO, say OK and exit
        next = talk.GetNext(currentStep='0.3', answer=None)
        cls.AssertEqual(next, None)


    @classmethod
    def TestGetMenu(cls):

        talk = cls.TestParseScript()
        p = talk.GetMenu(message='my-message')

        cls.AssertEqual(p.RequireMessage(), 'my-message')
        cls.AssertEqual(p.RequireOptions(), ['Order'])


    @classmethod
    def _mockAnswerUpdate(cls):
        pass

    @classmethod
    def _mockAnswerExec(cls, arg):
        pass

    @classmethod
    def TestAnswer(cls):

        cls.MOCKS().ACTOR().MockActor()
        talk = cls.TestParseScript()
        
        # We don't have a table, so let's ignore the Update.
        talk.UpdateItem = cls._mockAnswerUpdate

        # We're not prepared to test the executions, so let's ignore that as well.
        talk.Exec = cls._mockAnswerExec
        
        session = SESSION.New(
            host= 'any-host.org',
            broker= 'any-broker.org',
            locator= 'any-locator',
            sessionID= '<session-uuid>')

        prompt = PROMPT.New(
            format= 'ONE',
            message= 'my-message', 
            options= ['A','B'])
        
        talk.SavePrompt(
            stepID= 'TOP',
            session= session,
            prompt= prompt)
        
        talk.Answer(
            PROMPT_REPLY.Reply(
                prompt= prompt,
                result= 'OK',
                answer= 'Order'))


    
    
    @classmethod
    def TestAllTalkerTalk(cls):
        LOG.Print('TALK_TESTS.TestAllTalkerTalk() ==============================')

        from TALK_PROMPT_TESTS import TALK_PROMPT_TESTS
        TALK_PROMPT_TESTS.TestAllTalkPrompt()

        # BASE.
        cls.TestNew()
        cls.TestSession()
        cls.TestBroker()
        cls.TestHost()
        cls.TestSessionID()

        # PARSE.
        cls.TestGroups()
        cls.TestParseScript()
        cls.TestGetTalkGroup()
        cls.TestGetTalkProcedure()
        cls.TestGetTalkStep()
        cls.TestParseTalkStep()

        # INDEX.
        cls.TestIndex()
        cls.TestGetNext()

        # EXEC
        cls.TestGetMenu()
        cls.TestAnswer()
        
