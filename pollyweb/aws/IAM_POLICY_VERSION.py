from PW_UTILS.LOG import LOG
from PW_UTILS.PRINTABLE import PRINTABLE
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS


class IAM_POLICY_VERSION(PRINTABLE):
    
    def __init__(self, 
        meta:dict,
        client,
        policy
    ) -> None:
        
        # Get the policy.
        from IAM_POLICY import IAM_POLICY
        UTILS.AssertIsType(policy, IAM_POLICY, require=True)
        self.Policy:IAM_POLICY = policy

        struct = STRUCT(meta)
        self.ID = struct['VersionId']
        self.IsDefaultVersion = struct.RequireBool('IsDefaultVersion')

        self.Client = client

    
    def Delete(self):
        '''👉️ Deletes the policy version.''' 

        LOG.Print('@')

        self.Client.delete_policy_version(
            PolicyArn= self.Policy.GetArn(),
            VersionId= self.ID)


    def GetStatement(self):
        '''👉️ Returns the statement list.'''

        LOG.Print('@')
        
        if hasattr(self, '_Statement'):
            return self._Statement

        details = self.Client.get_policy_version(
            PolicyArn= self.Policy.GetArn(),
            VersionId= self.ID)
        
        self._Statement = details['PolicyVersion']['Document']['Statement']

        return self._Statement
