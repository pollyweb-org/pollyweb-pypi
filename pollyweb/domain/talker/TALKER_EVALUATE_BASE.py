from pollyweb import LOG
from pollyweb import STRUCT
from SESSION import SESSION
from TALKER_STEP import TALKER_STEP
from TALK_PROMPT import TALK_PROMPT
from pollyweb import UTILS 


class TALKER_EVALUATE_BASE(STRUCT):
    '''
    Example: 
        Function: any-talker-function-name
        Context: {}
        Session: 
            Host: atm.any-fintech.org
            Locator: cash-machine
            Broker: any-broker.org
            SessionID: 2ca481fb-d626-410c-8073-7b5de2979dd3
        Prompts: {}
        Result: None
    '''

    @classmethod
    def New(cls,
        step:TALKER_STEP, talkID:str, function:str, 
        context:dict, session:SESSION, answers:list[str]):

        UTILS.RequireArgs([step, talkID, function])
        SESSION.AssertClass(session, require=True)
        UTILS.AssertIsType(answers, list)
        TALKER_STEP.AssertClass(step)

        item = {
            'TalkID': talkID,
            'Function': function,
            'Step': step,
            'Session': session,
            'Context': context,
            'Prompts': answers,
            'Result': None
        }
        item = cls(item)
        return item
    

    def RequireTalkID(self):
        return self.RequireStr('TalkID')


    def RequireStep(self):
        step = self.RequireStruct('Step')
        step = TALKER_STEP(step)
        return step


    def RequirePrompts(self):
        '''👉 Returns all the user's answers in the talk/session as a STRUCT.'''
        return self.ListStr('Prompts', require=True)
    

    def RequireAnswerList(self):
        '''👉 Returns all the user's answers in the talk/session as a LIST.'''
        return self.RequirePrompts()
    

    def LastAnswer(self):
        '''👉 Returns the user's last answer.'''
        answers = self.RequireAnswerList()
        LOG.Print('ANSWERS:', answers)
        promptID = answers[-1]
        prompt = TALK_PROMPT.RequirePrompt(promptID)
        return prompt.GetAnswer()


    def LastShareOf(self, code:str):
        '''👉 Returns the user's last share of a code.'''
        answers = self.RequireAnswerList()
        for i in range(len(answers)-1, 0, -1):
            promptID = answers[i]
            answer = TALK_PROMPT.RequirePrompt(promptID)
            if answer.RequireFormat() == 'SHARE':
                shared = answer.GetData()
                if shared.RequireStr('Code') == code:
                    return shared
        LOG.RaiseException('Code not shared yet!', code)


    def RequireSession(self) -> SESSION:
        session = self.RequireStruct('Session')
        session = SESSION(session)
        session.VerifySession()
        return session
    

    def RequireContext(self):
        return self.RequireStruct('Context')
    

    def RequireFunction(self):
        return self.RequireStr('Function')
    
    
    def RequireResult(self):
        return self.RequireAtt('Result')
    