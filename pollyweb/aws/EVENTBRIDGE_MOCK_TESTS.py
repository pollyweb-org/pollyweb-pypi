from PW_UTILS.TESTS import TESTS
from EVENTBRIDGE_MOCK import EVENTBRIDGE_MOCK
from PW_UTILS.STRUCT import STRUCT
from LOG import LOG


class EVENTBRIDGE_MOCK_TESTS(EVENTBRIDGE_MOCK):

        
    _handled:any = None

    @classmethod
    def _handler(cls, event):
        EVENTBRIDGE_MOCK_TESTS._handled = event['detail']


    @classmethod
    def _testPublish(cls, detail={}):
        cls.Publish(
            eventBusName='default', 
            source= 'any',
            detailType= 'method@actor',
            detail= detail)


    @classmethod
    def TestPublish(cls):

        cls.ResetMock()
        with TESTS.AssertValidation():
            cls._testPublish()

        # Happy path:
        cls.ResetMock()
        cls.MockHandlers({'method@actor': cls._handler})

        TESTS.AssertEqual(EVENTBRIDGE_MOCK_TESTS._handled, None)
        cls._testPublish(detail=STRUCT({'A':1}))
        TESTS.AssertEqual(EVENTBRIDGE_MOCK_TESTS._handled, {'A':1})
    

    @classmethod
    def TestAllBus(cls):
        LOG.Print('MOCK_BUS_TESTS.TestAllBus() ==============================')

        cls.TestPublish()