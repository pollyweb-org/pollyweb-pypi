from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_EXEC_FILE(DEPLOYER_EXEC_TASK):
    pass


    def OnValidate(self):
        dir = self.task.GetDirectory().AssertExists()
        paramPath = self.task.RequireParam('Path')
        self.File = dir.GetFile(paramPath).AssertExists()


    def OnExecute(self):
        return {
            'Content': self.File.ReadText()
        }