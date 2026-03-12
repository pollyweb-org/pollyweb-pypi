# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union
from NLWEB import NLWEB
from TALKER_GROUP import TALKER_GROUP

from pollyweb import UTILS
from TALK_BASE import TALK_BASE
from TALKER_STEP import TALKER_STEP
from pollyweb import LOG
from pollyweb import STRUCT


class TALK_STACK_ITEM(STRUCT):

    def RequireCaller(self):
        return self.RequireStr('Caller')
    
    def RequireProcedure(self):
        return self.RequireStr('Procedure')

    def RequireProcTitle(self):
        return self.RequireStr('ProcTitle')

    def __to_yaml__(self, indent:int=0):
        return (' '*indent) +\
            f'{self["Caller"]} >> {self.RequireProcedure()}: {self.RequireProcTitle()}'


class TALK_STACK(STRUCT):

    def ToYamlArray(self):
        '''👉 Returns an array of strings representing the stack.'''
        items = self.GetList()
        items = TALK_STACK_ITEM.FromStructs(items)
        yaml = [i.ToYaml() for i in items]
        return yaml
    
    def MatchEmpty(self):
        '''👉 Verifies if the stack is empty.'''
        UTILS.AssertEqual(self.Obj(), [], msg='😡 Stubborn!')

    def AddCall(self, currentIndex:str, proc:TALKER_GROUP) -> TALK_STACK_ITEM:
        '''👉 Adds a stack call back for when a procedure ends.'''
        call = {
            'Caller': currentIndex, # next.StepID(),
            'Procedure': proc.GroupID(),
            'ProcTitle': proc.Title(),
        }
        self.Append(call)
        return TALK_STACK_ITEM(call)
        


