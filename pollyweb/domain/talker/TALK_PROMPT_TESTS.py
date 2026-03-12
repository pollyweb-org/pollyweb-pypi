
# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from PW_AWS.AWS_TEST import AWS_TEST
from PROMPT import PROMPT
from TALK_PROMPT import TALK_PROMPT


class TALK_PROMPT_TESTS(TALK_PROMPT, AWS_TEST):
    
    
    @classmethod
    def TestInsert(cls):

        from TALK_TESTS import TALK_TESTS

        item = cls.Insert(
            stepID='1.0',
            session= TALK_TESTS.MockSession(),
            prompt= PROMPT.New(
                format= 'INT',
                message= 'my-message',
                default= '123'
            ))
        
        input = item.GetAtt('Input')
        cls.AssertEqual(input, {
            "StepID": "1.0", 
            "Format": "INT", 
            "Message": "my-message", 
            "Default": "123"
        })


    @classmethod
    def TestToInterface(cls):
        
        talkPrompt = TALK_PROMPT({
            "ID": "<uuid>",
            "Input": {
                "Format": "INT", 
                "Message": "my-message", 
                "Default": "123", 
                "Results": ["OK", "CANCEL"]
            }
        })
        
        interface = talkPrompt.ToInterface()
        
        cls.AssertEqual(interface, {
            "PromptID": "<uuid>",
            "Format": "INT", 
            "Message": "my-message", 
            "Default": "123", 
            "Results": ["OK", "CANCEL"]
        })


    @classmethod
    def TestAllTalkPrompt(cls):

        cls.TestInsert()
        cls.TestToInterface()