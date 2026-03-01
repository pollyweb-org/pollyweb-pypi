# 📚 SECRETS

import boto3

from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from pollyweb.utils.LOG import LOG
from pollyweb.utils.UTILS import UTILS

secretsmanager = boto3.client('secretsmanager')
events_client = boto3.client('events')
lambda_client = boto3.client('lambda')


class SECRETS_SECRET:


    def __init__(self, name:str, arn:str= None) -> None:
        self.Name = name

        if not arn:
            try:
                response = secretsmanager.describe_secret(SecretId=name)
                arn = response['ARN']
            except secretsmanager.exceptions.ResourceNotFoundException:
                # If the secret does not exist, the ARN will be None
                pass

        self.Arn = arn


    def GetArn(self) -> str:
        ''' 👉 Retrieves the ARN of a secret.'''
        response = secretsmanager.describe_secret(SecretId=self.Name)
        self.Arn = response['ARN']
        return self.Arn



    def Delete(self):
        ''' 👉 Deletes a secret.'''
        secretsmanager.delete_secret(
            SecretId= self.Name)
        

    def GetValue(self) -> str:
        ''' 👉 Retrieves a secret.'''
        
        secretId:str = self.Name

        try:
            ret = secretsmanager.get_secret_value(
                SecretId= secretId
            )['SecretString']

        except Exception as e:
    
            if 'InvalidRequestException' in str(e):
                if 'marked for deletion' in str(e):
                    LOG.RaiseValidationException(f'Secret {secretId} is marked for deletion.')
    
            if 'ResourceNotFoundException' in str(e):
                from AWS import AWS
                region = AWS.STS().GetRegion()
                LOG.RaiseValidationException(
                    f'Secret {secretId} not found in region [{region}].')
    
            raise

        UTILS.AssertStrings([ret], require=True)
        return ret


    def SetValue(self, value:str):
        ''' 👉 Creates or updates a secret.'''

        name:str = self.Name

        LOG.Print(f'{name=}')
        LOG.Print(f'{value=}')
        
        try:
            secretsmanager.create_secret(
                Name=name,
                SecretString=value)
        except:
            secretsmanager.update_secret(
                SecretId=name,
                SecretString=value)


    def TriggerLambda(self, fn:LAMBDA_FUNCTION_REAL):
        ''' 👉 Sets a lambda trigger for a secret.'''

        rule_name = f'Trigger-{fn.RequireName()}-On-{self.Name}-Change'

        # Create EventBridge rule
        rule_response = events_client.put_rule(
            Name= rule_name,
            EventPattern={
                "source": ["aws.secretsmanager"],
                "detail-type": ["AWS API Call via CloudTrail"],
                "detail": {
                    "eventName": ["PutSecretValue"],
                    "requestParameters": {
                        "secretId": [self.Arn]
                    }
                }
            },
            State='ENABLED')

        # Get the rule ARN
        rule_arn = rule_response['RuleArn']

        # Add the Lambda function as a target
        events_client.put_targets(
            Rule= rule_name,
            Targets=[
                {
                    'Id': '1',
                    'Arn': fn.GetArn(),
                }
            ])