# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union

from PW_AWS.AWS import AWS
from SESSION import SESSION
from TALK import TALK
from PW_UTILS.HANDLER import HANDLER
from pollyweb import UTILS
from PROMPT_REPLY import PROMPT_REPLY
from pollyweb import LOG


class TALKER_BASE(HANDLER):
    '''😃 Talker
    * https://quip.com/J24GAMbu7HKF/-Talker'''
    

    # ✅ DONE
    @classmethod
    def Talks(cls):
        '''👉 Stored talks.
        * TODO: Consider keeping only the active ones.'''
        return AWS.DYNAMO('TALKS')


    # ✅ DONE
    @classmethod
    def NewTalk(cls, session:SESSION, script:str, context:any=None) -> TALK:
        '''👉 Inserts a new talk based on the script.'''

        talk = TALK.New(
            session= session, 
            context= context) 
        
        # Parse the script.
        talk.ParseScript(script)

        # Save to database.
        item = cls.Talks().Insert(talk)

        # Cast.
        return TALK(item)


    # ✅ DONE
    @classmethod
    def RequireTalk(cls, talkID:str) -> TALK:
        '''👉 Gets the stored talk.'''
        LOG.Print(f'😃 TALKER.RequireTalk()', f'{talkID=}')
        
        UTILS.RequireArgs([talkID])
        #UTILS.MatchUUID(talkID)

        item = cls.Talks().Require(talkID)
        return TALK(item)


    @classmethod
    def ShowMenu(cls, talkID:str, message:str=None):
        LOG.Print(f'😃 TALKER.ShowMenu()', f'{talkID=}', f'{message=}')

        UTILS.RequireArgs([talkID])

        talk = cls.RequireTalk(talkID)
        talk.ResetTalkIndexAndStack()
        talk.VerifyTalkReset()

        prompt = talk.GetMenu(message= message)
        
        # Request the prompt to the broker.
        talk.InvokePrompt(
            session= talk.RequireSession(),
            prompt= prompt,
            stepID= 'TOP')
        

    @classmethod
    def HandleAnswer(cls, talk:Union[str,TALK], reply:PROMPT_REPLY):
        '''👉 Handles a user's reply to a previously sent prompt.'''

        LOG.Print(
            '😃 TALKER.HandleAnswer()', 
            f'talk=', talk, 
            f'reply=', reply)
        
        # Get the talk.
        if isinstance(talk, str):
            talk = cls.RequireTalk(talk)
        talk.Require()
        
        # Register the answer.
        talk.Answer(reply)
    