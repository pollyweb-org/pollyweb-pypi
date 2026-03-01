from aws.AWS import AWS
from DEPLOYER_DEPLOY import DEPLOYER_DEPLOY
from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_MAESTRO_EXEC_ARGS import DEPLOYER_MAESTRO_EXEC_ARGS
from LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from DEPLOYER_BASE import DEPLOYER_BASE
from PW_UTILS.UTILS import UTILS



class DEPLOYER(DEPLOYER_BASE):
    ICON= '🏗️'

    def __init__(self, 
        deployArgs:DEPLOYER_ARGS,
        goUp:int=0
    ) -> None:
        '''👉️ Initializes the deployer.'''

        LOG.Print('🏗️ DEPLOYER.__init__()', deployArgs)
        
        super().__init__(deployArgs)
        
        # Prepare the runner to be able to delete the logs.
        from PW_PARALLEL.PARALLEL_THREAD_POOL import PARALLEL_THREAD_POOL
        self._runner:PARALLEL_THREAD_POOL = None


    def Maestro(self):
        '''👉️ Returns the DEPLOYER_MAESTRO class.'''
        return self.MAESTRO(self.DeployArgs)


    def ExecuteDirectory(self, 
        path:str,
        assertMethod:callable= None,
        goUp:int=0
    ):
        '''👉️ Executes all deployment files in a directory.'''
        LOG.Print(self.ExecuteDirectory, f'{path=}')

        # Load the tasks from cache, or parse them.
        from DEPLOYER_TASK import DEPLOYER_TASK
        cached = self.Cache.Get('Tasks')

        if cached:
            # Convert the cached tasks to DEPLOYER_TASK.
            tasks = DEPLOYER_TASK.ParseList(cached)
        else:

            # Load the tasks.
            tasks = self.PARSER().DirectoryToTasks(path)
            LOG.Print('🏗️ DEPLOYER.ExecuteDirectory:', 
                f'{len(tasks)} tasks found.')

            # Verify the tasks
            if self.DeployArgs.Verify:
                self.EXECUTER().VerifyTasks(
                    tasks= tasks, 
                    deployArgs= self.DeployArgs)
                
            # Save the tasks to cache
            self.Cache.Set('Tasks', tasks)

        # Execute the tasks
        LOG.Print(self.ExecuteDirectory, 
            f'{len(tasks)} tasks to execute.')
        
        deployment = self.Maestro().ExecuteTasks(
            DEPLOYER_MAESTRO_EXEC_ARGS(
                Tasks= tasks,
                AssertMethod = assertMethod), 
            goUp= goUp+1)
        
        DEPLOYER_DEPLOY.AssertClass(deployment, require=True)
        self._runner = deployment.GetRunner()
        return deployment
            

    def ExecuteFile(self, path:str):
        '''👉️ Executes a deployment file.'''        
        tasks = self.PARSER().FileToTasks(path)
        self.Maestro().ExecuteTasks(tasks)
        

    def ExecuteYaml(self, 
        stack:str, 
        yaml:STRUCT, 
        path:str,
        goUp:int=0
    ):
        '''👉️ Executes a deployment yaml struct.'''

        LOG.Print('🏗️ DEPLOYER.ExecuteYaml()', dict(
            stack= stack, 
            #yaml= yaml, # Too big to print.
            path= path
        ))
        
        tasks = self.PARSER().YamlToTasks(
            stack, 
            yaml= yaml, 
            path= path)
        
        deploy = self.Maestro().ExecuteTasks(
            DEPLOYER_MAESTRO_EXEC_ARGS(
                Tasks= tasks),
            goUp= goUp+1)
        
        self._runner = deploy.GetRunner()

        return self


    def ExecuteYamls(self, stack:str, yamls:list[STRUCT]):
        '''👉️ Executes a list of deployment yaml structs.'''
        tasks = self.PARSER().YamlsToTasks(stack, yamls)
        self.Maestro().ExecuteTasks(tasks)