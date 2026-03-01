from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_DEPLOY import DEPLOYER_DEPLOY
from DEPLOYER_TASK import DEPLOYER_TASK
from aws.DYNAMO_MOCK import DYNAMO_MOCK
from LOG import LOG
from pollyweb.utils.STRUCT import STRUCT   
from pollyweb.utils.UTILS import UTILS 
from aws.AWS import AWS

class DEPLOYER_DEPLOYS(STRUCT):
    

    @classmethod
    def _table(cls):
        return DYNAMO_MOCK('DEPLOYS')
    

    @classmethod
    def DEPLOY(cls):
        '''👉️ Returns the DEPLOYER_DEPLOY class.'''
        from DEPLOYER_DEPLOY import DEPLOYER_DEPLOY
        return DEPLOYER_DEPLOY()


    @classmethod
    def Register(cls, deployArgs:DEPLOYER_ARGS) -> DEPLOYER_DEPLOY:
        '''👉️ Inserts a deployment record.'''
        LOG.Print('@', deployArgs)

        UTILS.AssertIsType(deployArgs, DEPLOYER_ARGS, require=True)

        # Generate a deployment record.
        deploy = DEPLOYER_DEPLOY({
            'ID': UTILS.UUID(),
            'Status': 'PENDING',
            'StartedAt': UTILS.GetTimestamp(),
            'DeployOrder': [],
            'Inputs': deployArgs.Inputs
        })
        
        # Insert the deployment record.
        item = cls._table().Insert(deploy, days= 1)
        
        # Return the deployment.
        return DEPLOYER_DEPLOY(item)
    

    @classmethod
    def RequireDeployment(cls, deployID:str) -> DEPLOYER_DEPLOY:
        '''👉️ Returns a deployment record.'''
        return cls._table().Require(deployID)
    

    