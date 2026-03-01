from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS

class DEPLOYER_EXEC_CERTIFICATE(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):

        self.VerifyAlienParameters([
            'Global'
        ])

        self.certGlobal = self.task.GetBoolParam('Global', False)


    def OnExecute(self):
        
        self.certDomainName= self.results.RequireDependency('DomainName', str)

        ret = AWS.ACM().Ensure(
            domainName= self.certDomainName,
            central= self.certGlobal)
        
        return ret