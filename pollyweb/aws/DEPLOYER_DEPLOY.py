from LOG import LOG
from DEPLOYER_RESULTS import DEPLOYER_RESULTS
from DEPLOYER_TASK import DEPLOYER_TASK
from aws.ITEM import ITEM
from pollyweb.parallel.PARALLEL_THREAD_POOL import PARALLEL_THREAD_POOL
from pollyweb.utils.STRUCT import STRUCT   
from pollyweb.utils.UTILS import UTILS 

class DEPLOYER_DEPLOY(ITEM):
    '''👉️ A deployment record.
    
    Example:
        ID: <UUID>
        Status: 'PENDING'
        StartedAt: <Timestamp>
        Trace: 

        Tasks: 
            ```python```
            - stack: MyStack
              asset: RestApi
              type: RestApi
            - stack: MyStack
              asset: DomainName
              type: SsmParameter
              params:
                Name: MyParam
                Value: MyValue
            ```python```
    '''
    
    ICON= '🏗️'


    def __init__(self, trx:dict):
        '''👉️ Initializes the deployment record.'''
        super().__init__(trx)
        self._runner: PARALLEL_THREAD_POOL = None
        self._tasksCache: dict = None
    

    def GetRunner(self):
        '''👉️ Returns the runner.'''
        return self._runner


    def RequireID(self) -> str:
        '''👉️ Returns the deployment ID.'''
        return self.RequireStr('ID')
    

    def RequireStartedAt(self) -> str:
        '''👉️ Returns the deployment started at.'''
        return self.RequireTimestamp('StartedAt')


    def GetFinishedAt(self) -> str:
        '''👉️ Returns the deployment finished at.'''
        return self.GetTimestamp('FinishedAt')


    def RequireFinishedAt(self) -> str:
        '''👉️ Returns the deployment finished at.'''
        return self.RequireTimestamp('FinishedAt')


    def RequireStartedAtAsDateTime(self):
        '''👉️ Returns the deployment started at as a datetime.'''
        return self.RequireDateTime('StartedAt')
    

    def RequireFinishedAtAsDateTime(self):
        '''👉️ Returns the deployment finished at as a datetime.'''
        if self.IsPending():
            return LOG.RaiseException('Deployment is pending.', self)
        return self.RequireDateTime('FinishedAt')
    

    def RequireTask(self, taskName:str):
        '''👉️ Returns the task with the given name.'''
        tasks = self.RequireTasks()
        task = tasks.RequireStruct(taskName, 
            msg=f'Task not found: {taskName}')
        ret = DEPLOYER_TASK.Parse(task)
        UTILS.Require(ret, msg=f'Error parsing task: {taskName}')
        return ret
        

    def RequireTasks(self) -> STRUCT:
        '''👉️ Returns the tasks dictionary.'''
        #LOG.Print(f'@', self)

        if self._tasksCache != None:
            return self._tasksCache

        # Import the tasks from the DEPLOYER_TASKS module
        from DEPLOYER_TASKS import DEPLOYER_TASKS
        tasks = DEPLOYER_TASKS().GetDeploymentTasks(self)

        # Sort the tasks by type
        tasks = UTILS.SortList(tasks, key= 'Type')

        # Convert the list to a dictionary, using the task name as the key
        tasks = UTILS.DictFromList(tasks, 
            key= DEPLOYER_TASK.RequireFullName)
        
        # Return the dictionary of tasks
        LOG.Print(f'@: done. len={tasks.Length()}', self)
        
        self._tasksCache = tasks
        return self._tasksCache
    

    def GetTaskList(self) -> list[DEPLOYER_TASK]:
        '''👉️ Returns the list of tasks.'''   
        LOG.Print(self.GetTaskList)

        tasks = self.RequireTasks()
        return DEPLOYER_TASK.FromStructs(tasks)
    

    def GetTaskDictionary(self):
        '''👉️ Returns the dictionary of tasks.'''
        tasks = self.GetTaskList()
        return UTILS.DictFromList(tasks, 
            key= DEPLOYER_TASK.RequireFullName)


    def GetPendingTasks(self):
        '''👉️ Returns a list of pending tasks.'''
        LOG.Print(self.GetPendingTasks)

        # Initialize the return list
        ret:list[DEPLOYER_TASK] = []

        # Iterate through the tasks, adding pending tasks to the list
        for task in self.GetTaskList():
            if task.IsPending():
                ret.append(DEPLOYER_TASK(task))

        # Return the list of pending tasks
        return ret
    

    def EnsureIsPending(self):
        '''👉️ Ensures that the deployment is pending.'''
        if self.IsPending() == False:
            LOG.RaiseException('Deployment is not pending.')


    def IsFinished(self) -> bool:
        '''👉️ Returns True if the deployment is finished.'''
        return self.RequireStatus() == 'FINISHED'
    

    def IsFailed(self) -> bool:
        '''👉️ Returns True if the deployment is failed.'''
        return self.RequireStatus() == 'FAILED'


    def IsPending(self) -> bool:
        '''👉️ Returns True if there's any pending task.'''
        if len(self.GetPendingTasks()) == 0:
            return False
        if self.RequireStatus() != 'PENDING':
            return False
        return True
    

    def TaskHasNoPendingDependencies(self, task:DEPLOYER_TASK) -> bool:
        '''👉️ Returns True if the task has no pending dependencies.'''
        return self.TaskHasPendingDependencies(task) == False


    def TaskHasPendingDependencies(self, task:DEPLOYER_TASK) -> bool:
        '''👉️ Returns True if the task has any pending dependencies.'''
        
        # Iterate through the dependencies.
        for taskName in task.RequireDependencies():

            # Get the dependency.
            dependency = self.RequireTask(taskName)
            UTILS.Require(dependency, msg='Dependency not found.')

            # Check if the dependency is pending.
            if dependency.IsPending():
                return True
            
        # Return False if no pending dependencies were found.
        return False
    

    def GetResultsForTaskDependencies(self, 
        task:DEPLOYER_TASK
    ) -> DEPLOYER_RESULTS:
        '''👉️ Returns the results for the dependencies of a task.'''

        LOG.Print('🏗️ DEPLOYER: getting results for dependencies', task)
        
        # Initialize the return dictionary
        ret = {}
        
        # Ensure there is at least one dependency.
        dependencies = task.RequireDependencies()        
        if len(dependencies) == 0:
            return None

        # Iterate through the dependencies.
        for taskName in dependencies:

            # Get the dependency.
            dependency = self.RequireTask(taskName)

            # Ensure the dependency is finished.
            dependency.EnsureIsFinished()

            # Add the dependency result to the return dictionary.
            ret[taskName] = dependency.RequireResult()

        # Return the dictionary of dependency results.
        LOG.Print('🏗️ DEPLOYER: results for dependencies', ret)
        return DEPLOYER_RESULTS(ret)


    def MarkTaskAsFinished(self, task:DEPLOYER_TASK, result:dict|STRUCT):
        '''👉️ Marks a task as finished.'''
        LOG.Print(
            f'@: {task.RequireTypeAndFullName()}', 
            task, result)

        UTILS.AssertIsType(task, DEPLOYER_TASK, require=True)
        UTILS.AssertIsDict(result, require=True)
        
        # Mark the task as finished
        task.MarkAsFinished(result)

        # Update the task record on the database
        if task.HasTable():
            task.UpdateItem()

        # Update the deployment record on the database
        self.DeployOrder().append(
            f'{task.RequireType()}|{task.RequireFullName()}')
        

    def DeployOrder(self) -> list[str]:
        '''👉️ Returns the deployment order.'''
        return self.GetList('DeployOrder')


    def MarkAsFinished(self):
        '''👉️ Marks the deployment as finished.
            * It reloads the item becase there are concurrent updates.'''
        
        # Update the database record
        trx = self.Reload()
        trx['Status'] = 'FINISHED'
        trx['FinishedAt'] = UTILS.TIME().GetTimestamp()
        trx.UpdateItem()

        # Update the local object
        self['Status'] = trx['Status']
        self['FinishedAt'] = trx['FinishedAt']


    def MarkAsFailed(self, 
        e:Exception=None, 
        stackTrace:str=None
    ):
        '''👉️ Marks the deployment as failed.
            * It reloads the item becase there are concurrent updates.'''
        
        LOG.Print('🏗️ DEPLOYER.DEPLOY: marking deployment as failed', self)
        
        # Update the database record
        trx = self.Reload()
        trx['Status'] = 'FAILED'
        trx['FinishedAt'] = UTILS.TIME().GetTimestamp()

        # Get exception stack strace
        if stackTrace != None:
            trx['ErrorStack'] = stackTrace
            self['ErrorStack'] = trx['ErrorStack']
        else:
            trx['ErrorStack'] = '<EMPTY>'
            self['ErrorStack'] = trx['ErrorStack']

        if e != None:
            trx['ErrorMessage'] = str(e)
            trx['ErrorType'] = type(e).__name__
            self['ErrorMessage'] = trx['ErrorMessage']
            self['ErrorType'] = trx['ErrorType']

        trx.UpdateItem()

        # Update the local object
        self['Status'] = trx['Status']
        self['FinishedAt'] = trx['FinishedAt']

        LOG.Print('🏗️ DEPLOYER.DEPLOY.MarkAsFailed', self)


    def RequireStatus(self) -> str:
        '''👉️ Returns the deployment status.
            * It loads the last status from the database because of concurrent updates.'''
        trx = self.Reload()
        return trx.RequireStr('Status')

    
    def GetDurationInSeconds(self) -> str:
        '''👉️ Returns the duration of the deployment.'''

        if not self.GetFinishedAt():
            return None
        
        return UTILS.TIME().GetDurationInSeconds(
            self.RequireStartedAtAsDateTime(), 
            self.RequireFinishedAtAsDateTime())


    def GetErrorMessage(self) -> str:   
        '''👉️ Returns the error message.'''
        return self.GetStr('ErrorMessage')
    

    def GetErrorType(self) -> str:
        '''👉️ Returns the error type.'''
        return self.GetStr('ErrorType')


    def GetErrorStack(self) -> str:
        '''👉️ Returns the error stack.'''
        return self.GetStr('ErrorStack')


    def __to_json__(self):
        '''👉️ Returns the deployment as a yaml struct.'''
        return {
            'Status': self.RequireStatus(),
            #'ErrorType': self.GetStr('ErrorType'),
            #'ErrorStack': self.GetStr('ErrorStack'),
            #'ErrorMessage': self.GetStr('ErrorMessage'),
            'StartedAt': self.RequireStartedAt(),
            'FinishedAt': self.GetFinishedAt(),
            'DurationInSeconds': self.GetDurationInSeconds(),
            'DeployOrder': self.DeployOrder(),
            'Inputs': self.GetInputs()
        }
    

    def GetInputs(self) -> dict:
        '''👉️ Returns the deployment inputs.'''
        return self.GetDict('Inputs')