
import boto3

from LOG import LOG
from STEPFUNCS_PARSER import STEPFUNCS_PARSER

# Initialize the Boto3 client for Step Functions
client = boto3.client('stepfunctions')


class STEPFUNCS():

    @classmethod
    def Parser():
        return STEPFUNCS_PARSER()
    

    @classmethod
    def InvokeStepFunctionByArn(cls, arn:str, input:dict):
        '''👉️ Invokes a Step Function.'''
        response = client.start_execution(
            stateMachineArn=arn,
            input=input)
        return response.get('executionArn')
    

    @classmethod
    def GetStateMachineArn(cls, name:str):
        '''👉️ Gets the ARN of a Step Function by name.'''
        response = client.list_state_machines()
        for stateMachine in response.get('stateMachines'):
            if stateMachine.get('name') == name:
                return stateMachine.get('stateMachineArn')
        LOG.RaiseException(f'State Machine "{name}" not found.')


    @classmethod
    def InvokeStepFunctionByName(cls, name:str, input:dict):
        '''👉️ Invokes a Step Function by name.'''
        stateMachineArn = cls.GetStateMachineArn(name)
        return cls.InvokeStepFunctionByArn(stateMachineArn, input)