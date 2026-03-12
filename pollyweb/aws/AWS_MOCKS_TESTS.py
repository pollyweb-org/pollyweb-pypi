from LOG import LOG
from PW_PARALLEL.PARALLEL import PARALLEL

class AWS_MOCKS_TESTS:
    
    
    @classmethod
    def Run(cls):

        # -----------------------------
        # AWS.
        # -----------------------------

        from APPCONFIG_MOCK_TESTS import APPCONFIG_MOCK_TESTS
        APPCONFIG_MOCK_TESTS.TestAllAppConfig()
        
        from SECRETS_MOCK_TESTS import SECRETS_MOCK_TESTS
        SECRETS_MOCK_TESTS.TestAllSecrets()
        
        from SSM_MOCK_TESTS import SSM_MOCK_TESTS
        SSM_MOCK_TESTS.TestAllSettings()
        
        from EVENTBRIDGE_MOCK_TESTS import EVENTBRIDGE_MOCK_TESTS
        EVENTBRIDGE_MOCK_TESTS.TestAllBus()
        
        from LAMBDA_MOCK_TESTS import LAMBDA_MOCK_TESTS
        LAMBDA_MOCK_TESTS.TestAllLambda()
        
        from DYNAMO_MOCK_TESTS import DYNAMO_MOCK_TESTS
        DYNAMO_MOCK_TESTS.TestAllDynamo()


    @classmethod
    def GetAll(cls):
        '''👉 Returns all the test handlers for this class.'''
        return [
            cls.Run,
        ]


    @classmethod
    def TestAwsMocks(cls):

        with PARALLEL.THREAD_POOL() as pool:
            handlers = cls.GetAll()
            pool.RunThreadList(
                handlers= handlers)

        LOG.PARALLEL().SetClassDone()