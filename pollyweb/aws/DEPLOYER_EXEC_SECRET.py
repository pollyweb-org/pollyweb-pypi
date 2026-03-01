from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_EXEC_SECRET(DEPLOYER_EXEC_TASK):
    pass


    def OnValidate(self):
        '''👉️ Validates the task.'''
        self.VerifyAlienParameters([
            'Name'
        ])


    def OnExecute(self):
        '''👉️ Executes the task.'''
        LOG.Print(self.OnExecute)

        name = self.task.RequireParam('Name')
        secret = AWS.SECRETS().Get(name)

        # If the secret does not exist, create it.
        value = self.task.GetParam('Value')
        if value == None: value = 'empty'
        secret.SetValue(value)

        # Return the ARN of the secret, for dependencies.
        return {
            'Arn': secret.GetArn(),
            'Name': name
        }
    