# 📚 TALKER_GROUP

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union

from pollyweb import LOG

from TALKER_STEP import TALKER_STEP
from pollyweb import UTILS


class TALKER_GROUP(TALKER_STEP):
    '''😃 Wrapper for a group of steps in a talker script.

    Properties:
    * `Steps`: list of steps
    * `Title`: title
    
    Methods:
    * `FirstStep`: the first step
    * `NextStep(currentID)`: the next step, after the given ID

    Script examples:
    * 💬|I need a table:
    * Available:

    JSON Example:
    {
        "ID": "0",
        "Title": "Order",
        "Steps": [
            {
                "ID": "0.1",
                "Type": "STEP",
                "Parts": ["CHARGE", "{amount}"]
            }
        ]
    }
    '''


    def GroupID(self):
        '''👉 Returns the zero-base index of the group in the talker.
        * e.g., 0 means the 1st group.'''
        return self.RequireAtt('ID')


    def Title(self):
        return self.RequireStr('Title')


    def Steps(self) -> list[TALKER_STEP]:
        '''👉 Returns the Steps attribute.'''

        if self.IsStep() or not self.IsGroup():
            LOG.RaiseValidationException(f'Use only for groups. Type={self.Type()}')
        
        groupID = self.StepID()

        steps = []
        index = 0
        for item in self.GetList('Steps', mustExits= True):
            step = TALKER_STEP(item)
            
            # Validations.
            UTILS.AssertEqual(step.GroupID(), groupID, 'Step belogs to group?')
            UTILS.AssertEqual(step.IsGroup(), False, 'Step is not a group?')
            UTILS.AssertEqual(step.StepID(), f'{groupID}.{index}', 'Step index is correctly assigned?')

            steps.append(step)
            index = index + 1

        return steps


    def NextStep(self, currentID:Union[str,TALKER_STEP]) -> Union[TALKER_STEP, None]:
        '''👉 Finds the next step in the group.
        * ${ID:1, Steps:[a,b]}.NextStep(1.0) -> $b
        * ${ID:1, Steps:[a,b]}.NextStep(1.1) -> $None
        
        Exceptions:
        * Use only for groups!
        * The step doesnt belong to this group!
        '''

        if self.IsStep():
            LOG.RaiseException('Use only for groups.')
        
        if currentID == None:
            return self.FirstStep()

        if isinstance(currentID, TALKER_STEP):
            currentID = currentID.StepID()

        groupIndex = currentID.split('.')[0]
        if str(self.GroupID()) != str(groupIndex):
            LOG.RaiseException(f'The step does not belong to group={groupIndex}! It belongs to group={self.GroupID()}.')
        
        groupSize = len(self.Steps())
        stepIndex = currentID.split('.')[1]

        ret = None
        if stepIndex != groupSize:
            ##LOG.Print(f'TALKER.GROUP.NextStep(): stepIndex={stepIndex} != groupSize={groupSize})')
            
            nextIndex = int(stepIndex)+1
            steps = self.Steps()

            if nextIndex > len(steps)-1:
                return None
            
            UTILS.AssertInterval(
                value= nextIndex,
                lower= 0,
                upper= len(steps)-1,
                msg= 'Index in NextStep()'
            )

            ret = steps[nextIndex]

        return TALKER_STEP(ret)
    

    def FirstStep(self) -> TALKER_STEP:
        '''👉 Returns the first step.
        * ${Steps:[a,b]}.FirstStep() -> $a
        * ${Steps:[]}.FirstStep() -> Exception!
        '''
        if self.IsStep():
            LOG.RaiseException('Use only for groups.')
        
        steps = self.Steps() 
        if len(steps) == 0:
            LOG.RaiseException('Groups should have at least one step.')
        
        return steps[0]
    


    def VerifyGroup(self):
        self.Type() # Only valid types?
        self.StepID() # The format of stepID is correct?
        self.Steps() # All steps correctly indexed?
        self.FirstStep() # At least one step?
        
