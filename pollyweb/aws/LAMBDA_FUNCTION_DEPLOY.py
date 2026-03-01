import json
import boto3

from AWS import AWS
from AWS_RETRY import RetryWithBackoff
from IAM_ROLE import IAM_ROLE
from LAMBDA_FUNCTION import LAMBDA_FUNCTION
from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS
from PW_UTILS.ZIP import ZIP


# Initialize a boto3 client
lambdaClient = boto3.client('lambda')
lambda_client = lambdaClient
logs_client = boto3.client('logs')
events_client = boto3.client('events')
iam_client = boto3.client('iam')


class LAMBDA_FUNCTION_DEPLOY(LAMBDA_FUNCTION):


    @classmethod
    def Client(cls):
        return lambdaClient
    

    @RetryWithBackoff(codes= [
        'ResourceConflictException', # An update is in progress for resource
        'InvalidParameterValueException' # The role defined for the function cannot be assumed by Lambda.
    ])
    def UpdateLambdaLayerArns(self, layerArns:list[str]):
        ''' 👉 Updates the Lambda function with the provided layer ARNs.'''

        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.UpdateLambdaLayerArns()', 
            f'{self.Name=}', f'{layerArns=}')
        
        # Update the Lambda function configuration
        self.Client().update_function_configuration(
            FunctionName=self.Name,
            Layers=layerArns)


    def EnsurePythonLambda(self, 
        code:str, 
        tags:dict, 
        timeout:int=None,
        layerArns:list[str]= [],
        env:dict= {}, 
        permissions: list[str] | dict[str, list[str]] = [],
        statements: list[dict] = []
    ):
        ''' 👉 Ensures a Python Lambda function with inline code.'''

        LOG.Print(self.EnsurePythonLambda, 
            f'{timeout=}', f'{layerArns=}', f'{env=}', f'{permissions=}', self)
        
        UTILS.AssertIsAnyType(permissions, [list, dict])
        UTILS.AssertIsList(statements, itemType=dict)

        # Zip the Python code
        zip = self.ZipCode(code, 'py')

        if self.Exists():
            self.Delete()

        """
        # Check if the lambda already exists
        if self.Exists():
            LOG.Print(f'🦙 LAMBDA.REAL.EnsurePythonLambda.Exists')
            
            # Set the permissions before updating the configurations.
            # Otherwise, the permissions won't be applied.
            self.SetPermissions(permissions)

            self.UpdateLambdaLayerArns(layerArns)
            self.UpdateLambdaCode(zip)
            self.UpdateTimeout(timeout)
            return self
        """
                
        # Create the lambda.
        self.CreatePythonLambda(
            timeout= timeout,
            zip= zip, 
            tags= tags, 
            env= env, 
            layerArns= layerArns,
            permissions= permissions,
            statements= statements)
                
        return self


    def UpdateTimeout(self, timeout:int):
        ''' 👉 Updates the Lambda function with the provided timeout.'''

        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.UpdateTimeout()', 
            f'{self.Name=}', f'{timeout=}')
        
        # Update the Lambda function configuration
        self.Client().update_function_configuration(
            FunctionName=self.Name,
            Timeout=timeout)

    
    """
    def SetPermissions2(self, permissions:list[str]):
        ''' 👉 Updates the Lambda function with the provided permissions.'''

        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.UpdatePermissions()', 
            f'{self.Name=}', f'{permissions=}')
        
        # Update the Lambda function permissions
        role = self.EnsureRole()
        role.SetPermissions(permissions)
    """


    """
    def SetPermissions(self, permissions:list[str]):
        role = self.GetRole()
        role.DetachPolicy()
        policy = role.GetPolicy()
        policy.Delete()
        role.SetPermissions(permissions)
    """

    """
    def SetPermissions3(self, permissions:list[str]):

        function_name = self.Name
        new_actions = permissions
        my_policy_name = f'{function_name}-Role-policy'

        # Get the IAM role name from the Lambda function
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        role_arn = response['Role']
        role_name = role_arn.split('/')[-1]

        # Get the attached policy names
        policies = iam_client.list_attached_role_policies(RoleName=role_name)
        policy_arn = None

        for policy in policies['AttachedPolicies']:
            if policy['PolicyName'] == my_policy_name:  # Modify this as necessary
                policy_arn = policy['PolicyArn']
                break

        # Get the policy document
        versionId = iam_client.get_policy(
            PolicyArn=policy_arn)['Policy']['DefaultVersionId']
        policy = iam_client.get_policy_version(
            PolicyArn=policy_arn,
            VersionId=versionId)
        policy_document = policy['PolicyVersion']['Document']
        LOG.Print(f'🦙 LAMBDA.DEPLOY.SetPermissions: old policy_document', policy_document)

        # Update the policy statement and manage versions
        for action in new_actions:
            for statement in policy_document['Statement']:
                if statement['Sid'] == 'NLWEB':
                    if 'Action' in statement:
                        if isinstance(statement['Action'], list):
                            if action not in statement['Action']:
                                statement['Action'].append(action)
                        else:
                            if action != statement['Action']:
                                statement['Action'] = [statement['Action'], action]
                    break

        # Check the number of existing versions
        versions = iam_client.list_policy_versions(PolicyArn=policy_arn)
        if False and len(versions['Versions']) >= 5:
            
            # Delete the non-default oldest version
            oldest_version = sorted(
                [v for v in versions['Versions'] if not v['IsDefaultVersion']],
                key=lambda v: v['CreateDate']
            )[0]

            iam_client.delete_policy_version(
                PolicyArn=policy_arn,
                VersionId=oldest_version['VersionId'])

        # Create a new version of the policy with the updated document
        iam_client.create_policy_version(
            PolicyArn=policy_arn,
            PolicyDocument=json.dumps(policy_document),
            SetAsDefault=True)
              
        LOG.Print(f'🦙 LAMBDA.DEPLOY.SetPermissions: new policy_document', policy_document)
    """

    def EnsureNodeLambda(self, zip:bytes, tags:dict, env:dict={}):
        ''' 👉 Ensures a Node Lambda function with inline code.'''

        LOG.Print(
            f'🦙 LAMBDA.REAL.EnsurNodeLambda()', 
            f'{self.Name=}')

        # Check if the lambda already exists
        exists = self.Exists()
        if exists:
            LOG.Print(f'🦙 LAMBDA.REAL.EnsurNodeLambda.Exists', exists)
            self.UpdateLambdaCode(zip)
            return self
                
        self.CreateNodeLambda(
            zip, tags=tags, env=env)
        
        return self


    def CreateNodeLambda(self, 
        zip:bytes, 
        tags:dict, 
        env:dict={}
    ):
        LOG.Print(
            f'🦙 LAMBDA.DEPLOY.CreateNodeLambda()', 
            f'{self.Name=}')
        
        self.CreateLambda(
            runtime= 'nodejs20.x',
            handler= 'index.handler',
            zip= zip, 
            tags= tags, 
            env= env,
            layerArns= [])


    def CreatePythonLambda(self, 
        zip:bytes, 
        tags:dict,
        layerArns:list[str],
        env:dict={},
        timeout:int=None,
        permissions: list[str] | dict[str, list[str]] = [],
        statements: list[dict] = []
    ):
        LOG.Print(self.CreatePythonLambda, 
            f'{self.Name=}')
        
        self.CreateLambda(
            timeout= timeout,
            runtime= 'python3.11',
            handler= 'index.handler',
            zip= zip, 
            tags= tags, 
            env= env,
            layerArns= layerArns,
            permissions= permissions,
            statements= statements)


    def Delete(self):
        ''' 👉 Deletes the lambda function.'''

        LOG.Print(self.Delete, 
            f'{self.Name=}')
        
        self.DeleteLogs()
        
        LOG.Print('@: delete the function.')
        lambdaClient.delete_function(
            FunctionName= self.Name)
            

    def Exists(self):
        ''' 👉 Indicates if the lambda exists.
        https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/get_function.html '''
        LOG.Print(f'@', self)
        
        try:
            lambdaClient.get_function(
                FunctionName= self.Name)
            return True
        except lambdaClient.exceptions.ResourceNotFoundException:
            return False


    @classmethod
    def ZipCode(cls, code:str, ext:str):
        ''' 👉 Zips the code.'''

        UTILS.AssertIsAnyValue(ext, ['py', 'js', 'mjs'])

        import base64
        import zipfile
        import io
        
        # Zip the code
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'a', 
            zipfile.ZIP_DEFLATED, False) as zip_file:
            
            zip_file.writestr(f'index.{ext}' , code)

        zip_buffer.seek(0)
    
        zip_bytes = zip_buffer.read()
        return zip_bytes


    def ValidateZipBytes(self, zip_bytes:bytes|ZIP):
        """
        Validate if the provided bytes object is a correct zip file.
        - zip_bytes: bytes object representing the zip file.
        Returns True if the zip file is valid, False otherwise.
        """

        UTILS.AssertIsAnyType(zip_bytes, [bytes, ZIP], require=True)
        if zip_bytes.__class__ == ZIP:
            zip_bytes = zip_bytes.GetBytes()

        import zipfile
        import io
        
        try:
            # Use io.BytesIO to treat the bytes object as a file.
            with io.BytesIO(zip_bytes) as file_obj:
                # Open the zip file.
                with zipfile.ZipFile(file_obj, 'r') as zip_file:
                    # Check if the zip file can be read and the files listed.
                    zip_file_contents = zip_file.namelist()

                    LOG.Print(
                        f'🦙 LAMBDA.DEPLOY.Zip file contents:', 
                        zip_file_contents)

                    # Attempt to read each file in the zip to check for corrupt files.
                    for file in zip_file_contents:
                        with zip_file.open(file) as f:
                            # Reading the content to ensure there's no corruption in files.
                            f.read()

                    return zip_bytes  # All checks passed, the zip file is valid.
        except zipfile.BadZipFile:
            LOG.RaiseException("The provided bytes object is not a zip file or it is corrupted.")
        except zipfile.LargeZipFile:
            LOG.RaiseException("The zip file requires ZIP64 functionality but it is not enabled.")
        except Exception as e:
            raise


    @RetryWithBackoff(codes= ['ResourceConflictException'])
    def UpdateLambdaCode(self,
        zip:bytes|ZIP                     
    ):
        zipBytes = self.ValidateZipBytes(zip)

        # botocore.errorfactory.ResourceConflictException: 
        # An error occurred (ResourceConflictException) when calling the UpdateFunctionCode operation: 
        # The operation cannot be performed at this time. 
        # An update is in progress for resource: 
        # arn:aws:lambda:us-west-2:99****:function:DomainMaintenance-BackUp
        result = lambda_client.update_function_code(
            FunctionName= self.Name,
            ZipFile= zipBytes)

        # Ensure the code was updated
        assert result['ResponseMetadata']['HTTPStatusCode'] == 200
        # Ensure there was no error
        assert result['ResponseMetadata']['HTTPHeaders']['content-type'] == 'application/json'
        # Ensure there was no AWS error
        assert 'FunctionError' not in result
    

    def EnsureRole(self):
        return AWS.IAM(
            #cached= self._cached
        ).EnsureLambdaRole(
            name= f'{self.Name}-Role')


    def CreateLambda(self, 
        zip:bytes|ZIP, 
        tags:dict, 
        runtime:str,
        handler:str,
        layerArns:list[str],
        env:dict={},
        timeout:int=None,
        permissions: list[str] | dict[str, list[str]] = [],
        statements: list[dict] = []
    ):
        '''👉 Creates a Python Lambda function with inline code.'''

        LOG.Print(self.CreateLambda, 
            f'{self.Name=}')
        
        # Validate the input parameters
        UTILS.AssertIsAnyType(zip, [bytes|ZIP], require=True)
        UTILS.AssertIsDict(tags, require=True, itemType=str)
        UTILS.AssertIsDict(env, itemType=str)
        UTILS.AssertIsList(layerArns, itemType=str)

        if timeout == None or timeout == 0:
            timeout = 15

        # Verify that no env has a dot.
        for key in env:
            if '.' in key:
                LOG.RaiseException(
                    f'Environment variable "{key}" of [{self.Name=}] cannot contain a dot.',
                    f'{self.Name=}', env)
        
        # Validate the zip file
        zipBytes = self.ValidateZipBytes(zip)

        role = self.EnsureRole()

        # Set the permissions before creating the lambda configurations.
        # Otherwise, the permissions won't be applied.

        # Replace a placeholder in the statements with the Lambda ARN
        if statements:
            json = UTILS.ToJson(statements)
            if '<LAMBDA_ARN>' in json:
                json = json.replace('<LAMBDA_ARN>', self.GetArn())
                statements = UTILS.FromJson(json)

        # Set the role's permissions.
        role.SetPermissions(
            permissions= permissions,
            statements= statements)
        
        LOG.Print(
            f'@: create', 
            {
                'Name': self.Name,
                'RoleName': role.RequireName(),
                'Environment': {
                    'Variables': env
                },
                'Tags': tags,
                'Layers': layerArns
            })

        # Wait for the role to be created, to avoid the error:
        # > An error occurred (InvalidParameterValueException) when calling the CreateFunction operation: 
        #   >  The role defined for the function cannot be assumed by Lambda.
        @RetryWithBackoff(codes= ['InvalidParameterValueException'])
        def create_lambda():
            # Create the Lambda function
            ret = lambdaClient.create_function(
                FunctionName= self.Name,
                Runtime= runtime,  
                Role= role.RequireArn(),
                Handler= handler,  # The file name (without .py) and the method name
                Code={
                    'ZipFile': zipBytes
                },
                Publish=True,
                Description= 'DTWF function',
                Environment={
                    'Variables': env
                },
                Tags = tags,
                Layers = layerArns,
                Timeout = timeout)
            return STRUCT(ret)

        # Extract the ARN of the newly created Lambda function
        lambda_arn = create_lambda().RequireStr(
            'FunctionArn')

        # Copy the values to the instance
        self.RoleName = role.RequireName()
        self.RoleArn = role.RequireArn()
        self.Arn = lambda_arn

        self.SetWarmUp()
        self.SetLogRetention()

        return self


    def GrantInvoke(self,
        title: str,
        principal: str,
        sourceArn: str = None          
    ):
        '''👉 Adds a permission for a principal.
         * `title`: free text to uniquly identify the statement.
         * `principal`: e.g. appconfig.amazonaws.com, events.amazonaws.com
         * `sourceArn`: where does the request comes from.
        '''

        LOG.Print(f'@: {title=}, {principal=}')
        
        if sourceArn:
            # With source ARN.
            lambda_client.add_permission(
                FunctionName= self.Name,
                StatementId= title, 
                Action= 'lambda:InvokeFunction',
                Principal= principal,
                SourceArn= sourceArn)
        else:        
            # Without source ARN.
            try:
                lambda_client.add_permission(
                    FunctionName= self.Name,
                    StatementId= title, 
                    Action= 'lambda:InvokeFunction',
                    Principal= principal)
            
            except Exception as e:
                # Ignore duplicate statement IDs.
                if 'ResourceConflictException' not in str(e):
                    raise
                LOG.Print('Duplicate statement ID ignored.')
                

    def SetWarmUp(self):

        # Create the CloudWatch Events rule
        rule_response = events_client.put_rule(
            Name= 'every-5-minutes-rule',
            ScheduleExpression= 'cron(*/5 * * * ? *)',  # Runs every 5 minutes
            State= 'ENABLED',
            Description= 'Trigger Lambda every 5 minutes')

        self.GrantInvoke(
            title= 'every-X-minutes-invoke-' + self.Name,
            principal= 'events.amazonaws.com',
            sourceArn= rule_response['RuleArn'])

        # Define your specific payload here
        payload = { "warm-up": "true" }

        # Link the Lambda function to the CloudWatch Events rule
        events_client.put_targets(
            Rule='every-5-minutes-rule',
            Targets=[
                {
                    'Id': '1',
                    'Arn': self.Arn,
                    'Input': json.dumps(payload)  
                }
            ])


    @RetryWithBackoff(
        maxRetries= 3,
        codes= ['ResourceNotFoundException'])
    def SetLogRetention(self, days:int=1):
        ''' 👉 Sets the log retention for the Lambda function.'''

        function_name = self.Name
        
        # Set log retention to 1 day only.
        log_group_name = f'/aws/lambda/{function_name}'

        try:
            logs_client.put_retention_policy(
                logGroupName= log_group_name,
                retentionInDays= days)
            
        except logs_client.exceptions.ResourceNotFoundException:

            # The log group does not exist, create it.
            logs_client.create_log_group(
                logGroupName= log_group_name)
            
            logs_client.put_retention_policy(
                logGroupName= log_group_name,
                retentionInDays= days)
        

    def GetArn(self):
        ''' 👉 Returns the ARN of the lambda.'''

        LOG.Print(
            f'🦙 LAMBDA.REAL.GetArn()', 
            f'{self.Name=}')
        
        if self.Arn:
            return self.Arn
        
        if not self.Exists():
            self.Arn = f'arn:aws:lambda:{AWS.Region()}:{AWS.AccountNumber()}:function:{self.Name}'
        
        else: # the lambda exists.
            response = lambdaClient.get_function(
                FunctionName= self.Name)
            LOG.Print({
                '🦙 LAMBDA.REAL.GetArn': response
            })
            
            self.Arn = response['Configuration']['FunctionArn']

        return self.Arn
    

    def GetRole(self):
        ''' 👉 Returns the lambda's role.'''
        arn = self.GetRoleArn()
        return AWS.IAM().ROLE(arn.split('/')[-1])
    

    def UpdateRole(self, role:IAM_ROLE):
        lambda_client.update_function_configuration(
            FunctionName= self.Name,
            Role= role.RequireArn())



    def GetRoleArn(self):
        ''' 👉 Returns the ARN of the lambda's role.'''

        LOG.Print(
            f'🦙 LAMBDA.REAL.GetRoleArn()', 
            f'{self.Name=}')
        
        # Verify if the role ARN exists
        if hasattr(self, 'role_arn') and self.RoleArn:
            return self.RoleArn

        response = lambdaClient.get_function(
            FunctionName= self.Name)
        
        LOG.Print({
            '🦙 LAMBDA.REAL.GetRoleArn': response
        })
        
        self.RoleArn = response['Configuration']['Role']
        return str(self.RoleArn)
    
    
    def GetRoleName(self):
        ''' 👉 Returns the name of the lambda's role.'''
        arn = self.GetRoleArn()
        return arn.split('/')[-1]
    


    @classmethod
    def GetLambdaNamesByTag(cls, tag_key, tag_value):
        ''' 👉 Returns a list of Lambda function names that have a 
            specific tag with a specific value.'''

        lambda_names = []

        # Paginate through all Lambda functions in case there are more than can be returned in a single call
        paginator = lambdaClient.get_paginator('list_functions')
        for page in paginator.paginate():
            for function in page['Functions']:

                # Get the ARN of the function
                function_arn = function['FunctionArn']
                
                # Retrieve tags for the function
                tags = lambdaClient.list_tags(Resource=function_arn)['Tags']
                
                # Check if the function has the specified tag and its value matches
                if tags.get(tag_key) == tag_value:
                    lambda_names.append(function['FunctionName'])
        
        return lambda_names
    

    def DeleteLogs(self):
        LOG.Print('@')

        # Derive the log group name from the Lambda function name
        log_group_name = f'/aws/lambda/{self.Name}'

        # Get all log streams in the log group
        paginator = logs_client.get_paginator('describe_log_streams')
        response_iterator = paginator.paginate(logGroupName=log_group_name)

        # Delete each log stream
        for response in response_iterator:
            log_streams = response['logStreams']
            for log_stream in log_streams:
                log_stream_name = log_stream['logStreamName']
                
                LOG.Print(f"@: Deleting log stream: {log_stream_name}")
                logs_client.delete_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)

        # Optionally, delete the entire log group (uncomment the line below if needed)
        # logs_client.delete_log_group(logGroupName=log_group_name)
        LOG.Print(f"@: Deleted all logs for Lambda function: {self.Name}")
