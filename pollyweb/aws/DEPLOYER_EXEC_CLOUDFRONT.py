from aws.ACM_CERTIFICATE import ACM_CERTIFICATE
from aws.APIGW_RESTAPI import APIGW_RESTAPI
from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from aws.WAF_WACL import WAF_WACL

class DEPLOYER_EXEC_CLOUDFRONT(DEPLOYER_EXEC_TASK):


    def OnValidate(self):

        self.VerifyAlienParameters([])


    def OnExecute(self):

        self.cfDomainName= self.results.GetDependency('DomainName', str)
        self.cfRestApi= self.results.RequireDependencyByType(APIGW_RESTAPI)
        self.cfWebAcl= self.results.GetDependencyByType(WAF_WACL)
        self.cfCertificate= self.results.GetDependencyByType(ACM_CERTIFICATE)

        ret = AWS.CLOUDFRONT().EnsureDomainDistribution(
            domainName= self.cfDomainName,
            restApi= self.cfRestApi,
            webAcl= self.cfWebAcl,
            certificate= self.cfCertificate)

        return ret
