from DEPLOYER_EXEC_ARGS import DEPLOYER_EXEC_ARGS
from LOG import LOG
from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS
from dataclasses import dataclass, asdict


class DEPLOYER_EXEC_TASK(STRUCT):

    ICON = '🏗️'
    

    def __init__(self, args:DEPLOYER_EXEC_ARGS) -> None:
        '''👉️ Initializes the task execution.'''
        
        # Just for the logs.
        super().__init__({
            'Task': args.task
        })

        # Assign the arguments.
        self.args = args
        self.task = args.task
        self.results = args.results
        self.simulate = args.simulate
        self.taskDict = args.taskDict
        self.inputs = STRUCT(args.deployArgs.Inputs)
        self.layerArns = args.layerArns

        # Cache the executions.
        self._cached = args.deployArgs.CacheExecutions
        if self._cached: self._cache = UTILS.CACHE()


    def VerifyMissingParameters(self, params:list[str]):
        for param in params:
            if self.task.GetParam(param) == None:
                LOG.RaiseValidationException(
                    f'Required param [{param}] missing'
                    f' in task [{self.task.RequireTypeAndFullName()}]'
                    f' of stack [{self.task.RequireStackName()}].')


    def VerifyAlienParameters(self, params:list[str]):
        '''👉️ Verifies the alien parameters.'''

        UTILS.AssertIsList(params, itemType=str)

        # Loops all task properties, raising errors on unknown properties.
        myParams = self.task.RequireParams()
        myParams.AssertOnlyKeys(params, context= self)
 

    def OnValidate(self):
        '''👉️ Validates the task (TO OVERRIDE).'''
        pass


    def OnExecute(self):
        '''👉️ Executes the task (TO OVERRIDE).'''
        LOG.RaiseException(
            f'🏗️ Implement '
            f' {type(self).__name__}.OnExecute()')


    def Execute(self):
        '''👉️ Executes the task.'''
        LOG.Print(
            f'@('
            f'{self.task.RequireType()}|'
            f'{self.task.RequireFullName()})')
        
        self.OnValidate()
        
        if self.args.simulate: 
            LOG.Print(f'@: Simulation, ignoring.')
            return {}

        try:
            ret = self.OnExecute()
        except Exception as e:
            LOG.Print(
                f'@: failed!'
                f'{self.task.RequireTypeAndFullName()}) failed: '
                f'Error: {str(e)}', self, e)
            raise

        LOG.Print(
            f'@('
            f'{self.task.RequireTypeAndFullName()}) result:', ret)
        
        if ret == None:
            ret = {}
        UTILS.AssertIsDict(ret, require=True)

        return ret


    
    @property
    def forReal(self):
        '''👉️ Returns True if the task is for real.'''
        return not self.simulate
        


    def GetTags(self):
        '''👉️ Returns the common NLWEB tags.'''
        return {
            'NLWEB/Name': self.task.RequireName(),
            'NLWEB/Stack': self.task.RequireStackName(),
            'NLWEB/Type': self.task.RequireType(),
            'NLWEB/CreatedAt': UTILS.GetTimestamp(),
        }
    

    def RequireInput(self, key:str):
        '''👉️ Returns the input.'''
        return STRUCT(self.inputs).RequireAtt(key)
    

    def RequireInputString(self, key:str):
        '''👉️ Returns the input.'''
        return STRUCT(self.inputs).RequireStr(key)
    

    def RequireDependency(self, name:str):
        '''👉️ Returns a task by name.'''

        if '-' not in name:
            stack = self.task.RequireStackName()
            reference = f'{stack}-{name}'
        else:
            reference = name

        if not STRUCT(self.taskDict).ContainsAtt(reference):
            LOG.RaiseException(
                f'@: Dependency [{reference}] not found'
                f' for task [{self.task.RequireTypeAndFullName()}].')

        task = self.taskDict[reference]

        # Test the full name from the reference.
        task.RequireFullName()

        return task


    def GetDependencyMap(self):
        '''👉️ Returns the dependencies for the task.'''
    
        if hasattr(self, 'dependencyMap'):
            return self.dependencyMap    

        @dataclass
        class DEPENDENCY(PRINTABLE):
            FullName:str
            Type:str
            Arn:str
            Name:str

            def RequireArn(self):
                '''👉️ Returns the ARN.'''

                if not self.Arn:
                    LOG.RaiseException(
                        f'@: ARN not found for {self.FullName}.')
                
                return self.Arn
            

        # Create a map of dependencies.
        map:list[DEPENDENCY] = []

        # Get the dependencies.
        from DEPLOYER_TASK import DEPLOYER_TASK
        for fullName in self.task.GetDependencies():
            dep:DEPLOYER_TASK = STRUCT(self.taskDict).RequireAtt(fullName)
            result = dep.RequireResult()
            arn = STRUCT(result).GetStr('Arn')
            type = dep.RequireType()
            name = dep.RequireName()

            map.append(DEPENDENCY(
                FullName= fullName,
                Type= type,
                Arn= arn,
                Name= name
            ))

        self.dependencyMap = map
        return map