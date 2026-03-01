from DEPLOYER_BASE import DEPLOYER_BASE
from DEPLOYER_DEPLOY import DEPLOYER_DEPLOY
from DEPLOYER_EXEC_ARGS import DEPLOYER_EXEC_ARGS
from DEPLOYER_TASK import DEPLOYER_TASK
from LOG import LOG
from PW_PARALLEL.PARALLEL import PARALLEL
from DEPLOYER_TASK import DEPLOYER_TASK
from PW_UTILS.UTILS import UTILS
from DEPLOYER_MAESTRO_EXEC_ARGS import DEPLOYER_MAESTRO_EXEC_ARGS


class DEPLOYER_MAESTRO_PARALLEL(DEPLOYER_BASE):


    # Define the task runner
    def taskRunner(self, task:DEPLOYER_TASK):

        try:
            # Get the results of previous dependency executions.
            results = self.Deployment.GetResultsForTaskDependencies(task)

            # Execute the task
            result = self.EXECUTER().ExecuteTask(
                DEPLOYER_EXEC_ARGS(
                    deployArgs= self.DeployArgs,
                    simulate= self.DeployArgs.Simulate,
                    taskDict= self.TaskDict,
                    task= task,
                    results= results,
                    layerArns= self.LayerArns))
            
            # Mark the task as finished
            self.Deployment.MarkTaskAsFinished(
                task=task, 
                result=result)

        except Exception as e:
            import traceback
            stack_trace = traceback.format_stack()
            self.Deployment.MarkAsFailed(e, stack_trace)
            raise
    
    
    def _ExecuteLocalInParallel(self, 
        execArgs:DEPLOYER_MAESTRO_EXEC_ARGS,
        deployment:DEPLOYER_DEPLOY,
        layerArns: list[str]= None,
        goUp:int=0
    ):
        LOG.Print('🏗️ DEPLOYER.MAESTRO._ExecuteLocalInParallel()', dict(
            options= execArgs,
            deployment= deployment,
            layerArns= layerArns,
        ))
            
        self.Deployment = deployment
        self.LayerArns = layerArns

        self.TaskDict = deployment.GetTaskDictionary()
    
        runner = PARALLEL.THREAD_POOL(
            name= self.DeployArgs.Name,
            seconds= self.DeployArgs.Seconds,
            continueMethod= deployment.IsPending,
            goUp= goUp+1)
        deployment._runner = runner
        
        for task in deployment.GetTaskList(): 

            if self.DeployArgs.FilterTasks \
            and task.RequireFullName() not in self.DeployArgs.FilterTasks:
                continue

            runner.AddThread(
                name= task.RequireTypeAndFullName(),
                handler= self.taskRunner,
                args= dict(task= task), 
                continueMethod= deployment.TaskHasNoPendingDependencies,
                goUp= goUp+1)

        try:
            results = runner.RunAllThreads()
            deployment.MarkAsFinished()

            if execArgs.AssertMethod:
                execArgs.AssertMethod()
                
            return results  

        except Exception as e:
            LOG.Print(f"An error occurred, updating deployment: {e}")
            deployment.MarkAsFailed(e, 'MY-STACK-TRACE')
            raise e
