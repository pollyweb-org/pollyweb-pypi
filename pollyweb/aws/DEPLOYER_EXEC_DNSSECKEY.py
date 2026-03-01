from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK

class DEPLOYER_EXEC_DNSSECKEY(DEPLOYER_EXEC_TASK):


    def OnExecute(self):
        '''👉️ Executes a DnsSecKey task.'''
        
        # Get the default tags.
        tags = self.GetTags()

        # Create the key.
        from aws.KMS_REAL import KMS_REAL
        keyDetails = KMS_REAL.CreateForDnsSec(tags=tags)

        # return the Arn and ID.
        return keyDetails