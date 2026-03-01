from PW_UTILS.LOG import LOG
from PW_UTILS.UTILS import UTILS


class LAMBDA_BASE():
    '''👉 Base class for Lambda functions.'''

    ICON = '🦙'


    def __init__(self, 
        cached: bool= False):
        '''👉 Initialize the class.'''

        self._cached = cached
        if cached: self._cache = UTILS.CACHE()



    @classmethod
    def IsLambda(cls):
        '''👉 Is a the code running on AWS Lambda?
        * Returns true if the the code is running on AWS Lambda.
        * Returns false if the code is running in a local environment.
        '''
        import os
        if os.environ.get('AWS_EXECUTION_ENV') is not None:
            return True
        return False


    @classmethod
    def IsLocal(cls):
        '''👉 Is the code running locally?
        * Returns true if the code is running in a local environment.'''
        return not cls.IsLambda()


    @classmethod
    def IsWarmUp(cls, event):
        '''
        👉 Is a Lambda warm up? 
        * Returns true if the payload is {"warm-up": "true"}.
        * Used to keep the lambdas warm via a CloudWatch schedule.
        '''

        # Exit if it's a warm-up.
        if event == { "warm-up": "true" }:
            from PW_UTILS.LOG import LOG
            LOG.Print('Warming up...')
            return True
        
        # Print the event if running in on AWS.
        if cls.IsLambda():
            from PW_UTILS.LOG import LOG
            LOG.Print(event)

        # Not a warm-up, continue.
        return False
    

    @classmethod
    def ParseEvent(cls, event):
        '''👉 Parse the event into multiple records.'''
        LOG.Print('🦙 LAMBDA.ParseEvent()', event)

        if 'Records' in event:
            ret = []

            # Break SQS events
            for record in event['Records']:
                if 'eventSource' not in record: break
                if 'body' not in record: break
                if record['eventSource'] != 'aws:sqs': break
                
                body = record['body']
                content = UTILS.FromJson(body)
                ret.append(content)

            LOG.Print('🦙 LAMBDA.ParseEvent: return...', ret)
            return ret            

        return [event]
        

    @classmethod
    def ReturnSuccess(cls, body:any= {}):
        '''👉 Return a 200 response.'''
        from WEB import WEB
        WEB().HttpResponse(
            status= 200,
            body= body)


    @classmethod
    def ReturnInvalidRequest(cls, body:any= {}):
        '''👉 Return a 400 response.'''
        from WEB import WEB
        WEB().HttpResponse(
            status= 400,
            body= body)
        

    