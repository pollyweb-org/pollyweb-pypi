from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_EXEC_PYTHON(DEPLOYER_EXEC_TASK):
    

    def GetHandler(self):
        '''👉️ Gets the handler.'''

        LOG.Print('🏗️ DEPLOYER.EXEC.PYTHON.GetHandler()', self)

        task = self.task

        # Get the handler from the task.
        handler:str = task.GetStringParam('Handler')
        
        # If the handler is not set, then get it from the stack.
        if not UTILS.IsNoneOrEmpty(handler):
            code = f'''
from NLWEB import NLWEB
from PW_AWS.AWS import AWS
{handler}'''
            if not code.endswith(')'):
                exec(code)

            return code

        handler = task.GetStackParam('Handler')
        if not UTILS.IsNoneOrEmpty(handler):
            code = f'''
from {handler} import {handler}
{handler}.Handle{task.RequireName()}'''
            
            exec(code)
            return code

        LOG.RaiseException(
            f'Handler not set for task nor stack.', self)


    def OnValidate(self):
        
        self.VerifyAlienParameters([
            'Handler'
        ])
        
        self.pythonHandler = self.GetHandler()


    def OnExecute(self):
        LOG.Print('🏗️ DEPLOYER.EXEC.PYTHON.OnExecute()', self)

        code = self.pythonHandler
        if not code.endswith(')'):
            code += '(task)'

        LOG.Print('🏗️ DEPLOYER.EXEC.PYTHON.OnExecute: executing code...', code)
        args = { 'task': self }
        ret = exec(code, args)
        return ret