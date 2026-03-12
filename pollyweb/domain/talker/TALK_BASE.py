# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union

from pollyweb import LOG

from SESSION import SESSION
from NLWEB import NLWEB

from PW_AWS.ITEM import ITEM
from PW_UTILS.HANDLER import HANDLER
from TALKER_STEP import TALKER_STEP
from TALKER_GROUP import TALKER_GROUP
from pollyweb import UTILS


class TALK_BASE(HANDLER, ITEM):
    '''😃 Structure of a talk'''
        

    def SetIndex(self, set:str=None) -> str:
        '''👉 Gets or sets the current position in the talk.'''
        return self.RequireStr('Index', set=set)


    def RequireSession(self) -> SESSION:
        session = self.RequireStruct('Session')
        ret = NLWEB.INTERFACES().SESSION(session)
        ret.VerifySession()
        return ret
    

    def GetContext(self) -> any:
        '''👉 Get the starting context of the talk, if not initiated via a CheckIn.'''
        return self.GetAtt('Context')


    def RequireBroker(self) -> str:
        return self.RequireSession().RequireBroker()
    

    def RequireHost(self) -> str:
        return self.RequireSession().RequireHost()
    

    def RequireSessionID(self) -> str:
        return self.RequireSession().RequireID()


    def Groups(self) -> list[TALKER_GROUP]:
        '''👉 Returns the groups within the talk.'''
        groups = []
        for group in self.Structs('Groups'):
            groups.append(TALKER_GROUP(group))
        return groups
    

    def TopGroups(self) -> list[TALKER_GROUP]:
        '''👉 Returns the top groups within the talk.'''
        return [g for g in self.Groups() if g.Type() == 'TOP']
    

    def TopGroupsAsTitleDictinary(self) -> dict[str,TALKER_GROUP]:
        '''👉 Returns the top groups as a dictionary.'''
        ret = {}
        for g in self.TopGroups():
            ret[g.Title()] = g
        return ret
    

    def GetTalkGroup(self, groupID:Union[str, TALKER_STEP]) -> TALKER_GROUP:
        '''👉 Returns the group with the given StepID.'''

        ##LOG.Print(f'TALK.GetTalkGroup(id={groupID})')
        
        if isinstance(groupID, TALKER_STEP):
            groupID = groupID.GroupID()
        
        UTILS.AssertIsType(groupID, str)
        group = self._getStruct(id=groupID)

        # Validations.
        group.Require()
        UTILS.AssertIsAnyValue(group.Type(), ['TOP', 'PROC'])

        # Cast.
        return TALKER_GROUP(group)
    

    def GetTalkProcedure(self, name:str) -> TALKER_GROUP:
        '''👉 Returns the procedure group with the given name.
        * raises an exception if not found.'''
        UTILS.RequireArgs([name])
        UTILS.AssertIsType(name, str)

        for group in self.Groups():
            if group.IsProcedure():
                if group.Title() == name:
                    return group
            
        LOG.RaiseValidationException(f'Procedure {name} not found in the groups!')
    

    def GetTalkStep(self, stepID:str) -> Union[TALKER_STEP,None]:
        '''👉 Returns the step with the given StepID.'''
        
        UTILS.Require(stepID)
        if stepID == 'TOP':
            return None
        
        step = self._getStruct(id=stepID)
        UTILS.Require(step)

        UTILS.AssertIsAnyValue(step.Type(), ['TOP','STEP'])

        return TALKER_STEP(step)


    def _getStruct(self, id:str) -> TALKER_STEP:
        '''👉 Returns the group/step with the given stepID.
        * Usage: current = self._getStep(stepID)
        '''
        UTILS.AssertIsType(id, str)

        ##LOG.Print(f'TALK._getStruct(id={id})')

        if id == None or id == '' or id == 'TOP':
            return None
                
        parts = id.split('.')
        try:
            groupIndex = int(parts[0])
        except:
            LOG.RaiseValidationException(
                f'GroupId [{parts[0]}] should be a number!')

        groups = self.Groups()
        if len(groups) <= groupIndex:
            LOG.RaiseValidationException(f'Invalid groupIndex={groupIndex} for len={len(groups)} on groups={groups}')
        group:TALKER_GROUP = groups[groupIndex]

        step = None
        if len(parts) == 2:

            stepIndex = int(parts[1])
            steps = group.Steps()

            UTILS.AssertInterval(
                value= stepIndex,
                lower= 0,
                upper= len(steps)-1)
            
            step:TALKER_STEP = steps[stepIndex]

        if step != None:
            return step
        else:
            return group


    

