
# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations
from typing import Union

from PW_AWS.AWS import AWS
from PW_AWS.ITEM import ITEM
from MSG import MSG
from PROMPT import PROMPT
from pollyweb import LOG
from PROMPT_REPLY import PROMPT_REPLY
from SESSION import SESSION
from pollyweb import UTILS


class TALK_PROMPT(ITEM):
    ''' 👉 Prompts and answers.
    {
        ID: <uuid>
        Broker: any-broker.org
        SessionID: <session-uuid>
        PromptedOn: <timestamp>
        StepID: 2.0
        Format: INFO
        Message: How can I help?
        Options: [A, B]
        AnsweredOn: <timestamp>
        Result: OK
        Answer: 123
    }
    '''


    @classmethod
    def APPENDIX(cls, obj):
        from TALK_APPENDIX import TALK_APPENDIX
        return TALK_APPENDIX(obj)


    @classmethod
    def _table(cls):
        return AWS.DYNAMO('PROMPTS')


    @classmethod
    def RequirePrompt(cls, promptID:str):
        '''👉 Returns the prompt with the given ID'''
        UTILS.AssertIsUUID(promptID, require=True)
        prompt = cls._table().Require(promptID)
        return cls(prompt)
    

    @classmethod
    def Insert(cls, stepID:str, session:SESSION, prompt:PROMPT) -> ITEM:
        '''👉 Called when the host sends a prompt to a user.'''

        UTILS.AssertIsType(stepID, str, require=True)
        
        SESSION.AssertClass(session, require=True)
        session.VerifySession()

        PROMPT.AssertClass(prompt, require=True)
        prompt.VerifyPrompt()

        item = cls({
            'ID': prompt.RequirePromptID(),
            'Session': {
                'Broker': session.RequireBroker(),
                'SessionID': session.RequireSessionID(),
            },
            'Input': { 
                'StepID': stepID,
                'Format': prompt.RequireFormat(),
                'Message': prompt.RequireMessage(),
                'Options': prompt.GetOptionList(),
                'Default': prompt.GetDefault(),
                'Appendix': prompt.GetAppendix(),
                'Locator': prompt.GetLocator()
            },
            'Output': {
                #'Result': None,
                #'Answer': None
            },
            'Trace': {
                'PromptedOn': UTILS.GetTimestamp(),
                #'AnsweredOn': None,
            }
        })

        # Cleanup empty properties.
        if item.GetAppendix().IsMissingOrEmpty():
            item.Input().RemoveAtt('Appendix', safe= True)
        if item.GetOptions() == []:
            item.Input().RemoveAtt('Options', safe= True)
        if item.Input().IsMissingOrEmpty('Locator'):
            item.Input().RemoveAtt('Locator', safe= True)
        
        return cls._table().Insert(item, days=1)

    
    def RequirePromptID(self):
        return self.RequireID()

    # --------------------
    # Input Group
    # --------------------

    def Input(self):
        return self.RequireStruct('Input')
    
    def RequireStepID(self):
        '''👉 Gets the step ID.'''
        return self.Input().RequireStr('StepID')
    
    def RequireFormat(self):
        return self.Input().RequireStr('Format')
    
    def RequireMessage(self) -> str:
        return self.Input().RequireStr('Message')
    
    def GetDefault(self) -> str:
        return self.Input().GetStr('Default')
    
    def GetLocator(self) -> str:
        return self.Input().GetStr('Locator')

    def GetOptions(self) -> list[Union[str,dict]]:
        return self.Input().GetList('Options')

    def LookupOptionKey(self, value:str) -> str:
        '''👉 Returns the optionKey of the option with the given title.'''
        options = self.GetOptions()
        for option in options:
            UTILS.AssertIsType(option, dict)
            value2 = list(option.values())[0]
            if value == value2:
                return list(option.keys())[0]
        LOG.RaiseException('Value not found in options!', f'{value=}', options)


    def GetOptionValues(self) -> list[str]:
        '''👉 Returns a list of human-readable values.
        * Hosts should not send dictionaries to wallets.
        * Instead, hosts should send only dictionary values, then lookup the answer key.
        Examples:
        * [x,y] -> [x,y]
        * [{A:x}, {B:y}] -> [x,y]
        '''

        if not self.Input().ContainsAtt('Options'):
            return None
        
        options = self.Input().GetList('Options')
        
        ret:list[str] = []
        for option in options:
            UTILS.AssertIsAnyType(option, [str,dict])

            if isinstance(option, str):
                ret.append(option)

            elif isinstance(option, dict):
                value = list(option.values())[0]
                ret.append(value)

        return ret
    
    def HasAppendix(self):
        return self.Input().ContainsAtt('Appendix')

    def GetAppendix(self):
        ret = self.Input().GetStruct('Appendix')
        return self.APPENDIX(ret)
    
    # --------------------
    # Session Group
    # --------------------

    def Session(self):
        return self.RequireStruct('Session')

    def MatchSession(self, broker:str, sessionID:str):
        self.Session().Match('Broker', broker)
        self.Session().Match('SessionID', sessionID)

    # --------------------
    # Trace Group
    # --------------------

    def Trace(self):
        return self.GetStruct('Trace')

    def MarkAsRetrieved(self, msg:MSG):
        '''👉 Make sure the prompt isn't retrieved twice.
        * If a broker tries to collect the prompt after the wallet, it will fail.
        * If a broker tries to collect the prompt before the wallet, the wallet will fail.
        '''

        if not self.IsMissingOrEmpty('RetrievedOn'):
            LOG.RaiseException('Security warning: prompt already retrieved!')

        self.Trace().RequireTimestamp('RetrievedOn', set=UTILS.GetTimestamp())
        self.Trace().RequireUUID('RetrievedBy', set=msg.RequireCorrelation())
        self.UpdateItem()
    
    # --------------------
    # Output Group
    # --------------------
    
    def Output(self):
        return self.RequireStruct('Output')
    
    def GetAnswer(self):
        '''👉 Gets or sets the answer.'''
        answer = self.Output().GetAtt('Answer')
        UTILS.AssertIsAnyType(answer, [str,int,list,float])
        return answer
    
    def SetAnswer(self, set):
        '''👉 Sets the answer.'''
        if set == None:
            self.Output().RemoveAtt('Answer', safe=True)
        else:
            UTILS.AssertIsAnyType(set, [str,int,list,float])
            self.Output().GetAtt('Answer', set=set)
    
    def GetData(self):
        '''👉 Gets or sets the shared content.'''
        return self.Output().GetStruct('Data')
    
    def SetData(self, set):
        '''👉 Gets or sets the shared content.'''
        if UTILS.IsNoneOrEmpty(set): 
            self.Output().RemoveAtt('Data', safe=True)
        else: 
            self.Output().GetStruct('Data', set=set)
    
    def RequireResult(self, set=None):
        '''👉 Gets or sets the result.'''
        return self.Output().RequireStr('Result', set=set)
    
    # --------------------
    # Others
    # --------------------

    def Answer(self, reply:PROMPT_REPLY):
        '''👉 Called when a user answers a prompt.'''
        LOG.Print('😃💬 TALK.PROMPTS.Answer()', reply)

        self.RequireResult(set= reply.RequireResult())
        self.SetAnswer(reply.GetAnswer())
        self.SetData(reply.GetData())
        self.Trace().DefaultTimestamp('AnsweredOn')

        if self.RequireFormat() in ['SHARED']: 
            if not self.Output().ContainsAtt('Data'):
                LOG.RaiseException('SHARED answers require a Data attribute.')


    def ToInterface(self):
        
        ret = PROMPT.New(
            format= self.RequireFormat(),
            message= self.RequireMessage(),
            default= self.GetDefault(),
            options= self.GetOptionValues(),
            appendix= self.GetAppendix().ToInterface(),
            locator= self.GetLocator())
        
        # Use the existing ID.
        ret.RequirePromptID(
            set= self.RequirePromptID())
        
        return ret