from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from PW_UTILS.UTILS import UTILS

class DEPLOYER_EXEC_DYNAMO(DEPLOYER_EXEC_TASK):


    def OnValidate(self):

        self.VerifyAlienParameters([
            'Dated',
            'Stream', 
            'TTL',
            'Indexes'
        ])

        self.stream = self.task.GetBoolParam('Stream', default=False)
        self.dated = self.task.GetBoolParam('Dated', default=False)
        self.indexes = self.task.GetListParam('Indexes', itemType=str, default=[])
        self.ttl = self.task.GetBoolParam('TTL', default=False)
        
        # create an alias from the name.
        name = self.task.RequireFullName()
        alias = UTILS.CamelToUppercase(name)

        # Set the table.
        self.table = AWS.DYNAMO(
            alias= alias,
            name= name).Table()
        

    def OnExecute(self):
        #return {}

        tags = self.GetTags()
        
        # Cache is not worth it because table tails are collected indiidually.
        self.table.EnsureExists(tags=tags, cache=False) # Create the table.

        self.table.EnsureStream(self.stream)            # Enable the stream.
        self.table.EnsureTtl(self.ttl)                  # Enable TTL.
        self.table.EnsureIndexes(self.indexes)          # Ensure indexes.
        self.table.EnsurePitr()                         # Enable PITR.

        return {
            'Alias': self.table._alias,
            'TableName': self.table._name,
            'Arn': self.table.GetArn()
        }