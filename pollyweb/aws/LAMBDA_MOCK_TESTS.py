from AWS_TEST import AWS_TEST
from PW_UTILS.STRUCT import STRUCT
from LAMBDA_MOCK import LAMBDA_MOCK
from PW_UTILS.LOG import LOG


class LAMBDA_MOCK_TESTS(LAMBDA_MOCK, AWS_TEST):


    @classmethod
    def _testInvoke(cls, event:dict[str,any]):
        event['b']=2
        return event
    

    @classmethod
    def TestHappyPath(cls):

        cls.ResetMock()
        cls.MOCKS().ACTOR().MockActor()
        cls.MockInvoke('l', cls._testInvoke)
        
        result = LAMBDA_MOCK('l').Invoke({'a':1})
        cls.AssertEqual(result, STRUCT({'a':1,'b':2}))


    @classmethod
    def TestUnregistered(cls):
        
        cls.ResetMock()
        with cls.AssertValidation():
            LAMBDA_MOCK('l').Invoke({})
        

    @classmethod
    def TestWarmUp(cls):
        cls.AssertTrue(cls.IsWarmUp({ "warm-up": "true" }))
        cls.AssertTrue(cls.IsWarmUp({ 
            'warm-up':'true'
        }))
        cls.AssertFalse(cls.IsWarmUp({}))
        cls.AssertFalse(cls.IsWarmUp(None))


    @classmethod
    def TestAllLambda(cls):
        LOG.Print('MOCK_LAMBDA_TESTS.TestAllLambda() ==============================')
        
        cls.TestWarmUp()
        cls.TestHappyPath()
        cls.TestUnregistered()

        
