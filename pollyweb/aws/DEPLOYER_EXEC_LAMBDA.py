from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from aws.AWS_RETRY import RetryWithBackoff
from LOG import LOG
from pollyweb.utils.STRUCT import STRUCT

class DEPLOYER_EXEC_LAMBDA(DEPLOYER_EXEC_TASK):


    def GetVerifierHandler(self):
        '''👉️ Gets the Lambda handler.'''

        LOG.Print(self.GetVerifierHandler, self)

        task = self.task

        # Get the handler from the task.
        handler:str = task.GetStringParam('Verifier')
        
        # If the handler is not set, then get it from the stack.
        if not handler:
            handler = task.GetStackParam('Verifier')

        # If the handler is not set, then exit the function.
        if not handler:
            return
        
        exec(f'from {handler} import {handler}')
        return handler


    def VerifyLambda(self):
        '''👉️ Verifies the Lambda function.'''
        LOG.Print(self.VerifyLambda, self)

        verifier = self.GetVerifierHandler()
        method = self.task.RequireName()
        if verifier:

            code = f'''
from {verifier} import {verifier}
{verifier}().Verify{method}(args)'''
            
            args = { 'args': self }

            LOG.Print('@: executing', 
                f'{code=}', f'{verifier=}', f'{method=}')
            
            @RetryWithBackoff(
                codes=['ContinuousBackupsUnavailableException'],
                maxRetries= 15)
            def myExec(code, args):
                exec(code, args)

            try: 
                myExec(code, args)
            except Exception as e:
                LOG.Print(
                    '@: failed.', f'{e=}', 
                    f'{code=}', f'{verifier=}', f'{method=}')
                raise 

    
    def OnValidate(self):
        '''👉️ Gets the Lambda name.'''
        
        self.lambdaAlias = self.task.RequireAsset()

        self.lambdaName = self.task.RequireFullName().replace('.', '-')

        self.lambdaTests:STRUCT = self.GetTests()

        self.lambdaVerifier = self.GetVerifierHandler()



    def GetTests(self):
        '''👉️ Gets the Lambda tests.'''

        # Always return a WarmUp test.
        ret = {
            'WarmUp': {
                'request': {
                    "warm-up": "true"
                },
                'response': None
            }
        }

        # Get the tests param.
        tests = self.task.GetParam('Tests')

        # If the tests param is not set, then return.
        if not tests:
            return STRUCT(ret)
        
        # Get the tests directory.
        testsDir = self.task.GetDirectory().GetSubDir('tests').AssertExists()
        name = self.task.RequireName()
        lambdaDir = testsDir.GetSubDir(name).AssertExists()
        
        for name in STRUCT(tests).Keys():
            testDir = lambdaDir.GetSubDir(name)
            testDir.AssertExists()
            
            jsonRequest = testDir.GetFile('request.json')
            yamlRequest = testDir.GetFile('request.yaml')
            if jsonRequest.Exists():
                request = jsonRequest.ReadJson()
            elif yamlRequest.Exists():  
                request = yamlRequest.ReadYaml()
            else:
                LOG.RaiseException('Request file not found.', f'{name=}')
            
            jsonResponse = testDir.GetFile('response.json')
            yamlResponse = testDir.GetFile('response.yaml')
            if jsonResponse.Exists():
                response = jsonResponse.ReadJson()
            elif yamlResponse.Exists():  
                response = yamlResponse.ReadYaml()
            else:
                LOG.RaiseException('Response file not found.', f'{name=}')

            ret[name] = {
                'request': request,
                'response': response
            }
        
        return STRUCT(ret)
    

    def InvokeLambda(self, event:dict):
        '''👉️ Invokes the Lambda function.'''
        
        LOG.Print(self.InvokeLambda, 
            f'{self.lambdaName=}', f'{self.lambdaAlias=}',
            'Payload=', event, self)

        fn = AWS.LAMBDA(
            name= self.lambdaName,
            alias= self.lambdaAlias)
        
        fn.WaitToBeReady(seconds=10)
        
        try :
            return fn.Invoke(
                params= event)
        
        except Exception as e:
            if 'Lambda was unable to decrypt the environment variables because KMS access was denied' in str(e):
                LOG.Print(f'@: {e}')

                # Fix the KMS access by re-setting the role.
                tempRole = AWS.IAM().EnsureLambdaRole(
                    name= 'NLWEB-Fix-KMS-Access')
                oldRole = fn.GetRole()
                fn.UpdateRole(tempRole)
                fn.UpdateRole(oldRole)

                # Retry the invocation.
                return fn.Invoke(
                    params= event)
            
            # Otherwise, raise the exception.
            raise


    def PostExecute(self):
        '''👉️ Executes the post task.'''

        # Add the lambda alias to the environment
        #  so that the next task can use it for verifying deployments.
        alias = self.task.GetStringParam('Alias')
        
        if alias:            
            import os
            os.environ[
                #UTILS.CamelToUppercase(self.lambdaAlias)
                alias
            ] = self.lambdaName
        
        # Verify the deployment.
        self.VerifyLambda()
        

    def ParsePermissions(self):
        '''👉️ Parses the permissions.'''
        
        self.lambdaPermissions = self.task.GetListParam(
            'Permissions', 
            itemType= str, 
            default= [])
        
        statements = []
        
        # Build the initial permissions.
        permissions:dict[str, list[str]] = { '*': [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]}

        for permission in self.lambdaPermissions:
            permissions['*'].append(permission)

        # Get the trigger name for permissions.
        trgName = None
        if hasattr(self, 'Trigger') and self.Trigger:    
            trgName = self.Trigger.RequireFullName()
        LOG.Print(f'@: Trigger name= {trgName}')

        # Add permissions for dependencies.
        for dep in self.GetDependencyMap():
            LOG.Print(f'@: Add dependency permissions for {dep.FullName}', dep)
            
            if dep.Type in ['Lambda', 'Node']:
                LOG.Print(f'@: Lambda dependency')
                permissions[dep.RequireArn()] = [
                    'lambda:InvokeFunction'
                ]

            if dep.Type == 'SqsQueue':
                LOG.Print(f'@: SqsQueue dependency')

                queueName = dep.FullName.replace('.', '-')
                queue = AWS.SQS().Require(queueName)

                permissions[queue.Arn] = [
                    'sqs:ChangeMessageVisibility',
                    'sqs:ChangeMessageVisibilityBatch',
                    'sqs:DeleteMessage',
                    'sqs:DeleteMessageBatch',
                    'sqs:GetQueueAttributes',
                    'sqs:GetQueueUrl',
                    'sqs:ListQueues',
                    'sqs:ReceiveMessage',
                    'sqs:SendMessage',
                    'sqs:SendMessageBatch',
                    'sqs:PurgeQueue'
                ]

                statements.append({
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sqs.amazonaws.com"
                    },
                    "Action": "lambda:InvokeFunction",
                    "Resource": "<LAMBDA-ARN>",
                    "Condition": {
                        "ArnLike": {
                            "AWS:SourceArn": queue.Arn
                        }
                    }
                })

            if dep.Type == 'Secret':
                LOG.Print(f'@: Secret dependency')
                permissions[dep.RequireArn()] = [
                    'secretsmanager:DescribeSecret',
                    'secretsmanager:GetSecretValue',
                    'secretsmanager:UpdateSecret',
                    'kms:Encrypt',
                    'kms:Decrypt',
                    #'secretsmanager:CreateSecret',
                ]
                
            # Dependent tables on the stack will have write permission.
            if dep.Type == 'Dynamo':
                LOG.Print(f'@: Dynamo dependency')
                permissions['*'].append('dynamodb:ListTables')
                permissions['*'].append('dynamodb:ListStreams')

                table = self.RequireDependency(dep.FullName)
                tableArn = table.RequireResult()['Arn']
                
                permissions[tableArn] = [
                    "dynamodb:BatchGetItem",
                    "dynamodb:BatchWriteItem",
                    "dynamodb:DeleteItem",
                    'dynamodb:DescribeTable',
                    'dynamodb:DescribeStream',
                    'dynamodb:GetItem',
                    'dynamodb:GetShardIterator',
                    'dynamodb:GetRecords',
                    'dynamodb:ListStreams',
                    'dynamodb:PutItem',
                    "dynamodb:Query",
                    "dynamodb:Scan",
                    'dynamodb:UpdateItem',
                    
                    #'dynamodb:CreateBackup',
                    #'dynamodb:ListBackups',
                    #'dynamodb:DeleteBackup'
                ]

                # For dynamo streams, the permission is on the stream ARN.
                if trgName == dep.FullName:
                    LOG.Print(f'@: Dynamo Stream trigger')

                    # Get the stream Arn.
                    streamArn = AWS.DYNAMO(
                        name= dep.FullName
                    ).Table().GetStreamArn()

                    # Add streaming permissions.
                    permissions[streamArn] = [
                        "dynamodb:DescribeStream",
                        "dynamodb:GetRecords",
                        "dynamodb:GetShardIterator",
                        "dynamodb:ListStreams"
                    ]

        LOG.Print(f'@: Dependency permissions added.', [
            f'{k}' for k in permissions.keys()])
        
        return permissions, statements