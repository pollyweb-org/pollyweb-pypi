# 📚 TALKER_STEP

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import List, Set, Tuple, Dict, Union

from pollyweb import LOG

from pollyweb import STRUCT
from pollyweb import UTILS


class TALKER_STEP(STRUCT):
    '''😃 Wrapper for a step in a talker script.

    Properties:
    * `ID`: combination of zero-based indexes of parent and self
    * `Type`: one of TOP|PROC|STEP
    * `Parts`: array of raw string split by |

    Functions:
    * `Category`: one of PROMPT|BEHAVIOUR
    * `Command`: 1st part
    * `FirstArgument`: 1st argument
    * `SecondArgument`: 2nd argument
    * `GroupID`: ID of the parent group (left part of .)
    * `StepID`: internal ID

    Scrip examples:
    * INT|How many people?
    * CONFIRM|{wait-time}

    JSON example: 
    {
        "ID": "0.2",
        "Type": "STEP",
        "Parts": ["ONE", "{question}", "Ignore,Call,Cancel"]
    }
    '''


    def __to_yaml__(self, indent:int=0):
        '''👉 Returns a 1 line description of the step.'''
        if self.IsProcedure():
            yaml = self.StepID() + ':' + self.GetAtt('Title')
        else:
            parts = self.GetParts()
            if not parts:
                return ''
            # Return 0.2:ONE|{question}|Ignore,Call,Cancel
            yaml = self.StepID() + ':' + '|'.join(parts)
        return (' '*indent) + yaml


    @classmethod
    def Context(self):
        # the CHAT.ReplaceTalkException() implements this.
        return ''
        

    def Exception(self, msg:str):            
        LOG.RaiseException(
            msg, 
            'Step=', self.Raw, 
            self.Context)


    def StepID(self):
        '''👉 Returns the global index of the step in the talker.
        * IDs are composed of GroupPosition.StepPosition.
        * e.g., 0.1 means the 2nd step of the 1st group.'''

        stepID = self.RequireStr('ID')

        if self.IsGroup():
            try:
                int(stepID)
            except:
                LOG.RaiseValidationException(
                    f'Group.StepID() should be a number', 
                    'but is [{stepID}]! On={self._obj}')

        elif self.IsStep():
            try:
                int(stepID.split('.')[0])
                int(stepID.split('.')[1])
            except:
                LOG.RaiseValidationException(
                    f'Step.ID should be <group>.<index>, but is [{stepID}]!')

        return stepID
    

    def GetParts(self) -> List[str]:
        '''👉 Returns the string parts of the raw script.'''
        return self.GetList('Parts', mustExits=False)
    

    def RequireParts(self) -> List[str]:
        '''👉 Returns the string parts of the raw script.'''
        return self.GetList('Parts', mustExits=True)
    

    def Args(self, index:int, optional:bool=False, msg:str=None) -> str:
        '''👉 Returns the part identified by the index, 
            excluding the command name (1st part).
        * ${Parts:[cmd,arg0,arg1]}.Args(1) -> arg1
        * ${Parts:[cmd,arg0]}.Args(1) -> None (safe return)
        '''

        UTILS.AssertIsType(index, int)

        parts = self.RequireParts()
        partIndex = index+1

        if partIndex >= len(parts):

            if optional == True:
                return None
            self.Exception(
                f'💬 TALKER.Args:\n💥 '\
                'Required {partIndex=} not found on parts={self.Parts()}!\n{msg}')

        ret = parts[partIndex]

        if UTILS.IsNoneOrEmpty(ret):
            if optional == True:
                return None
            self.Exception(
                f'💬 TALKER.Args:\n💥 Required {partIndex=} is empty '\
                'on parts={self.Parts()}!\n{msg}')
        
        return ret
        

    def FirstArg(self, optional:bool=False, msg:str=None) -> str:
        '''👉 Returns the 1st argument.'''
        return self.Args(0, optional=optional, msg=msg)

    
    def SecondArg(self, optional:bool=False, msg:str=None) -> str:
        '''👉 Returns the 2nd argument.'''
        return self.Args(1, optional=optional, msg=msg)
    

    def ThirdArg(self, optional:bool=False, msg:str=None) -> str:
        '''👉 Returns the 3nd argument.'''
        return self.Args(2, optional=optional, msg=msg)
    

    def Type(self) -> str:
        '''👉 Returns the type'''
        ret = self.RequireStr('Type')
        UTILS.AssertIsAnyValue(ret, ['STEP', 'TOP', 'PROC'])
        return ret
    

    def Format(self) -> str:
        '''👉 Returns the command'''
        parts = self.RequireParts()
        return parts[0]
    

    def Category(self) -> str:
        '''👉 Returns one of PROMPT|BEHAVIOUR'''
        format = self.Format()
        cat = ''
        
        if format in [
            'AMOUNT', 'CONFIRM', 'DATE', 'EAN', 'INFO', 'INT', 
            'LOCATION', 'OTP', 'QUANTITY', 'RATE', 'SCAN', 'SELFIE', 
            'TIME', 'TOUCH', 'TRACK', 'UNTIL', 'UPLOAD', 'WAIT'
        ]:
            cat = 'PROMPT'

        elif format in ['MANY', 'ONE']:
            cat = 'PROMPT'

        elif format in ['DOWNLOAD']:
            cat = 'PROMPT'

        elif format in [
            'BINDABLE', 'CHARGE', 'CRUD', 'GOODBYE', 'ISSUE', 'REDIRECT', 
            'RESUBSCRIBE', 'REVOKE', 'SHARE', 'SUBSCRIBE'
        ]:
            cat = 'BEHAVIOUR'

        return cat
    

    def IsPrompt(self):
        '''👉 Is a step and asks the user for something.'''
        return self.IsStep() and self.Category() == 'PROMPT'
    

    def IsBehaviour(self):
        '''👉 Is a step and asks the user for something.'''
        return self.IsStep() and self.Category() == 'BEHAVIOUR'
        

    def IsGroup(self):
        '''👉 Is a top menu or procedure.'''
        return self.IsTop() or self.IsProcedure()
    

    def IsProcedure(self):
        '''👉 Is a procedure.'''
        return self.Type() == 'PROC'


    def IsTop(self):
        '''👉 Is a top menu.'''
        return self.Type() == 'TOP'
    

    def IsStep(self):
        '''👉 Is a group's step.'''
        return self.Type() == 'STEP'


    def GroupID(self):
        '''👉 Returns the ID of the parent group.'''
        id = self['ID']
        parts = id.split('.')
        ##LOG.Print(f'TALKER.STEP.GroupID(): returning [{parts[0]}] of StepID={self.StepID()}')
        return parts[0]
    

    def Position(self):
        '''👉 Returns the zero-based position of the step in the parent group.'''
        id = self.StepID()
        parts = id.split('.')
        return parts[1]
    

    def ToConfirm(self):
        '''👉 Creates a CONFIRM step from a REPEAT step.'''
        if self.Format() != 'REPEAT':
            LOG.RaiseException('ToConfirm() can only be used for REPEAT commands.')
        confirm = TALKER_STEP(self.Copy())
        confirm['Parts'][0] = 'CONFIRM'
        return confirm