from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG

class DEPLOYER_EXEC_SNS(DEPLOYER_EXEC_TASK):


    def OnValidate(self):
        self.VerifyAlienParameters([])


    def OnExecute(self):
        LOG.Print(self.OnExecute, self)

        name = self.task.RequireFullName()
        name = name.replace('.', '-')
        
        arn = AWS.SNS().Ensure(name)

        return {
            'Name': name,
            'ARN': arn
        }