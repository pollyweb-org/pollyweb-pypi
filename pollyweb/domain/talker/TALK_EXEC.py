# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union

from NLWEB import NLWEB
from PROMPT_REPLY import PROMPT_REPLY
from pollyweb import STRUCT
from TALKER_EVALUATE import TALKER_EVALUATE
from TALK_BASE import TALK_BASE
from TALK_INDEX import TALK_INDEX
from TALK_PROMPTS import TALK_PROMPTS
from TALKER_STEP import TALKER_STEP
from TALKER_GROUP import TALKER_GROUP
from PROMPT import PROMPT
from pollyweb import UTILS
from MSG import MSG
from pollyweb import LOG

class TALK_EXEC(TALK_INDEX, TALK_PROMPTS, TALK_BASE):
    '''😃 Executes the dialog in a talk.

    Methods:
    -------
    * `ShowMenu(message=None)`: show the main menu
    * `Answer(stepID, answer)`: saves the answer, and proceeds
    '''


    def GetMenu(self, message:str):
        LOG.Print(f'😃🧠 TALK.GetMenu(message={message})')
        
        UTILS.RequireArgs([message])
        self.Require()
        return self._getMenu(
            message= message)


    def HandleContinue(self, msg:MSG):
        '''👉 Continues from a message received by a Host.'''
        LOG.Print(
            f'😃🧠 TALK.EXEC.Continue():', 
            f'domain={NLWEB.CONFIG().RequireDomain()}',
            msg)

        UTILS.AssertIsType(msg, MSG)

        # If there's no index, then this is a test - abandon.
        if self.CurrentIndex() == None:
            return
        
        result = None
        if msg.RequireSubject() == 'Bound@Vault':
            binds = msg.GetList('Binds', mustExits=True)
            prompt = PROMPT.New(
                format= 'BIND',
                message= 'Bound@Vault')
            self.SaveBehaviour(
                stepID= self.CurrentIndex(),
                prompt= prompt,
                result= 'BOUND',
                data= binds)
            
        elif msg.RequireSubject() == 'Consume@Consumer':
            shared = msg.RequireStruct('Shared')
            answer = shared.RequireStr('Code')+':'+shared.RequireStr('Version')
            userdata = shared.RequireAtt('UserData')
            prompt = PROMPT.New(
                format= 'SHARE',
                message= 'Consume@Consumer')
            self.SaveBehaviour(
                prompt= prompt, 
                stepID= self.CurrentIndex(),
                result= 'SHARED',
                answer= answer,
                data= shared)
            
        elif msg.RequireSubject() == 'Accepted@Issuer':
            token = msg.Body()
            prompt = PROMPT.New(
                format= 'ISSUE',
                message= 'Accepted@Issuer')
            self.SaveBehaviour(
                prompt= prompt,
                stepID= self.CurrentIndex(),
                result= 'ACCEPTED',
                data= token)
            
        elif msg.RequireSubject() == 'WontShare@Consumer':
            result = 'NO'
            code = msg.RequireCode('Code')
            prompt = PROMPT.New(
                format= 'SHARE',
                message= 'WontShare@Consumer')
            self.SaveBehaviour(
                prompt= prompt,
                stepID= self.CurrentIndex(),
                result= 'NO',
                answer= code)
            
        elif msg.RequireSubject() == 'Verify@Consumer':
            prompt = PROMPT.New(
                format= 'SHARE',
                message= 'Verify@Consumer')
            self.SaveBehaviour(
                prompt= prompt,
                stepID= self.CurrentIndex(),
                result= 'SHARED',
                data= msg.Structs('Tokens'))
            
        elif msg.RequireSubject() == 'Paid@Seller':
            prompt = PROMPT.New(
                format= 'CHARGE',
                message= 'Paid@Seller')
            self.SaveBehaviour(
                prompt= prompt,
                stepID= self.CurrentIndex(),
                result= 'PAID',
                answer= msg.RequireStruct('Charge').RequireFloat('Amount'))

        elif msg.RequireSubject() in [
            'Order@Selfie',
            'Touched@Ephemeral',
            'Order@Transcriber'
        ]:
            # There's a protection against saving the answer.
            pass 

        else:
            LOG.RaiseException(f'TALKER.Continue():',
                f'Unexpected subject: {msg.RequireSubject()}')
            
        LOG.Print(f"😃🧠 TALK.EXEC.Continue:", "getting next...")
        next = self.GetNext(
            currentStep= self.CurrentIndex(), 
            answer= None,
            result= result)
        LOG.Print(f"😃🧠 TALK.EXEC.Continue:", "received next={next}")

        if not UTILS.IsNoneOrEmpty(next):
            LOG.Print(f"😃🧠 TALK.EXEC.Continue:", "executing next...")
            self.Exec(next)
        else:
            LOG.Print(f"😃🧠 TALK.EXEC.Continue:", "no other next step - exiting...")


    def Answer(self, reply:PROMPT_REPLY):
        '''👉 Updates the current group/step with the answer.'''

        LOG.Print(
            f"😃🧠 TALK.EXEC.Answer()",
            f'domain={NLWEB.CONFIG().RequireDomain()}',
            f'reply', reply)
        
        PROMPT_REPLY.AssertClass(reply, require=True)

        prompt = self.SaveAnswer(reply)

        if reply.RequireResult() == 'CANCEL':
            LOG.Print(
                f"😃🧠 TALK.EXEC.Answer:", 
                "the chat was cancelled - exiting...")
            NLWEB.ROLES().BROKER().InvokeGoodbye(
                source= 'Talk@Talker',
                session= self.RequireSession())
            return
        
        next = self.GetNext(
            currentStep= prompt.RequireStepID(), 
            answer= reply.GetAnswer(), 
            result= reply.RequireResult())

        if next != None:
            self.Exec(next)
        else:
            LOG.Print(f"😃🧠 TALK.EXEC.Answer:",
                "no other next step - exiting...")


    # ✅ DONE
    def _Evaluate(self, 
        step: TALKER_STEP,
        expression:str, 
        forceFunction:bool= False, 
        require:bool= False,
        msg:str=None) -> Union[str,any]:
        '''👉 Executes a trigger that returns the result of an evaluation.
        * Triggers must return { Result:any }
        '''

        LOG.Print(
            f'😃🧠 TALK.EXEC._Evaluate()', 
            f'domain={NLWEB.CONFIG().RequireDomain()}',
            f'{expression=}', 
            f'{forceFunction=}')
        
        # Verify.
        TALKER_STEP.AssertClass(step)
        
        if expression == None:
            return None

        if not expression.startswith('{') and not expression.endswith('}'):    
            if forceFunction==True:
                LOG.RaiseException(f'A function must be wrapped in {{}}!', msg)
            return expression

        function = expression.replace('{', '').replace('}', '')
        payload = TALKER_EVALUATE.New(
            step = step,
            talkID = self.RequireID(),
            function= function,
            context= self.GetContext(),
            session= self.RequireSession(),
            answers= self.RequirePrompts())

        # Raise an event to calculate what to do.
        result = self.Trigger('OnEvaluate@Talker', payload)
        if result == None and require == True:
            UTILS.Require(result)

        # Enhance the response.
        result = STRUCT(result)

        # Return the 'Result' attribute if there is one.
        if result.ContainsAtt('Result'): return result.RequireAtt('Result')
        # Otherwise, return the entire response.
        else: return result.Obj()


    def Exec(self, step:TALKER_STEP):
        '''👉 Allows the method to be overrided during tests.'''
        LOG.Print(f'😃🧠 TALK.EXEC.Exec(step={step})')
        self.ExecLogic(step=step)


    def ExecLogic(self, step:TALKER_STEP):
        '''👉 To allow for tests, don't call this directly - call Exec() instead.'''
        UTILS.RequireArgs([step])

        LOG.Print(
            f'😃🧠 TALK.EXEC.ExecLogic()', 
            f'domain={NLWEB.CONFIG().RequireDomain()}',
            f'ID={step.StepID()}', 
            f'Type={step.Type()}', 
            f'Title={step.GetStr("Title")}')

        currentIndex = self.CurrentIndex()
        self.UpdateIndex(step)

        if step.IsPrompt():
            self._execPrompt(step)

        elif step.IsBehaviour():
            self._execBehaviour(step)

        elif step.IsProcedure():
            self._ExecProcedure(step, currentIndex=currentIndex)

        elif step.Format() == 'EVAL':
            self._ExecEval(step)

        elif step.Format() == 'CASE':
            # Ignore, it's part of the EVAL.
            pass

        elif step.Format() == 'IF':
            self._execIf(step)

        elif step.Format() == 'MENU':
            self._execMenu(step)

        elif step.Format() == 'REPEAT':
            self._execRepeat(step)

        elif step.Format() == 'RUN':
            self._execRun(step)

        elif step.Format() == 'TOUCH':
            LOG.RaiseException('Not implemented, yet.')

        else:
            cmd = step.Format()
            LOG.RaiseException(f'Unexpected command=({cmd})')


    def _parseStep(self, step:TALKER_STEP) -> PROMPT:
        UTILS.RequireArgs([step])
        LOG.Print(f'😃🧠 TALK.EXEC._parseStep()', 
            f'domain={NLWEB.CONFIG().RequireDomain()}',
            f'ID={step.StepID()}', 
            f'Type={step.Type()}', 
            f'Format={step.Format()}', 
            f'Title={step.GetStr("Title")}')
                
        if not step.IsPrompt():
            LOG.RaiseException('Prompt expected!')
        
        format = step.Format()

        # Get the message.
        eval = step.FirstArg(msg='👉 Inform the message.')
        message = self._Evaluate(step, eval)
        UTILS.Require(message, msg=f'Message is required! Eval={eval}')

        # Parse the default.
        default = None
        if format in ['INT', 'QUANTITY', 'AMOUNT', 'EAN', 'OTP', 'RATE']:
            default = step.SecondArg(optional=True)

        # Parse the options for ONE|MANY.
        options = None
        if format in ['ONE', 'MANY']:
            options = step.SecondArg(msg='👉 Inform the options.')
            options = self._Evaluate(step, options)
        elif format in ['DOWNLOAD']:
            options = step.ThirdArg(optional=True)
            options = self._Evaluate(step, options)

        # Get the appendix for downloads and selfies.
        locator = None
        if format in ['SELFIE']:
            locator = step.SecondArg(msg='👉 Inform the locator.')
            locator = self._Evaluate(step, locator, require=True)

        appendix = None
        if format in ['DOWNLOAD']:
            appendix = step.SecondArg(msg='👉 Inform the appendix.')
            appendix = self._Evaluate(step, appendix, require=True)

            # Replace asset:
            if appendix.startswith('asset:'):
                assetID = appendix.replace('asset:', '').strip()
                appendix = None
                asset = NLWEB.ROLES().HOST().ASSETS().RequireAsset(assetID)
                locator = asset.RequireURL()

        if format == 'SELFIE':
            LOG.Print(f'😃🧠 TALK.EXEC._execPrompt()', 
                'Selfies are handled in asynchronous mode.')
            return      

        # Get the locator for Ephemerals.
        if format in ['TOUCH']:
            locator = step.SecondArg(msg='👉 Inform the locator.')
            self._Evaluate(step, locator, require=True)

            LOG.Print(f'😃🧠 TALK.EXEC._execPrompt()', 
                'Ephemerals are handled in asynchronous mode.')
            return

        prompt = PROMPT.New(
            format= format,
            message= message,
            options= options,
            default= default,
            appendix= appendix,
            locator= locator)
        
        return prompt


    def _execPrompt(self, step:TALKER_STEP):

        # Process the prompt.
        prompt= self._parseStep(step)
        if prompt == None:
            return

        # Request the prompt to the broker.
        self.InvokePrompt(
            prompt= prompt,
            session= self.RequireSession(),
            stepID= step.StepID())


    def _ExecProcedure(self, proc:TALKER_GROUP, currentIndex:str):
        
        LOG.Print(
            f"😃🧠 TALK.EXEC._ExecProcedure()",
            f'domain={NLWEB.CONFIG().RequireDomain()}',
            f'{currentIndex=}', 
            f'proc=', proc)

        if not proc.IsProcedure():
            LOG.RaiseException('Procedure expected!')

        # Add a stack call back for when a procedure ends.
        call = self.AddToStack(currentIndex=currentIndex, proc=proc)
        LOG.Print(f"😃🧠 TALK.EXEC._ExecProcedure:","adding call=", call)

        # Exeute the first step of the procedure
        next = proc.FirstStep()
        self.Exec(next)


    def _ExecEval(self, step:TALKER_STEP):
        LOG.Print('😃🧠 TALK.EXEC._ExecEval()', step)

        if step.Format() != 'EVAL':
            LOG.RaiseException('EVAL command expected!')
        
        group = self.GetTalkGroup(step)

        # Calculate the EVAL from a function.
        function = step.FirstArg(optional=True)
        if function != None:
            eval:str = self._Evaluate(step, function, forceFunction=True)
        else: # No function found, use the last answer
            eval:str = self.LastPrompt().GetAnswer()

        current = step
        depth = 0
        while True:

            next = group.NextStep(current)

            # Detect loops.
            depth = depth + 1
            if depth > 20:
                LOG.RaiseException(
                    f'Too deep, probably a loop!')
            if current == next:
                LOG.RaiseException(f'Loop detected')
            
            # Check if there are no CASES.
            if next == None or next.Format() != 'CASE':
                LOG.Print(
                    '😃🧠 TALK.EXEC._ExecEval:', 
                    'No CASE for the EVAL, executing the next step...')
                next = self.GetNext(
                    currentStep= step.StepID(), 
                    answer= None)
                self.Exec(next)
                return
            
                # Allow for an EVAL not to have CASEs, to be used as a post-processor.
                LOG.RaiseException(f'No CASE found for eval {eval}', step)
            
            elif next.FirstArg() == eval:
                procName = next.SecondArg()
                proc = self.GetTalkProcedure(procName)
                self.Exec(proc)

                LOG.Print(
                    '😃🧠 TALK.EXEC._ExecEval:', 
                    'Executed, quitting...',
                    f'{procName=}')
                return 
            
            else:
                current = next


    def _execIf(self, step:TALKER_STEP):
        
        LOG.Print(f"😃🧠 TALK.EXEC._execIf()")

        if step.Format() != 'IF':
            LOG.RaiseException('IF command expected!')
        
        function = step.FirstArg()
        trueProcName = step.SecondArg(optional= True)
        falseProcName = step.ThirdArg(optional= True)

        eval:bool = self._Evaluate(step, function, forceFunction=True)
        LOG.Print(f"😃🧠 TALK.EXEC._execIf: ", 
                  f'{function=}', f'{eval=}', f'{trueProcName=}', f'{falseProcName=}')

        if eval == True:
            if trueProcName != None:
                trueProc = self.GetTalkProcedure(trueProcName)
                self.Exec(trueProc)
                return 

        elif eval == False:
            if falseProcName != None:
                falseProc = self.GetTalkProcedure(falseProcName)
                self.Exec(falseProc)
                return
            
        else:
            LOG.RaiseException('True|False expected!', f'{eval=}', step)

        # There was a True or False without a follow.
        # > let's just move to the next step.
        next = self.GetNext(
            currentStep= step.StepID(), 
            answer= eval)
        if next != None:
            self.Exec(next)


    def _getMenu(self, message:str):
        ##LOG.Print(f'TALK_EXEC._showMenu(message={message})')

        UTILS.RequireArgs([message])

        # Initialize the talk.
        self._Initialize()

        # Send the top menus to the wallet.
        options = []
        for group in self.Groups():
            if group.IsTop():
                item = group.Title()
                ##LOG.Print(f'TALKER.TALK._showMenu(): item={item}')
                options.append(item)

        prompt = PROMPT.New(
            format= 'ONE',
            message= message,
            options= options)

        return prompt


    def _execMenu(self, step:TALKER_STEP):
        if step.Format() != 'MENU':
            LOG.RaiseException('MENU command expected!')
        
        message= step.FirstArg(optional=True)
        prompt = self._getMenu(message= message)

        # Request the prompt to the broker.
        self.InvokePrompt(
            prompt= prompt,
            stepID= 'TOP')
        

    def _execRepeat(self, step:TALKER_STEP):
        if step.Format() != 'REPEAT':
            LOG.RaiseException('REPEAT command expected!')
        
        # Validate of the repeat is the last call in a procedure with other steps.
        group = self.GetTalkGroup(step)
        
        if not group.IsProcedure():
            LOG.RaiseException(
                '💥 REPEAT can only be used in Procedures!',
                '👉 Move the repeatable code from the top menu to a procedure, and call it with "RUN|<proc>".')
            
        if len(group.Steps()) < 2:
            LOG.RaiseException(
                'Use REPEAT on procedures with at least 2 steps!')
            
        if len(group.Steps()) != (int(step.Position())+1):
            LOG.RaiseException('REPEAT should be the last step!')

        # If the REPEAT has a message.
        if step.FirstArg(optional=True) != None:
            # Prompt a confirmation on the wallet.
            self._execPrompt(step.ToConfirm())
        else:
            # Otherwise, just re-start from the begining of the group.
            self.Exec(group.FirstStep())


    def _execRun(self, step:TALKER_STEP):
        if step.Format() != 'RUN':
            LOG.RaiseException('RUN command expected!')
        
        procName = step.FirstArg()
        proc = self.GetTalkProcedure(procName)
        self.Exec(proc)


    def _execBehaviour(self, step:TALKER_STEP):
        if not step.IsBehaviour():
            LOG.RaiseException('Behaviour expected!')
        
        LOG.Print(f'😃🧠 TALK.EXEC.EXEC._execBehaviour()', 
                  f'command={step.Format()}')
        
        cmd = step.Format()
        source = 'Talk@Talker'
        
        if cmd == 'BINDABLE':
            first = step.FirstArg()
            ##LOG.Print(f'  TALK.EXEC._execBehaviour(): BINDABLE(first={first})')

            codeList = self._Evaluate(step, first)
            ##LOG.Print(f'  TALK.EXEC._execBehaviour(): BINDABLE(codeList={codeList})')

            if isinstance(codeList, str):
                codeList = codeList.replace('[','').replace(']','').split(',')
                ##LOG.Print(f'  TALK.EXEC._execBehaviour(): BINDABLE(codeList2={codeList})')

            NLWEB.ROLES().BROKER().InvokeBindable(
                source= source,
                session= self.RequireSession(),
                codes= codeList
            )

        # ✅ DONE
        elif cmd == 'CHARGE':

            # Get the amount
            first = step.FirstArg(msg='👉 Inform the value of the charge.')
            first = self._Evaluate(step, first)
            amount = float(first)

            # Get the currency
            currency = step.SecondArg(msg='👉 Inform the currency of the charge.')

            # Get the reason
            message = step.ThirdArg(msg='👉 Inform the message of the charge.')
            message = self._Evaluate(step, message)

            NLWEB.ROLES().SELLER().Charge(
                source= source,
                session= self.RequireSession(),
                message= message,
                amount= amount,
                currency= currency)
        

        elif cmd == 'GOODBYE':
            message = step.FirstArg(optional=True)
            message = self._Evaluate(step, message)

            NLWEB.ROLES().BROKER().InvokeGoodbye(
                source= source,
                session= self.RequireSession(),
                message= message)

        elif cmd == 'ISSUE':
            code = step.FirstArg()
            tokenID = step.SecondArg()

            tokenID = self._Evaluate(
                step= step,
                expression= tokenID, 
                forceFunction=True,
                msg= 'To issue tokens, you always need a function (not static values) '\
                    'because you need to create and store the token on your function.')

            NLWEB.ROLES().ISSUER().Offer(
                source= source,
                session= self.RequireSession(),
                code= code,
                tokenID= tokenID)
            
        elif cmd == 'CRUD':
            NLWEB.BEHAVIORS().CRUD().ShowMenu(
                session= self.RequireSession())

        elif cmd == 'REDIRECT':
            LOG.RaiseException('Not implemented!')

        elif cmd == 'RESUBSCRIBE':
            LOG.RaiseException('Not implemented!')

        # ✅ DONE
        elif cmd == 'REVOKE':
            tokenID = step.FirstArg()
            tokenID = self._Evaluate(step, tokenID, forceFunction=True)

            NLWEB.ROLES().ISSUER().Revoke(
                source= source,
                session= self.RequireSession(),
                tokenID= tokenID)

        # ✅ DONE
        elif cmd == 'SHARE':
            
            code = step.FirstArg()
            code = self._Evaluate(step, code)

            message = step.SecondArg(msg='👉 Inform the message of the share!')
            message = self._Evaluate(step, message)
            
            # Ask for all SHAREs at once.
            NLWEB.ROLES().CONSUMER().Query(
                session= self.RequireSession(),
                message= message,
                code= code)

        elif cmd == 'SUBSCRIBE':
            LOG.RaiseException('Not implemented!')
        
        else:
            LOG.RaiseException(f'Unexpected behaviour: {cmd}!')


  