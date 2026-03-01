
from DEPLOYER_ARGS import DEPLOYER_ARGS
from pollyweb.parallel.PARALLEL_THREAD_POOL import PARALLEL_THREAD_POOL
from pollyweb.utils.UTILS import UTILS


class DEPLOYER_BASE:

    
    def __init__(self, deployArgs:DEPLOYER_ARGS) -> None:
        
        self._runner: PARALLEL_THREAD_POOL = None
        '''👉️ Parallel thread pool.'''

        self.DeployArgs:DEPLOYER_ARGS = deployArgs
        '''👉️ Deployment options.'''

        self.Cache = UTILS.CACHE(f'__cache__/{self.__class__.__name__}.yaml') 

    
    @classmethod
    def PARSER(cls):
        '''👉️ Returns the DEPLOYER_PARSER class.'''
        from DEPLOYER_PARSER import DEPLOYER_PARSER
        return DEPLOYER_PARSER()
    

    @classmethod
    def EXECUTER(cls):
        '''👉️ Returns the DEPLOYER_EXECUTER class.'''
        from DEPLOYER_EXEC import DEPLOYER_EXEC
        return DEPLOYER_EXEC()
    

    @classmethod
    def TASKS(cls):
        '''👉️ Returns the DEPLOYER_TASKS class.'''
        from DEPLOYER_TASKS import DEPLOYER_TASKS
        return DEPLOYER_TASKS()


    @classmethod
    def DEPLOYS(cls):
        '''👉️ Returns the DEPLOYER_CTRL class.'''
        from DEPLOYER_DEPLOYS import DEPLOYER_DEPLOYS
        return DEPLOYER_DEPLOYS()
    

    @classmethod
    def MAESTRO(cls, deployArgs:DEPLOYER_ARGS):
        '''👉️ Returns the DEPLOYER_MAESTRO class.'''
        from DEPLOYER_MAESTRO import DEPLOYER_MAESTRO
        return DEPLOYER_MAESTRO(deployArgs)