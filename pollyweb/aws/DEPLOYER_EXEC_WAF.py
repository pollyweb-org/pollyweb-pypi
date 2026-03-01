from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_EXEC_WAF(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):

        self.VerifyAlienParameters([
            'Global'
        ])

        self.Global = self.task.GetBoolParam('Global', default=False)


    def OnExecute(self):
        '''👉️ Executes a GlobalWebAcl task.'''
        return {}
        if self.Global:
            return AWS.WAF().EnsureGlobalWebAcl(
                name= self.task.RequireFullName())
        else:
            return AWS.WAF().EnsureRegionalWebAcl(
                name= self.task.RequireFullName())
