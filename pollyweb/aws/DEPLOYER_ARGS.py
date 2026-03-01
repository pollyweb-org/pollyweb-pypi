
from dataclasses import dataclass

from aws.AWS import AWS
from LOG import LOG

@dataclass
class DEPLOYER_ARGS:
    '''👉️ Options for the deployer.'''
    
    Name:str= None
    '''👉️ Name of the tag `NLWEB/Deployer` in the AWS account'''
    
    FilterTasks:list[str]= None
    '''👉️ Filter the tasks to execute.'''
    
    Seconds:int= 5
    '''👉️ Seconds to wait for the tasks to complete.'''

    Parallel:bool= False
    '''👉️ If True, the tasks will be executed in parallel.'''
        
    Verify:bool= True
    '''👉️ If True, the tasks will be verified before execution'''

    Simulate:bool= True
    '''👉️ If True, the tasks will be simulated.
    * If False, the tasks will be executed on the account.
    * If executed in the account (reak), the name is required.
    * Default is True (simulate).'''
    
    OnTask:callable= None
    '''👉️ Callback to execute on each task.'''
    
    Inputs:dict= None
    '''👉️ Inputs to pass to the tasks.'''

    CacheLayers:bool= False
    '''👉️ If True, the layer Arn will be cached.'''

    CacheExecutions:bool= False
    '''👉️ If True, the executions will be cached.'''


    def __post_init__(self):
        '''👉️ Verifies the deployer arguments.'''
        if not self.Simulate:
            if not self.Name:
                LOG.RaiseException('Name is required when not simulating')
            self.VerifyAccount(self.Name)


    
    def VerifyAccount(self, name:str):
        '''👉️ Verifies the account.'''

        # Confirm the account.
        user = AWS.IAM().GetUser()
        tag = user.GetTag('NLWEB/Deployer')

        # Verify if the user has the tag.
        if not tag:
            LOG.RaiseException(
                f'Set tag `NLWEB/Deployer`'
                f' on user `{user.RequireUserName()}`'
                f' on account `{user.RequireAccount()}`.')
            
        # Verify if the tag is the expected.
        if tag != name:
            LOG.RaiseException(
                f'Wrong account - log into the right one!\n'
                f'Tag `NLWEB/Deployer`'
                f' on user `{user.RequireUserName()}`'
                f' on account `{user.RequireAccount()}`'
                f' has value `{tag}`'
                f' when the expected was `{name}`.')
            