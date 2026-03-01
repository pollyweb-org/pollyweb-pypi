from DEPLOYER_EXEC_LAMBDA import DEPLOYER_EXEC_LAMBDA
from DEPLOYER_TASK import DEPLOYER_TASK
from aws.AWS import AWS
from aws.LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from LOG import LOG
from PW_UTILS.UTILS import UTILS


class DEPLOYER_EXEC_LAMBDA_PYTHON(DEPLOYER_EXEC_LAMBDA):


    @classmethod
    def GetHandler(cls,
        task:DEPLOYER_TASK
    ):
        '''👉️ Gets the Lambda handler.'''

        LOG.Print(cls.GetHandler, task)

        # Get the handler from the task.
        taskHandler:str = task.GetParam('Handler')
        stackHandler:str = None

        # If the handler is not set, then get it from the stack.
        if not taskHandler:
            LOG.Print(f'@: Handler not set for task, get from stack.')
            stackHandler = task.GetStackParam('Handler')

        # If the handler is not set, then raise an error.
        if not taskHandler and not stackHandler:
            task.Exception(f'Handler not set for task nor stack.')

        LOG.Print(cls.GetHandler, 
            f'{taskHandler=}', f'{stackHandler=}')

        # If the handler param is set, then add the event parameter.
        if taskHandler:

            if taskHandler.endswith(')'):
                LOG.Print(f'@: Method already has parameters, just execute.')
                ret = f'''
    from NLWEB import NLWEB
    return {taskHandler}'''
                
            else:
                LOG.Print(f'@: Method does not have parameters, add (event).')
                ret = f'''
    from NLWEB import NLWEB
    return {taskHandler}(event)'''
                
        elif stackHandler:
            if stackHandler.endswith(')'):
                LOG.Print(f'@: Class already instantiated, just add the handler method.')
                ret = f'''
    from NLWEB import NLWEB
    return {stackHandler}.Handle{task.RequireAsset()}(event)'''
                
            else:
                LOG.Print(f'@: Instantiate the class and add the handler method.')
                ret = f'''
    from NLWEB import NLWEB
    from {stackHandler} import {stackHandler}
    return {stackHandler}().Handle{task.RequireAsset()}(event)'''
        
        LOG.Print(f'@: {ret=}')

        return ret
    
    
    def OnValidate(self):
        '''👉️ Executes a Lambda task.'''
        LOG.Print(self.OnValidate)

        super().OnValidate()

        self.VerifyAlienParameters([
            'Alias',
            'Handler',
            'Timeout', 
            'Environment', 
            'Trigger', 
            'Permissions',
            'RunAt'
        ])

        # Verify if the trigger is in dependencies.
        self.Trigger = self._VerifyTrigger()

        # Get the lambda name from the task.        
        self.handler = self.GetHandler(self.task)
        
        # Write an inline lambda with keep alive.
        # Execute the stack's default handler with 'return {handler}(event) 
        self.lambdaCode = f'''
from PW_AWS.AWS import AWS
l = AWS.LAMBDA()
def handler(event, context):    
    if l.IsWarmUp(event): return
{self.handler}
'''
        
        self.lambdaPermissions = self.task.GetListParam(
            'Permissions', 
            itemType= str, 
            default= [])
        
        self.lambdaTimeout = self.task.GetIntParam(
            'Timeout')
        

    def _VerifyTrigger(self):
        '''👉️ Verifies if the trigger is a dependency.'''

        trigger = self.task.GetParam('Trigger')
        if not trigger:
            return None
        else:
            dep = self.RequireDependency(trigger)

            if dep.RequireType() not in [
                'Dynamo', 
                'Secret', 
                'SqsQueue', 
                'SnsTopic',
                'Bus'
            ]:
                self.task.Exception(
                    f'Unexpected trigger type: {dep.RequireType()}.')
                
            return dep

        
    def OnExecute(self):
        '''👉️ Executes a Lambda deployment.'''

        #self.PostExecute()
        #return {}

        LOG.Print(f'@: {self._cached=}')

        self.lambdaEnv = self._AddDependencyAlias()
        
        fn:LAMBDA_FUNCTION_REAL = AWS.LAMBDA(
            name= self.lambdaName,
            alias= self.lambdaAlias, 
            cached= self._cached)
        
        tags = self.GetTags()

        permissions, statements = self.ParsePermissions()
        
        LOG.Print(f'@: EnsurePythonLambda')
        fn.EnsurePythonLambda(
            timeout= self.lambdaTimeout,
            code= self.lambdaCode,
            tags= tags, 
            env= self.lambdaEnv,
            layerArns= self.layerArns,
            permissions= permissions, 
            statements= statements)
        
        # External tables will default to read only.
        # Dependent event bridge bus grants push permission on it.

        # Map the trigger to the lambda.
        self._MapTrigger(fn)

        self.PostExecute()

        return {
            'Arn': fn.GetArn(),
            'Name': fn.RequireName()
        }
    

    def _AddDependencyAlias(self):
        # Dependent tables are added in CAPS to the env variables.

        env = {}
        
        for dep in self.GetDependencyMap():

            if dep.Type in ['Node', 'Lambda']:
                # 'Lambda' and 'Node' are both lambdas.
                key = f'Lambda_{dep.Name}_Name'
                # Lambdas can't have dots in the name.
                env[key] = dep.FullName.replace('.', '-')
            
            elif dep.Type in ['Dynamo']:
                key = f'{dep.Type}_{dep.Name}_Name'
                # Dynamo tables can have dots in the name.
                env[key] = dep.FullName

        return env


    def _MapTrigger(self, fn:LAMBDA_FUNCTION_REAL):
        '''👉️ Executes the trigger.'''
        LOG.Print(f'@')
        
        if not self.Trigger:
            return

        LOG.Print(
            f'@: Trigger on {self.Trigger.RequireTypeAndFullName()}', 
            self.Trigger)
        
        trgType= self.Trigger.RequireType()
        trgName = self.Trigger.RequireFullName()

        # Trigger on a Secret change.
        if trgType == 'Secret':
            secret = AWS.SECRETS().Get(trgName)
            secret.TriggerLambda(fn)

        # Trigger on a DynamoDB stream.
        if trgType == 'Dynamo':
            table = AWS.DYNAMO(
                name= trgName)
            table.TriggerLambda(fn)

        # Trigger on a SqsQueue.
        if trgType == 'SqsQueue':
            queue = AWS.SQS().Get(trgName)
            queue.TriggerLambda(fn)
        
        # Trigger on a Snstopic.
        if trgType == 'SnsTopic':
            raise Exception('Not implemented.')
        
        # Trigger on a Bus.
        if trgType == 'Bus':
            raise Exception('Not implemented.')