from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_EXEC_POSTPROCESSOR(DEPLOYER_EXEC_TASK):
    

    def OnExecute(self):
        # Post processors are not to be executed inline.
        # They should only be executed as dependency.
        return {}