class TALK_INDEX(TALK_BASE):
    '''😃 Moves between script lines.'''


    def _Initialize(self):
        '''👉 Initialize the talks index and stack.'''
        self.Require()
        self.ClearAtt('Index')
        self._ResetStack()


    def _Stack(self, set=None):
        return TALK_STACK(self.GetAtt('Stack', set=set))
    
    def _ResetStack(self):
        self._Stack(set=[]).MatchEmpty()

    
    def CurrentIndex(self):
        index = self.GetAtt('Index')
        if index == None or str(index).startswith('0'):
            self._ResetStack()
        return index


    def _AtTopMenu(self) -> str:
        '''👉 Indicates of the current index is empty, i.e. the user is at the top menu.'''
        return self.GetAtt('Index') == None


    def _GetNext_HandleAtTop(self, answer:str):

        LOG.Print(f"😃📚 TALK.INDEX.GetNext:", "_atTopMenu")
        # For entry talker options, move to the 1st option of the selected top menu.

        # Reset the stack, given that we are at the top.
        self._ResetStack()

        # Verify the answer input.
        UTILS.Require(answer)
        UTILS.AssertIsType(answer, str)

        # Verify if the given answer is one of the top menus.
        topTitles = [g.Title() for g in self.TopGroups()]
        UTILS.AssertIsAnyValue(answer, topTitles)

        # Get the group definition by group name == answer.
        topGroups = self.TopGroupsAsTitleDictinary()
        group = topGroups[answer]

        # Return the first group step of the selected top menu.
        ret = group.FirstStep()
        LOG.Print(f"😃📚 TALK.INDEX.GetNext:", 'FirstStep=', ret)
        return ret
    

    def _GetNext_HandleReturnToParent(self, 
        answer: str, group: TALKER_GROUP, currentStep: TALKER_STEP):

        LOG.Print(
            f"😃📚 TALK.INDEX.GetNext:",
            f"no more steps in group...",
            f"group= {group.Title()}",
            f"groupID= {group.StepID()}")

        # Nothing more to do on the group - return if it's a top menu.
        if group.IsTop():
            LOG.Print(
                f"😃📚 TALK.INDEX.GetNext:", 
                "already at the top, returning (None)...", 
                "group.IsTop()= True")
            return None

        # Check if there's a callback on the stack.                  
        call = TALK_STACK_ITEM(self.Pop('Stack'))
        if call.IsMissingOrEmpty():
            # It could happen for procs called to respond to events.
            return None
            procName = group.Title()
            LOG.RaiseException(
                f'💥 Procedure [{procName}] not found on stack.',
                self._Stack())
        else:
            LOG.Print(
                f"😃📚 TALK.INDEX.GetNext:", 
                f"we were called by procedure={call.GetAtt('Procedure')}",
                f"jumping out...")

        # Verify the integrity of the call back.
        procedureID = call.RequireProcedure()
        callerID = call.RequireCaller()
        if procedureID != currentStep.GroupID():
            LOG.RaiseException(
                f"😃📚 TALK.INDEX.GetNext:", 
                f'💥 Unexpected current procedure! ',
                f'Given procID= {procedureID}', 
                f'but expected groupID= {currentStep.GroupID()}',
                f'group.ID= {group.StepID()}', 
                f'group.Title= {group.Title()}', 
                f'call=', call,
                f'step=', currentStep)
        else:
            LOG.Print(
                f"😃📚 TALK.INDEX.GetNext:", 
                f"Verifying the integrity of the call back.",
                f"caller procedure={call.GetStr('Procedure')}",
                f"matches {currentStep.GroupID()=}, nice!")

        # Continue from the caller step.
        LOG.Print(
            f'😃📚 TALK.INDEX.GetNext:', 'get next...', 
            f'{callerID=}', f'{answer=}', call.Raw)
        
        return self.GetNext(
            currentStep=callerID, 
            answer=answer)


    # ✅ DONE
    def GetNext(self, currentStep:Union[str,TALKER_STEP], answer:any, result:str='OK') -> TALKER_STEP:
        '''👉 Finds the next step.'''

        LOG.Print(
            f'😃📚 TALK.INDEX.GetNext()', 
            f'{currentStep=}', f'{answer=}', f'{result=}',
            f"Locator={self.RequireSession().GetStr('Locator')}", 
            f'Host={self.RequireSession().RequireHost()}')
        
        LOG.Print(
            f'😃📚 TALK.INDEX.GetNext:', 'Entry stack lookup:', 
            self._Stack().ToYamlArray())

        # Handle a top menu selection.
        if UTILS.IsNoneOrEmpty(currentStep) \
        or (isinstance(currentStep, str) and currentStep == 'TOP'): #self._atTopMenu(): 
            return self._GetNext_HandleAtTop(answer)
        
        # Get the current step definition by stepID lookup, if necessary.
        if not isinstance(currentStep, TALKER_STEP):
            currentStep = self.GetTalkStep(currentStep)

        # Get the group definition of the current step.
        group = self.GetTalkGroup(currentStep)

        # else: Not a top level menu.
        if currentStep.Format() == 'REPEAT':

            LOG.Print(
                f"😃📚 TALK.INDEX.GetNext:", 
                "Processing a REPEAT...")

            # Repeat the current procedure or exit.
            if answer == 'YES':
                return group.FirstStep()
            elif answer == 'NO':
                pass # Handle to stack.pop() further down.
            else:
                LOG.RaiseException(f'Unexpected answer for REPEAT [{answer}]!')
        # else: not a REPEAT, or REPEAT==False

        if result == 'NO':
            
            # If it's a CONFIRM, check for a if-false-procedure.
            if currentStep.Format() == 'CONFIRM' \
            and currentStep.SecondArg(optional=True) != None:
                
                LOG.Print(
                    f"😃📚 TALK.INDEX.GetNext:", 
                    'Calling the exception procedure of the CONFIRM...')
                
                procName = currentStep.SecondArg()
                proc = self.GetTalkProcedure(procName)
                return proc 
            
            else:
                # Stop processing the group when there's a NO.
                next = None

        else:
            # Return the next step in the group, if one exists.
            next = group.NextStep(currentStep)
            # Ignore cases, because these are handled by EVAL.
            while next != None and next.Format() == 'CASE':
                next = group.NextStep(next)

        # There's a next step, let's run it.
        if not UTILS.IsNoneOrEmpty(next):
            LOG.Print(
                f"😃📚 TALK.INDEX.GetNext:", 
                f"moving in group...",
                f"returning next=", next)
            return next
        
        # Nothing else on this group, let's return to the parent group.
        return self._GetNext_HandleReturnToParent(
            answer=answer, 
            group= group, 
            currentStep= currentStep)


    def ResetTalkIndexAndStack(self):
        self['Index'] = None
        self['Stack'] = []


    def VerifyTalkReset(self):

        index = self.GetAtt('Index')
        if index not in [None, '0']:
            LOG.RaiseException(
                'Index should be 0, None, or missing!',
                f'Found index={index}')

        stack = self.GetAtt('Stack')
        if index not in [None, []]:
            LOG.RaiseException('Index should be empty, None, or missing!')


    def UpdateIndex(self, step:TALKER_STEP):
        '''👉 Save the new index.'''
        LOG.Print(f'😃📚 TALK.INDEX.UpdateIndex():', 
                  f'domain={NLWEB.CONFIG().RequireDomain()}',
                  'step=', step)

        stepID = step.StepID()
        self.SetIndex(stepID)
        self.UpdateItem()


    def AddToStack(self, currentIndex:str, proc:TALKER_GROUP) -> TALK_STACK_ITEM:
        LOG.Print(
            f"😃📚 TALK.INDEX.AddToStack:", 
            f'{currentIndex=}', proc)
        return self._Stack().AddCall(currentIndex, proc=proc)
        