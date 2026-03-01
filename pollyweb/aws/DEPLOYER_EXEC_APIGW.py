from aws.ACM_CERTIFICATE import ACM_CERTIFICATE
from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from aws.WAF_WACL import WAF_WACL

class DEPLOYER_EXEC_APIGW(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):
        
        self.VerifyAlienParameters(['Handlers'])
        
        self.apiHandlers = self.task.GetDictParam('Handlers', itemType=str)
        self.apiName= self.task.RequireFullName()


    def OnExecute(self):

        self.apiDomainName= self.results.GetDependency('DomainName', str)
        self.apiCertificate= self.results.GetDependencyByType(ACM_CERTIFICATE)
        self.apiWebAcl= self.results.GetDependencyByType(WAF_WACL)

        return AWS.APIGW().Ensure(
            name= self.apiName,
            domainName= self.apiDomainName,
            certificate= self.apiCertificate,
            webAcl= self.apiWebAcl)