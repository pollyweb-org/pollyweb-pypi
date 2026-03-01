from AWS_RETRY import RetryWithBackoff
from PW_UTILS.LOG import LOG
from PW_UTILS.TESTS import TESTS, ValidationException


class AWS_RETRY_TESTS:

    @classmethod
    def RetryWithBackoffSuccess(cls):
        LOG.Print(cls.RetryWithBackoffSuccess, f':')

        cls._countTestRetryWithBackoffSuccess = 0
        
        @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
        def TestMe():
            cls._countTestRetryWithBackoffSuccess += 1
            if cls._countTestRetryWithBackoffSuccess < 3:
                raise ValidationException('Test')
            
        TestMe()
        LOG.Print('@: after TestMe()')

        TESTS.AssertEqual(cls._countTestRetryWithBackoffSuccess, 3)
        LOG.Print('@: after AssertEqual()')


    @classmethod
    def RetryWithBackoffFailure(cls):
        cls._countTestRetryWithBackoffFailure = 0

        try:
            @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
            def TestMe():
                cls._countTestRetryWithBackoffFailure += 1
                raise ValidationException('Test')
                
            TestMe()
        except ValidationException:
            pass

        TESTS.AssertEqual(cls._countTestRetryWithBackoffFailure, 5)


    @classmethod
    def RetryWithBackoffReturn(cls):
        cls._countTestRetryWithBackoffReturn = 0

        @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
        def TestMe():
            cls._countTestRetryWithBackoffReturn += 1
            if cls._countTestRetryWithBackoffReturn < 3:
                raise ValidationException('Test')
            return cls._countTestRetryWithBackoffReturn * 100
            
        TESTS.AssertEqual(TestMe(), 300)


    @classmethod
    def GetAllTests(cls):
        return [
            cls.RetryWithBackoffSuccess,
            cls.RetryWithBackoffFailure,
            cls.RetryWithBackoffReturn,
        ]