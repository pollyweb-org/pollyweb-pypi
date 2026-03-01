# 📚 LAMBDA
 
import os
import json

import boto3

from LAMBDA_FUNCTION import LAMBDA_FUNCTION
from LAMBDA_FUNCTION_DEPLOY import LAMBDA_FUNCTION_DEPLOY
from pollyweb.utils.PRINTABLE import PRINTABLE

lambdaClient = boto3.client('lambda')
lambda_client = lambdaClient

from AWS_RETRY import RetryWithBackoff
from pollyweb.utils.LOG import LOG


class LAMBDA_FUNCTION_REAL(
    LAMBDA_FUNCTION_DEPLOY,
    LAMBDA_FUNCTION,
    PRINTABLE
):
    ''' 👉 Looks up the `alias` in `os.environ`
        * if not found, considers the `alias` as the function name.'''


    def __init__(self, 
        alias: str, 
        name: str= None, 
        cached: bool= False
    ):
        ''' 👉 Looks up the `alias` in `os.environ`
            * if not found, considers the `alias` as the function name.'''

        LAMBDA_FUNCTION.__init__(self, 
            cached= cached)

        # If the function name is not provided, look up the alias in os.environ.
        self.Name = None
        if name:
            self.Name = name
        elif alias:
            # Look up the alias in os.environ.
            lookup = f'Lambda_{alias}_Name'
            if lookup in os.environ:
                self.Name = os.environ[lookup]
            elif alias in os.environ:
                self.Name = os.environ[alias]
            else:
                self.Name = alias

        self.Arn = None

        PRINTABLE.__init__(self, lambda: {
            'Name': self.Name,
            'Arn': self.Arn
        })


    # botocore.errorfactory.ResourceConflictException: 
    # An error occurred (ResourceConflictException) when calling the Invoke operation: 
    # The operation cannot be performed at this time. 
    # The function is currently in the following state: Pending
    @RetryWithBackoff(codes=['ResourceConflictException'])
    def Invoke(self, params:any={}):
        ''' 👉 https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/invoke.html '''
        LOG.Print(
            self.Invoke, 
            f'{self.Name=}', params)
        
        response = lambdaClient.invoke(
            FunctionName= self.Name,
            Payload= json.dumps(params),
            LogType= 'Tail')
        
        LOG.Print(self.Invoke, 
            f'StatusCode={response["StatusCode"]}')

        if response['StatusCode'] != 200:
            LOG.RaiseException(f'@ Response: {response}', response)
        
        raw = response['Payload'].read()
        returned = json.loads(raw)
        LOG.Print(f'@.Returned', raw, returned)

        if returned == None:
            return None
        
        if 'errorMessage' in returned:
            LOG.RaiseException(
                '@: ' + returned['errorMessage'], returned, self)

        from pollyweb.utils.STRUCT import STRUCT
        ret = STRUCT(returned)

        if ret.GetAtt('errorMessage'):
            LOG.RaiseException(
                '@.Invoke: ' + ret['errorMessage'], ret)
    
        return ret
    

    def WaitToBeReady(self, seconds=300):
        """ 👉 Waits for the Lambda function to be in the 'Active' state.

        Args:
            * `function_name` (str): Name of the Lambda function.
            * `seconds` (int): Maximum time to wait in seconds.
        """

        LOG.Print(self.WaitToBeReady, 
            f'{self.Name=}', f'{seconds=}')

        import time
        
        function_name = self.Name

        start_time = time.time()
        while time.time() - start_time < seconds:
            try:
                
                # Retrieve the function's configuration
                response = lambda_client.get_function(FunctionName=function_name)

                if response['Configuration']['State'] == 'Active':
                    LOG.Print(self.WaitToBeReady,
                        "Lambda function is ready.")
                    return 
                
                else:
                    LOG.Print(self.WaitToBeReady,
                        f"Lambda function state: {response['Configuration']['State']}")

            except lambda_client.exceptions.ResourceNotFoundException:
                LOG.RaiseException(self.WaitToBeReady,
                    "Lambda function not found. Please check the function name.")
                
            time.sleep(1)  # Wait for 1 second before checking again

        LOG.RaiseException(self.WaitToBeReady,
            "Timeout waiting for Lambda function to become active.")


    def RequireName(self):
        return self.Name
    

    def GetArn(self):
        LOG.Print(f'@', f'{self.Name=}', self)

        if self.Arn:
            return self.Arn

        response = lambda_client.get_function(
            FunctionName= self.Name)
        
        self.Arn = response['Configuration']['FunctionArn']
        return self.Arn
    

    def AddEventSource(self, 
        sourceArn: str,
        batchSize: int= 1
    ):
        ''' 👉️ Adds an event source to the lambda function.'''
        LOG.Print(f'@', f'{self.Name=}', f'{sourceArn=}')

        try:
            lambdaClient.create_event_source_mapping(
                EventSourceArn= sourceArn,
                FunctionName= self.Name,
                Enabled= True,
                BatchSize= batchSize)
            
        except lambdaClient.exceptions.ResourceConflictException as e:
            LOG.Print(f'@', f'{e=}')
            return