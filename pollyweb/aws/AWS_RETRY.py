
import time
from botocore.exceptions import ClientError, BotoCoreError
from pollyweb.utils.LOG import LOG
from pollyweb.utils.TESTS import ValidationException
from functools import wraps


def RetryWithBackoff(
    maxRetries:int= 7, 
    initialDelay:int= 0.5, 
    backoffFactor= 2,
    codes: list[str]=[]
):
    '''👉 Retry with backoff.

    Arguments:
        * `numberOfAttempts`: Number of attempts to make before giving up.
        * `initialDelay`: Initial delay in seconds.
        * `backoffFactor`: Factor by which the delay increases after each attempt.
        * `additionalErrorCodes`: Additional error codes that should trigger a retry.

    Example:
        ```
        with AWS.RetryWithBackoff():
            # Code that may raise an exception
    '''

    if codes is None:
        codes = []
    retryableErrorCodes = {
        "ValidationException",
        "ThrottlingException", 
        "LimitExceededException", 
        "ProvisionedThroughputExceededException",
        "TooManyRequestsException"
    }
    retryableErrorCodes.update(codes)
        

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < maxRetries:
                try:
                    return func(*args, **kwargs)
                except (ValidationException, ClientError, BotoCoreError) as e:

                    if isinstance(e, ValidationException):
                        error_code = "ValidationException"
                    elif type(e).__name__ == 'ParamValidationError':
                        raise
                    else:
                        error_code = e.response['Error']['Code']
                    
                    if (error_code in retryableErrorCodes or type(e).__name__ in retryableErrorCodes) and attempts < maxRetries - 1:
                        attempts += 1
                        sleepTime = initialDelay * (backoffFactor ** attempts)
                        LOG.Print(f"⏳ Attempt {attempts}: Retrying in {sleepTime} seconds due to error: {error_code}")
                        time.sleep(sleepTime)
                    else:
                        raise
        return wrapper
    return decorator
