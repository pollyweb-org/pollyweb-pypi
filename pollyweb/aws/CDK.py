# 📚 CDK

from LOG import LOG

class CDK():


    @classmethod
    def BootstrapIntoNorthVirginia(cls):
        '''👉 Bootstraps the CDK into the North Virginia region (us-east-1).'''
        cls.BootstrapIntoRegion('us-east-1')


    @classmethod
    def BootstrapIntoRegion(cls, region:str):
        '''👉 Bootstraps the CDK into the specified region.'''
        
        # Get the account number.
        from AWS import AWS
        account = AWS.STS().GetAccountNumber()
        
        # Deploy the CDK bootstrap.
        print(f'🤖 Deploying CDK bootstrap in {region} region...')
        from PW_UTILS.UTILS import UTILS
        UTILS.OS().Execute(f'cdk bootstrap aws://{account}/{region}')


    @classmethod
    def Bootstrap(cls, region:str=None):
        '''👉 Bootstraps the CDK into the current region.'''
        
        # Get the current region.
        from AWS import AWS
        current = AWS.STS().GetRegion()

        # Check if the region is the requested.
        if region:
            from PW_UTILS.UTILS import UTILS
            UTILS.AssertEqual(
                given= current,
                expect= region,
                msg= f'Unexpected region!')
        
        # Deploy the CDK bootstrap.
        print(f'🤖 Deploying CDK bootstrap in {current} region...')
        from PW_UTILS.UTILS import UTILS
        UTILS.OS().ExecuteShellLess(['cdk','bootstrap'])
        

    @classmethod
    def DeployStack(cls, name:str, params:dict=None):
        '''👉 Deploys a CDK stack.'''
        
        # Prepare the command.
        cmds = ['cdk', 'deploy', name]

        # Add parameters if given.
        if params:
            for key, value in params.items():
                cmds.append(f'--parameters')
                cmds.append(f'{key}={value}')
        
        # Auto-approve the deployment.
        cmds += [ '--require-approval', 'never' ]

        # Execute the command.
        from PW_UTILS.UTILS import UTILS
        UTILS.OS().ExecuteShellLess(cmds)


    @classmethod
    def HandleCustomResource(cls, 
        event:dict, 
        on_create:callable,
        on_update:callable = None,
        on_delete:callable = None
    ):
        '''👉 Handles the custom resource event.
        
        Arguments:
            * `event` {dict} -- The event object.
            * `on_create` {callable} -- The mandatory create function.
            * `on_update` {callable} -- The optional update function.
            * `on_delete` {callable} -- The optional delete function.

        Resources:
            * https://medium.com/cyberark-engineering/advanced-custom-resources-with-aws-cdk-1e024d4fb2fa
        '''
        LOG.Print(event)

        # Validate the input.
        from PW_UTILS.UTILS import UTILS
        UTILS.AssertIsType(on_create, callable)
        UTILS.AssertIsType(on_update, callable)
        UTILS.AssertIsType(on_delete, callable)

        # Default to on_create if the request type is missing.
        if 'RequestType' not in event:
            return on_create()
        
        # Check the request type if there's one.
        request_type = event['RequestType'].lower()
        
        if request_type == 'create':
            # Execute the create function.
            on_create()

        elif request_type == 'update':
            # Check if the optional update function is available.
            if on_update:
                on_update()

        elif request_type == 'delete':    
            # Check if the optional delete function is available.
            if on_delete:      
                return on_delete()
            
        else:
            LOG.RaiseException(f'Invalid request type: {request_type}')

        # Return the response.
        return {
            'PhysicalResourceId': 
            'custom'
        }
    

    @classmethod
    def ReturnLambdaPayload(cls, value):
        from AWS import AWS
        AWS.LAMBDA().ReturnSuccess({
            'Value': value
        })