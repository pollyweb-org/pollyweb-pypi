from aws.AWS import AWS
from DEPLOYER_DEPLOY import DEPLOYER_DEPLOY
from DEPLOYER_TASK import DEPLOYER_TASK
from aws.DYNAMO_MOCK import DYNAMO_MOCK
from PW_UTILS.UTILS import UTILS

class DEPLOYER_TASKS():
    
    ICON= '🏗️'
    

    @classmethod
    def _table(cls):
        return DYNAMO_MOCK('TASKS')
    

    @classmethod
    def GetID(cls, 
        deployment:DEPLOYER_DEPLOY, taskName:str) -> str:
        '''👉️ Returns the task ID.'''
        return f'{deployment.RequireID()}_{taskName}'


    @classmethod
    def Register(cls, 
        deployment:DEPLOYER_DEPLOY, 
        tasks:list[DEPLOYER_TASK]
    ):
        '''👉️ Inserts the tasks.'''
        
        # Ensure the parameters.
        UTILS.AssertIsList(tasks, require=True, itemType=DEPLOYER_TASK)
        DEPLOYER_DEPLOY.AssertClass(deployment, require=True)
        
        # Insert the tasks
        for task in tasks:
            item = task.Raw()
            item['ID'] = cls.GetID(deployment, task.RequireFullName())
            item['DeploymentID'] = deployment.RequireID()
            cls._table().Insert(item)
            task.SetTable(cls._table())


    @classmethod
    def GetDeploymentTasks(cls, 
        deployment:DEPLOYER_DEPLOY
    ) -> list[DEPLOYER_TASK]:
        '''👉️ Returns the tasks for a deployment.'''
        
        # Ensure the parameters.
        DEPLOYER_DEPLOY.AssertClass(deployment, require=True)
        
        # Get the tasks
        tasks = cls._table().Query(
            att= 'DeploymentID', 
            equals= deployment.RequireID())
        
        # Sort tasks by task type.
        tasks = sorted(tasks, key=lambda x: x['Type'])
        
        # Convert the list to a list of DEPLOYER_TASK
        ret = DEPLOYER_TASK.ParseList(tasks)

        # Ensure the return value.
        UTILS.AssertIsList(ret, itemType=DEPLOYER_TASK, require=True)
        return ret