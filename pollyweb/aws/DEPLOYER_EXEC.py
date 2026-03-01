from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_EXEC_DUMMY import DEPLOYER_EXEC_DUMMY
from DEPLOYER_TASK import DEPLOYER_TASK
from aws.AWS import AWS
from LOG import LOG
from PW_UTILS.UTILS import UTILS
from DEPLOYER_EXEC_ARGS import DEPLOYER_EXEC_ARGS

class DEPLOYER_EXEC():

    ICON= '🏗️'


    @classmethod
    def VerifyTasks(cls, 
        tasks:list[DEPLOYER_TASK],
        deployArgs:DEPLOYER_ARGS= None,
    ):
        '''👉️ Verifies the tasks for execution.'''
        LOG.Print('@', deployArgs)

        # Ensure the parameters.
        UTILS.AssertIsList(tasks, itemType=DEPLOYER_TASK, require=True)

        # Clear the test records.
        DEPLOYER_EXEC_DUMMY.DummyExecutions = []

        # Create a dictionary from the list.
        taskDict = UTILS.DictFromList(tasks,
            key= DEPLOYER_TASK.RequireFullName)

        # Execute all tests in simulation mode.
        for task in tasks:
            cls.ExecuteTask(
                DEPLOYER_EXEC_ARGS(
                    taskDict= taskDict,
                    task= task,
                    simulate= True,
                    deployArgs= deployArgs))
                
        # Return the tasks.
        return tasks


    @classmethod
    def ExecuteTask(cls, args: DEPLOYER_EXEC_ARGS):
        '''👉️ Executes a task '''

        LOG.Print(f'@('
            f'{args.task.RequireType()}|'
            f'{args.task.RequireFullName()})', 
            args)

        # Get the type for the if statement.
        cmd = args.task.RequireType()
        
        if cmd == 'AppConfig':
            from DEPLOYER_EXEC_APPCONFIG import DEPLOYER_EXEC_APPCONFIG
            ret = DEPLOYER_EXEC_APPCONFIG(args).Execute()
        
        elif cmd == 'Bus':
            from DEPLOYER_EXEC_BUS import DEPLOYER_EXEC_BUS
            ret = DEPLOYER_EXEC_BUS(args).Execute()
        
        elif cmd == 'Certificate':
            from DEPLOYER_EXEC_CERTIFICATE import DEPLOYER_EXEC_CERTIFICATE
            ret = DEPLOYER_EXEC_CERTIFICATE(args).Execute()
        
        elif cmd == 'CloudFront':
            from DEPLOYER_EXEC_CLOUDFRONT import DEPLOYER_EXEC_CLOUDFRONT
            ret = DEPLOYER_EXEC_CLOUDFRONT(args).Execute()
        
        elif cmd == 'DnsSecKey':
            from DEPLOYER_EXEC_DNSSECKEY import DEPLOYER_EXEC_DNSSECKEY
            ret = DEPLOYER_EXEC_DNSSECKEY(args).Execute()

        elif cmd == 'Dynamo':
            from DEPLOYER_EXEC_DYNAMO import DEPLOYER_EXEC_DYNAMO
            ret = DEPLOYER_EXEC_DYNAMO(args).Execute()

        elif cmd == 'Dummy':
            # Used for testing.
            from DEPLOYER_EXEC_DUMMY import DEPLOYER_EXEC_DUMMY
            ret = DEPLOYER_EXEC_DUMMY(args).OnExecute()
        
        elif cmd == 'File':
            from DEPLOYER_EXEC_FILE import DEPLOYER_EXEC_FILE
            ret = DEPLOYER_EXEC_FILE(args).Execute()
        
        elif cmd == 'HostedZone':
            from DEPLOYER_EXEC_HOSTEDZONE import DEPLOYER_EXEC_HOSTEDZONE
            ret = DEPLOYER_EXEC_HOSTEDZONE(args).Execute()

        elif cmd == 'Input':
            from DEPLOYER_EXEC_INPUT import DEPLOYER_EXEC_INPUT
            ret = DEPLOYER_EXEC_INPUT(args).Execute()
        
        elif cmd == 'Lambda':
            from DEPLOYER_EXEC_LAMBDA_PYTHON import DEPLOYER_EXEC_LAMBDA_PYTHON
            ret = DEPLOYER_EXEC_LAMBDA_PYTHON(args).Execute()

        elif cmd == 'Node':
            from DEPLOYER_EXEC_LAMBDA_NODE import DEPLOYER_EXEC_LAMBDA_NODE
            ret = DEPLOYER_EXEC_LAMBDA_NODE(args).Execute()

        elif cmd == 'Parameter':
            from DEPLOYER_EXEC_PARAMETER import DEPLOYER_EXEC_PARAMETER
            ret = DEPLOYER_EXEC_PARAMETER(args).Execute()
                        
        elif cmd == 'Python':
            from DEPLOYER_EXEC_PYTHON import DEPLOYER_EXEC_PYTHON
            ret = DEPLOYER_EXEC_PYTHON(args).Execute()

        elif cmd == 'PostProcessor':
            from DEPLOYER_EXEC_POSTPROCESSOR import DEPLOYER_EXEC_POSTPROCESSOR
            ret = DEPLOYER_EXEC_POSTPROCESSOR(args).Execute()
            
        elif cmd == 'RestApi':
            from DEPLOYER_EXEC_APIGW import DEPLOYER_EXEC_APIGW
            ret = DEPLOYER_EXEC_APIGW(args).Execute()
        
        elif cmd == 'Secret':
            from DEPLOYER_EXEC_SECRET import DEPLOYER_EXEC_SECRET
            ret = DEPLOYER_EXEC_SECRET(args).Execute()
        
        elif cmd == 'SnsTopic':
            from DEPLOYER_EXEC_SNS import DEPLOYER_EXEC_SNS
            ret = DEPLOYER_EXEC_SNS(args).Execute()
        
        elif cmd == 'SnsApp':
            from DEPLOYER_EXEC_SNSAPP import DEPLOYER_EXEC_SNSAPP
            ret = DEPLOYER_EXEC_SNSAPP(args).Execute()
        
        elif cmd == 'SqsQueue':
            from DEPLOYER_EXEC_SQS import DEPLOYER_EXEC_SQS
            ret = DEPLOYER_EXEC_SQS(args).Execute()

        elif cmd == 'Stack':
            # Just a group for external reference.
            ret = {}
        
        elif cmd == 'WebAcl':
            from DEPLOYER_EXEC_WAF import DEPLOYER_EXEC_WAF
            ret = DEPLOYER_EXEC_WAF(args).Execute()
            
        elif cmd == 'WebsocketsApi':
            from DEPLOYER_EXEC_WEBSOCKETS import DEPLOYER_EXEC_WEBSOCKETS
            ret = DEPLOYER_EXEC_WEBSOCKETS(args).Execute()
        
        else:
            LOG.RaiseException(f'Unknown task type: {cmd}')

        UTILS.AssertIsDict(ret, require=True)
        return ret
