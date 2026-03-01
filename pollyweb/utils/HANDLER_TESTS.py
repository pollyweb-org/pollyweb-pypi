from .POLLYWEB import POLLYWEB
from .STRUCT import STRUCT
from .HANDLER import HANDLER
from .AWS_TEST import AWS_TEST
from .LOG import LOG


class HANDLER_TESTS(HANDLER, AWS_TEST):


    @classmethod
    def _resetMemory(cls):
        '''👉 Resets the internal memory.'''
        cls._events = {}

    
    @classmethod
    def TestMemory(cls):
        cls._resetMemory()
        cls.AssertEqual(cls._Events(), {})
        

    @classmethod
    def _testTriggerPython(cls, arg1:int, arg2:int) -> list[int]:
        return [arg1, arg2]
    

    @classmethod
    def TestOnPython(cls):
        cls._resetMemory()
        cls.OnPython(
            event= 'e', 
            handler= cls._testTriggerPython)

        cls.AssertEqual(
            given= cls._Events(),
            expect= {'e': [cls._testTriggerPython]})


    @classmethod
    def TestTriggerPython(cls):
        cls._resetMemory()
        
        cls.OnPython(
            event= 'e', 
            handler= cls._testTriggerPython)

        cls.AssertEqual(
            given= POLLYWEB.BEHAVIORS().HANDLER().TriggerPython('e', 1, 2),
            expect= [1, 2])
        

    @classmethod
    def _testTriggerLambda(cls, event:dict[str,any]):
        ##LOG.Print(f'HANDLER_TESTS._testTriggerLambda({event=})')
        event['b']=2
        return event
    
    
    @classmethod
    def TestTriggerLambdas(cls):
        
        # Clean up.
        cls.ResetAWS()
        cls._resetMemory()

        domain = 'any-domain.com' 

        # Mock the actor.
        cls.MOCKS().ACTOR().MockActor(domain)

        # Mock the Lambda function.
        cls.MOCKS().LAMBDA().MockInvoke(
            domain= domain,
            alias= 'myFunction',
            handler= cls._testTriggerLambda)
        
        # Mock the DynamoDB table.
        cls.AWS().DYNAMO('TRIGGERS').Insert({
            'ID':'myEvent', 
            'Lambdas': ['myFunction']
        })

        # Trigger.
        resp = cls.TriggerLambdas(
            event= 'myEvent', 
            payload= {'a':1})

        # Assert.
        cls.AssertEqual(resp, STRUCT({'a':1,'b':2}))
    

    @classmethod
    def TestAllHandler(cls):
        '''👉 Runs all tests in the class.'''

        LOG.Print('HANDLER_TESTS.TestAllHandler() ==============================')

        cls.TestMemory()
        cls.TestOnPython()
        cls.TestTriggerPython()
        cls.TestTriggerLambdas()

