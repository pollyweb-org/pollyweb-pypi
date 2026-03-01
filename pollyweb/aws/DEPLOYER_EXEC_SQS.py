from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from PW_UTILS.UTILS import UTILS


class DEPLOYER_EXEC_SQS(DEPLOYER_EXEC_TASK):


    def OnValidate(self):

        self.VerifyAlienParameters([
            'Trigger'
        ])

        # Validate the trigger setting.
        triggerName = self.task.GetStringParam('Trigger')
        if not triggerName:
            self.Trigger = None
        else:
            self.Trigger = self.RequireDependency(triggerName)
            UTILS.AssertEqual(self.Trigger.RequireType(), 'SnsTopic')
    

    def OnExecute(self):
        LOG.Print(self.OnExecute, self)

        # Ensure the SQS exists.
        name = self.task.RequireFullName()
        name = name.replace('.', '-')
        queue = AWS.SQS().Ensure(name)

        # Handle the trigger.
        if self.Trigger:
            topicName = self.Trigger.RequireFullName()
            topic = AWS.SNS().Require(name= topicName)
            queue.SubscribeSnsTopic(topic= topic)
        
        # Return the SQS definitions.
        return {
            'Name': name,
            'Arn': queue.Arn
        }
