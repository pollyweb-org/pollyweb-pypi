# 📚 TALK

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from SESSION import SESSION
from TALKER_EVALUATE import TALKER_EVALUATE

from TALK_INDEX import TALK_INDEX
from TALK_BASE import TALK_BASE
from TALK_EXEC import TALK_EXEC
from TALK_PARSE import TALK_PARSE
from pollyweb import LOG

class TALK(TALK_EXEC, TALK_INDEX, TALK_PARSE, TALK_BASE):
    
    '''
    Conversation in a session.
    
    Usage: 
    * talk = TALK.New(broker, sessionID)
    * talk.ShowMenu(message=None)
    * talk.Answer(stepID:str, answer:any)
    
    Properties:
    ----------
    * `Prompts`: answer history
    * `Groups`: list of grouped steps
    * `Index`: current position in the script, or None if at the top menu
    * `Stack`: breadcrumb of procedure stack

    JSON example:
    ------------
    {
        ID: any-broker.org/125a5c75-cb72-43d2-9695-37026dfcaa48
        Session:
            Host: any-host.org
            Broker: any-broker.org
            SessionID: <session-uuid>
        Index: "1.2"
        Stack: [{
            Caller: "0.2"
            Procedure: 1
        }]
        Prompts: [
            <uuid>, 
            <uuid>
        ]
        Groups: [
            - ID: 0
            Title: Order
            Steps: [
                - ID: "0.1"
                    Type: STEP
                    Parts: [SHARE, pollyweb.org/PROFILE/NAME/FRIENDLY]
                - ID: "0.2"
                    Type: STEP,
                    Parts: [RUN, Items]
            ]
        ]
    }
    '''

    
    @classmethod
    def EVALUATE(cls, obj:dict):
        return TALKER_EVALUATE(obj)


    # ✅ DONE
    @staticmethod
    def New(session:SESSION, context:any=None) -> TALK:
        '''👉 Creates and returns a new talk placeholder in memory.'''

        talk = TALK({
            'ID': f'{session.RequireBroker()}/{session.RequireSessionID()}',
            'Context': context,
            'Session': session,
            'Prompts': [],
            'Groups': []
        })

        talk._Initialize()
        return talk
    

