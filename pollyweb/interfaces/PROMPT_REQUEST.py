  
from __future__ import annotations
from PROMPT import PROMPT
from MSG import MSG


class PROMPT_REQUEST(MSG):
    '''
    "Body": {
        "SessionID": "125a5c75-cb72-43d2-9695-37026dfcaa48",
        "Prompt": {
            "PromptID": "27bcb372-fdf9-4bd6-bddd-e1b23cb888c9",        
            "Format": "ONE",
            "Message": "Which credit card to use?", 
            "Options": [
                {
                    "ID": "1",
                    "Translation": "Personal"
                },
                {
                    "ID": "2",
                    "Translation": "Business"
                }
            ],
            "Appendix": "308826e3-a3a2-471e-84fd-c673c2e42e38"
        }
    }'''

    def __init__(self, event):
        
        msg = MSG(event)
        msg.MatchSubject(
            subject='Prompt@Broker', 
            msg=f'Correct request in={str(msg)}',
            ignoreTo= True)

        super().__init__(event)
    
    
    def RequirePrompt(self) -> PROMPT:
        prompt = self.RequireAtt('Prompt')
        return PROMPT(prompt)
    

    

