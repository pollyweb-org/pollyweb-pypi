from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_EXEC_PARAMETER(DEPLOYER_EXEC_TASK):


    def OnValidate(self):
        LOG.Print('🏗️ DEPLOYER.EXEC.PARAMETER.OnValidate()')

        self.VerifyAlienParameters([
            'Name',
            'Value'
        ])

        self.nameParam = self.task.RequireParam('Name')
        self.valueParam = self.task.GetParam('Value')


    def OnExecute(self):
        '''👉️ Executes a SsmParameter task.'''
        LOG.Print('🏗️ DEPLOYER.EXEC.PARAMETER.OnExecute()')

        # Look for the value in the dependenciy results.
        if UTILS.IsNoneOrEmpty(self.valueParam):
            dependencies = self.task.GetDependencies()
            results = self.results

            for fullName in dependencies:
                
                dependency = STRUCT(self.taskDict).RequireAtt(fullName)
                LOG.Print('@: dependency',
                    {
                        'fullName': fullName,
                        'dependency': dependency
                    })
                
                # If the dependency is an input, get the value.
                if dependency.RequireType() == 'Input':
                    result = results.RequireStruct(fullName)
                    value = result.RequireAtt('Value')

                    # If the value is a string, use it.
                    if UTILS.IsString(value):
                        self.valueParam = value
                    else:
                        # If the value is an object, convert it to JSON.
                        self.valueParam = UTILS.ToJson(value)

                    # If the value is not empty, break the loop.
                    break

        # If the value is still empty, try to read the param.
        if UTILS.IsNoneOrEmpty(self.valueParam):
            param = self.valueParam = AWS.SSM().Get(
                name= self.nameParam,
                optional= True)
            self.valueParam = param

        # If the value is still empty, raise an exception.
        if UTILS.IsNoneOrEmpty(self.valueParam):
            LOG.RaiseException('Value not found in dependencies.', 
                f'Param={self.nameParam}', dependencies, results)

        AWS.SSM().EnsureParameter(
            name= self.nameParam,
            value= self.valueParam)
    
        return {
            'Name': self.nameParam,
            'Value': self.valueParam
        }