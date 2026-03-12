# 📚 TALKER_GROUP

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from TALKER_STEP import TALKER_STEP
from TALKER_GROUP import TALKER_GROUP
from pollyweb import TESTS
from pollyweb import LOG


class TALKER_GROUP_TESTS(TALKER_GROUP):
    

    @classmethod
    def TestSteps(cls):

        obj = {
            "ID": "0",
            "Type": "TOP",
            "Title": "Order",
            "Steps": [
                {
                    "ID": "0.0",
                    "Type": "STEP",
                    "Parts": ["CHARGE", "{amount}"]
                }
            ]
        }
        
        group = TALKER_GROUP(obj)
        steps = group.Steps()

        # OK for TOP menu.
        TESTS.AssertEqual(len(steps), 1)
        TESTS.AssertClass(steps[0], TALKER_STEP)
        TESTS.AssertEqual(steps[0].GroupID(), "0")

        # OK for PROC.
        group['Type'] = 'PROC'
        group.Type()
        group.Steps()

        # Only for groups.
        group['Type'] = 'STEP'
        group.Type()
        with TESTS.AssertValidation():
            group.Steps()

        # Invalid group type.
        group['Type'] = 'ANOTHER'
        with TESTS.AssertValidation():
            group.Type()

    
    @classmethod
    def TestNextStep(cls):

        obj = {
            "ID": "0",
            "Type": "TOP",
            "Title": "Order",
            "Steps": [
                {
                    "ID": "0.0",
                    "Type": "STEP",
                    "Parts": ["CHARGE", "{amount}"]
                },
                {
                    "ID": "0.1",
                    "Type": "STEP",
                    "Parts": ["INFO", "Done!"]
                }
            ]
        }
        
        group = TALKER_GROUP(obj)
        TESTS.AssertEqual( group.NextStep(None).StepID(), '0.0' )
        TESTS.AssertEqual( group.NextStep('0.0').StepID(), '0.1' )
        TESTS.AssertEqual( group.NextStep('0.1'), None )
    
    
    @classmethod
    def TestFirstStep(cls):

        obj = {
            "ID": "0",
            "Type": "TOP",
            "Title": "Order",
            "Steps": [
                {
                    "ID": "0.0",
                    "Type": "STEP",
                    "Parts": ["CHARGE", "{amount}"]
                },
                {
                    "ID": "0.1",
                    "Type": "STEP",
                    "Parts": ["INFO", "Done!"]
                }
            ]
        }

        group = TALKER_GROUP(obj)
        TESTS.AssertEqual( group.FirstStep().StepID(), '0.0' )
    

    @classmethod
    def TestVerifyGroup(cls):

        obj = {
            "ID": "0",
            "Type": "TOP",
            "Title": "Order",
            "Steps": [
                {
                    "ID": "0.0",
                    "Type": "STEP",
                    "Parts": ["CHARGE", "{amount}"]
                },
                {
                    "ID": "0.1",
                    "Type": "STEP",
                    "Parts": ["INFO", "Done!"]
                }
            ]
        }
        
        group = TALKER_GROUP(obj)
        group.VerifyGroup()

        copy = TALKER_GROUP(group.Copy())
        copy['Type'] = 'ANOTHER'
        with TESTS.AssertValidation('Group type in [TOP,PROC]'):
            copy.VerifyGroup()

        copy = TALKER_GROUP(group.Copy())
        copy['ID'] = 'bla'
        with TESTS.AssertValidation('Group ID is int?'):
            copy.VerifyGroup()

        copy = TALKER_GROUP(group.Copy())
        copy.ClearAtt('Steps')
        with TESTS.AssertValidation('Group has at least one step?'):
            copy.VerifyGroup()

        copy = TALKER_GROUP(group.Copy())
        copy.FirstStep()['ID'] = '1.0'
        with TESTS.AssertValidation('Step ID matches parent ID?'):
            copy.VerifyGroup()

        copy = TALKER_GROUP(group.Copy())
        copy.FirstStep()['ID'] = '0.1'
        with TESTS.AssertValidation('Step ID has a 0-base index?'):
            copy.VerifyGroup()

        copy = TALKER_GROUP(group.Copy())
        copy.FirstStep()['Type'] = 'TOP'
        with TESTS.AssertValidation('Step is STEP?'):
            copy.VerifyGroup()


    @classmethod
    def TestAllTalkGroup(cls):
        LOG.Print('TALKER_GROUP_TESTS.TestAllTalkGroup() ==============================')

        cls.TestSteps()
        cls.TestNextStep()
        cls.TestFirstStep()
        cls.TestVerifyGroup()