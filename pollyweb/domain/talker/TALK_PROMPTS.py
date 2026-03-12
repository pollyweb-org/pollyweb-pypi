
from MSG import MSG
from PROMPT import PROMPT
from NLWEB import NLWEB
from pollyweb import LOG
from PROMPT_REPLY import PROMPT_REPLY
from SESSION import SESSION
from TALK_BASE import TALK_BASE
from TALK_PROMPT import TALK_PROMPT
from pollyweb import UTILS


class TALK_PROMPTS(TALK_BASE):
    '''👉 Dictionary [id,prompt] of prompts and answers.'''


    @classmethod
    def PROMPTS(cls):
        return TALK_PROMPT()


    def SaveBehaviour(self,
        prompt:PROMPT,
        stepID:str,
        result:str, 
        answer:str=None,
        data:dict=None):
        '''👉 Adds prompt+answer, for special behaviours.'''

        LOG.Print('😃💬 TALK.PROMPTS.SaveBehaviour()',
            f'shared= ', data)

        self.SavePrompt(
            session= self.RequireSession(),
            prompt= prompt,
            stepID= stepID)
        
        reply = PROMPT_REPLY.Reply(
            prompt= prompt,
            result= result, 
            answer= answer,
            data= data,
            dontValidate= True)
        
        self.SaveAnswer(reply)


    def SavePrompt(self, stepID:str, session:SESSION, prompt:PROMPT):
        '''👉 Saves the last prompt.'''

        UTILS.AssertIsType(stepID, str, require=True)
        PROMPT.AssertClass(prompt, require=True)
        SESSION.AssertClass(session, require=True)

        TALK_PROMPT.Insert(
            stepID= stepID,
            session= session,
            prompt= prompt)
        
        self.AddPrompt(prompt.RequirePromptID())
        self.UpdateItem()

        LOG.Print(
            '😃💬 TALK.PROMPTS.SavePrompt:',
            'Prompt added.', prompt.RequirePromptID())


    # ✅ DONE
    def SaveAnswer(self, reply:PROMPT_REPLY) -> TALK_PROMPT:
        '''👉 Saves the last answer.'''

        LOG.Print('😃💬 TALK.PROMPTS.SaveAnswer()', reply)

        PROMPT_REPLY.AssertClass(reply, require=True)

        # Get the prompt details.
        promptID = reply.RequirePromptID()
        prompt = self.PROMPTS().RequirePrompt(promptID)
        format = prompt.RequireFormat()
        reply.VerifyPrompt(format)
        LOG.Print('😃💬 TALK.PROMPTS.SaveAnswer: prompt=', prompt)
        
        if prompt.RequireFormat() in ['SELFIE', 'TOUCH', 'WAIT']:
            LOG.RaiseValidationException(
                'Nao allowed, [SELFIE,TOUCH,WAIT] should not be answered!', 
                prompt)
            
        if prompt.RequireStepID() == 'CRUD':
            # For CRUD, remove from the database and process in memory.
            prompt.Delete()
            LOG.Print('😃💬 TALK.PROMPTS.SaveAnswer: CRUD, deleted!')
            return prompt
        
        # Check if it's the last prompt.
        last = self.LastPrompt()
        UTILS.AssertEqual(
            given= prompt.RequirePromptID(),
            expect= last.RequirePromptID(),
            msg= 'Not allowed: only the last prompt can be answered!')
        
        # Add the answer.
        prompt.Answer(reply)
        
        # Save to the database.
        prompt.UpdateItem()
        self.UpdateItem()
        return prompt
        

    def RequirePrompts(self) -> list[str]:
        '''👉 Returns the prompt list.'''
        self.Default('Prompts', [])
        return self.ListStr('Prompts', require=True) 
    

    def AddPrompt(self, promptID:str):
        '''👉 Adds a the prompt to the list.'''
        UTILS.AssertIsUUID(promptID, require=True)
        self.Default('Prompts', [])
        return self.AppendToAtt('Prompts', [promptID]) 
    

    def LastPromptID(self) -> str:
        '''👉 Returns the last prompt ID.'''
        prompts = self.RequirePrompts()
        lastID = prompts[-1]
        return lastID


    def LastPrompt(self):
        '''👉 Returns the last prompt object.'''
        lastID = self.LastPromptID()
        return self.PROMPTS().RequirePrompt(lastID) 
    

    def InvokePrompt(self, session:SESSION, prompt:PROMPT, stepID:str):
        '''👉️ Saves the prompt in the talk, then invokes the broker.'''

        SESSION.AssertClass(session, require=True)
        PROMPT.AssertClass(prompt, require=True)
        UTILS.AssertIsType(stepID, str, require=True)

        # Save the prompt in the talk.
        self.SavePrompt(
            prompt= prompt,
            session= session,
            stepID= stepID)

        # Request the prompt to the broker.
        NLWEB.ROLES().BROKER().InvokePrompt(
            source='Talk@Talker',
            session= self.RequireSession(),
            promptID= prompt.RequirePromptID())
        

    @classmethod
    def HandlePrompted(cls, msg:MSG, session:SESSION):

        # Get the prompt.
        promptID = msg.RequireUUID('PromptID')
        prompt = TALK_PROMPT.RequirePrompt(promptID)
        prompt.MatchSession(
            broker= msg.RequireFrom(),
            sessionID= session.RequireSessionID())
        
        # Make sure the prompt isn't retrieved twice.
        interface = prompt.ToInterface()
        prompt.MarkAsRetrieved(msg)

        return interface