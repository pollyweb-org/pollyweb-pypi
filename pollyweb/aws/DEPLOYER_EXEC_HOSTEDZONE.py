from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.AWS import AWS
from LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS

class DEPLOYER_EXEC_HOSTEDZONE(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):
        pass


    def OnExecute(self):
        
        for map in self.GetDependencyMap():

            if map.Type == 'Parameter':
                dep = self.RequireDependency(map.FullName)
                self.DomainName = dep.RequireResultStruct().RequireStr('Value')

            if map.Type == 'DnsSecKey':
                dep = self.RequireDependency(map.FullName)
                self.DnsSecKey = dep.RequireResultStruct().RequireStr('Arn')

        # Verify the required domain nname.
        if UTILS.IsNoneOrEmpty(self.DomainName):
            LOG.RaiseException('DomainName is required.')

        # Create the hosted zone.
        zone = AWS.ROUTE53().CreateHostedZone(
            domainName= self.DomainName)

        # Create the DNSSEC key.
        if not UTILS.IsNoneOrEmpty(self.DnsSecKey):
            zone.SetUpDnsSec(
                #name= self.DomainName,
                keyArn= self.DnsSecKey)