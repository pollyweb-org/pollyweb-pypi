from aws.AWS import AWS
from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_DEPLOY import DEPLOYER_DEPLOY
from DEPLOYER_EXEC_ARGS import DEPLOYER_EXEC_ARGS
from DEPLOYER_MAESTRO_EXEC_ARGS import DEPLOYER_MAESTRO_EXEC_ARGS
from DEPLOYER_MAESTRO_PARALLEL import DEPLOYER_MAESTRO_PARALLEL
from DEPLOYER_TASK import DEPLOYER_TASK
from LOG import LOG
from pollyweb.parallel.PARALLEL import PARALLEL
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS
from DEPLOYER_BASE import DEPLOYER_BASE


class DEPLOYER_MAESTRO(
    DEPLOYER_MAESTRO_PARALLEL,
    DEPLOYER_BASE
):

    ICON= '🏗️'
        
    
    def CheckForInfiniteLoops(self, tasks:list[DEPLOYER_TASK]):
        '''👉️ Checks for infinite loops in task dependencies.'''

        LOG.Print(self.CheckForInfiniteLoops)

        # Ensure the tasks are of the correct type
        UTILS.AssertIsList(tasks, 
            itemType= DEPLOYER_TASK, 
            require= True)

        # Convert the list to a dictionary, using the task name as the key
        taskDictionary = UTILS.DictFromList(tasks, 
            key= DEPLOYER_TASK.RequireFullName)
        LOG.Print(self.CheckForInfiniteLoops, 
            f': convert to dictionary=', taskDictionary)
        
        # Iterate through the tasks
        for task in tasks:
            self._CheckForInfiniteLoopsHelper(
                taskDictionary= taskDictionary, 
                task= task, 
                path= [])

    
    def _CheckForInfiniteLoopsHelper(self, 
        taskDictionary:dict[str, DEPLOYER_TASK],
        task:DEPLOYER_TASK, 
        path:list[str]
    ):
        '''👉️ Recurrent function to check for infinite loops in task dependencies.'''
        #LOG.Print('🏗️ DEPLOY.MAESTRO._CheckForInfiniteLoopsHelper()', 'path=', path)

        # Ensure the parameters are of the correct type        
        DEPLOYER_TASK.AssertClass(task, require=True)
        UTILS.AssertIsDict(taskDictionary, require=True )
        UTILS.AssertIsList(path, itemType=str, require=False)
        
        # Check if the task is already in the path
        if task.RequireFullName() in path:
            LOG.RaiseValidationException(
                'Infinite loop detected:', 
                'task=', task.RequireFullName(),
                'in=', path)
            
        # Add the task to the path
        path.append(task.RequireFullName())

        # Check the dependencies
        for dep in task.RequireDependencies():
            
            # Catch invalid dots.
            if '.' in dep:
                LOG.RaiseException(
                    f'@: Dependency names cannot contain dots,'
                    f' dependency= {dep},'
                    f' in task= {task.RequireFullName()}')
            
            # Check if the dependency exists
            task = STRUCT(taskDictionary).RequireAtt(dep)

            # Recursively check the dependencies
            self._CheckForInfiniteLoopsHelper(
                taskDictionary= taskDictionary,
                task= task, 
                path= path.copy())
            
            
    def ExecuteTasks(self, 
        args:DEPLOYER_MAESTRO_EXEC_ARGS,
        goUp:int=0
    ):
        '''👉️ Executes a deployment file.'''

        LOG.Print(self.ExecuteTasks, args)
        
        # 👉️ Clear the test execution records.
        from DEPLOYER_EXEC_DUMMY import DEPLOYER_EXEC_DUMMY
        DEPLOYER_EXEC_DUMMY.DummyExecutions = []

        # 👉️ Using a recurrent function, Look for infinit loops in task dependencies
        self.CheckForInfiniteLoops(args.Tasks)

        # 👉️ Register the deployment
        deployment = self.DEPLOYS().Register(
            deployArgs= self.DeployArgs)
        
        # 👉️ Register the tasks
        self.TASKS().Register(
            deployment= deployment,
            tasks= args.Tasks)

        # 👉️ Execute the deployment
        if AWS.LAMBDA().IsLambda():
            LOG.RaiseException('This is not tested yet!')
            
        try:
            
            # Prepare the layers if not already cached.
            layerArns = None
            if self.DeployArgs.CacheLayers:
                layerArns = self.Cache.Get('LayerArns')
            
            if not layerArns:
                # Prepare the layers.
                layerArns = self._PrepareLayers(
                    simulate= self.DeployArgs.Simulate)
                # Cache the layer ARNs.
                if not self.DeployArgs.Simulate:
                    self.Cache.Set('LayerArns', layerArns)

            if self.DeployArgs.Parallel:
                self._ExecuteLocalInParallel(
                    execArgs= args,
                    deployment= deployment,
                    layerArns= layerArns,
                    goUp= goUp+1)
            else:
                self._ExecuteLocalInSequence(
                    execArgs= args,
                    deployment= deployment,
                    layerArns= layerArns)
                    
            self._runner = deployment.GetRunner()
                
        except Exception as e:
            LOG.Print(self.ExecuteTasks, f': Error=', e)
            raise
        
        finally:
            if not self.DeployArgs.Simulate:
                self.CleanLayers()
            
        return deployment


    def _ExecuteLocalInSequence(self, 
        execArgs:DEPLOYER_MAESTRO_EXEC_ARGS,
        deployment:DEPLOYER_DEPLOY,
        layerArns: list[str]= None
    ):
        LOG.Print(self._ExecuteLocalInSequence)

        lastExecuted:int = 0
        nowExecuted:int = 0

        taskDict = deployment.GetTaskDictionary()
        taskLength = taskDict.Length()
        if taskLength == 0:
            LOG.RaiseException('No tasks to execute!')

        # Execute the deployment until all tasks are finished
        while deployment.IsPending():

            # Iterate through the pending tasks
            for task in deployment.GetPendingTasks():
                
                # Skip tasks with pending dependencies
                results = None
                if task.HasDependencies():
                    if deployment.TaskHasPendingDependencies(task):
                        continue    
                
                    # Get the results for the task dependencies
                    results = deployment.GetResultsForTaskDependencies(task)
                    
                # Check the cache for a previous result.
                cacheKey = f'Task.{task.RequireTypeAndFullName()}'
                result = self.Cache.Get(cacheKey)
                
                if result != None:
                    UTILS.Require(result, 
                        msg=f'Cache not set for task: {task.RequireFullName()}')

                # If no result was found, execute the task.
                if result == None:
                    # Execute the task
                    result = self.EXECUTER().ExecuteTask(
                        DEPLOYER_EXEC_ARGS(
                            simulate= self.DeployArgs.Simulate,
                            deployArgs= self.DeployArgs,
                            taskDict= taskDict,
                            task= task,
                            results= results,
                            layerArns= layerArns))
                    
                    # Cache the result
                    self.Cache.Set(cacheKey, result)
                    
                # Execute the onTask callback
                if self.DeployArgs.OnTask:
                    self.DeployArgs.OnTask(task, result)

                # Mark the task as finished
                deployment.MarkTaskAsFinished(
                    task= task, 
                    result= result)
                
                # Increment the counter
                nowExecuted += 1

            # Check for extra work:
            if taskLength < nowExecuted:
                LOG.RaiseException(
                    '🏗️ DEPLOYER.MAESTRO._ExecuteLocalInSequence: ',
                    'taskLength < nowExecuted:', taskLength, nowExecuted)

            # Check for deadlocks
            if lastExecuted == nowExecuted:

                # Get the names of the pending tasks
                pendingTaskNames = []
                for task in deployment.GetPendingTasks():
                    pendingTaskNames.append(task.RequireFullName())

                # If no tasks were executed, there's a deadlock.
                LOG.RaiseValidationException(
                    'Deadlock detected:', pendingTaskNames)

            lastExecuted = nowExecuted
                
        # Mark the deployment as finished
        deployment.MarkAsFinished()

        if execArgs.AssertMethod:
            execArgs.AssertMethod()

        return deployment
        

    def _PrepareLayers(self, simulate:bool):
        '''👉️ Prepares the deployment layers.'''
        LOG.Print(self._PrepareLayers)

        # Ensure the current directory is PollyWeb/NLWEB.
        current = UTILS.OS().CurrentDirectory()
        if current.GetName() not in ['NLWEB', 'PollyWeb']:
            LOG.RaiseException('Run this from the PollyWeb directory.')

        # Prepare the layers directory
        layers = current.GetSubDir('layers')
        
        # Prepare PyYAML package
        layers.GetFile('pyyaml.zip').Unzip()
        pyyaml = layers.GetSubDir('pyyaml').AssertExists()

        # Prepare nlweb package
        nlweb = layers.GetSubDir('nlweb').Touch()
        nlweb = nlweb.GetSubDir('python').Touch()
        for file in UTILS.OS().Directory('python').GetDeepFiles('.py'):
            file.CopyTo(nlweb)
        nlweb = nlweb.GetParentDir()

        # If simulating, don't deploy the layers.
        if simulate:
            return []
        
        # Deploy the layers.
        lbda = AWS.LAMBDA()
        
        runner = PARALLEL.THREAD_POOL()

        runner.AddThread(
            name= 'CreateLayer pyyaml',
            handler= lbda.CreateLayer,
            args= dict(
                dir= pyyaml,
                layerName= 'NLWEB-yaml'))
        
        runner.AddThread(
            name= 'CreateLayer nlweb',
            handler= lbda.CreateLayer,
            args= dict(
                dir= nlweb, 
                layerName= 'NLWEB-nlweb'))
        
        arns = runner.RunAllThreads()
        LOG.Print(self._PrepareLayers, f': arns=', arns)
        UTILS.AssertIsDict(arns, require=True)
        UTILS.AssertLenght(arns.Attributes(), expectedLength=2)

        # Return the ARNs
        return [
            STRUCT(arn).RequireStr('Arn')
            for arn in arns.GetDict().values()
        ]


    def CleanLayers(self):
        '''👉️ Cleans the deployment layers.'''
        LOG.Print(self.CleanLayers)
        
        layers = UTILS.OS().Directory('layers')

        # Delete pyyaml package content
        #layers.GetSubDir('pyyaml').Delete(recursive=True)

        # Delete nlweb package content
        layers.GetSubDir('nlweb').Delete(recursive=True)

        # Delete unused layer versions
        lbda = AWS.LAMBDA()

        runner = PARALLEL.THREAD_POOL() 
        
        for layer in ['NLWEB-yaml', 'NLWEB-nlweb']:
            runner.AddThread(
                name= f'Delete unused versions from layer= {layer}',
                handler= lbda.DeleteUnusedLayerVersions,
                args= { 
                    'layerName': layer
                })
            
        runner.RunAllThreads()
