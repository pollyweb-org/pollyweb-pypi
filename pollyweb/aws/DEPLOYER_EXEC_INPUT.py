from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from LOG import LOG
from pollyweb.utils.STRUCT import STRUCT

class DEPLOYER_EXEC_INPUT(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):
        '''👉️ Executes a task.'''
        self.VerifyAlienParameters([
            'Optional', 
            'Default'
        ])

    
    def OnExecute(self):
        value = STRUCT(self.inputs).GetStr('Name')
        default = self.task.GetParam('Default')
        optional = self.task.GetBoolParam('Optional', default=False)

        # If the value is None, and a default is provided, use it.
        if value is None:
            if default is not None:
                value = default

        # If the value is still None, and the input is not optional, raise an error.
        if value is None:
            if not optional:
                LOG.RaiseException(
                    f'Input {self.task.RequireFullName()} is required.', 
                    self.task)
                
        # Return the value.
        return { 'Value': value }
        