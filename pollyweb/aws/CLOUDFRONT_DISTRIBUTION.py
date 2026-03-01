from ACM_CERTIFICATE import ACM_CERTIFICATE
from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS
from WAF_WACL import WAF_WACL   

# Initialize a CloudFront client
import boto3
client = boto3.client('cloudfront')


class CLOUDFRONT_DISTRIBUTION(STRUCT):
    '''👉️ CloudFront distribution wrapper.'''


    def __init__(self, id:str, metadata:any=None) -> None:
        super().__init__({
            'ID': id
        })


    def GetID(self) -> str:
        '''👉️ Get the CloudFront distribution ID.'''
        return self.RequireStr('ID')
    

    def GetMetadata(self) -> STRUCT:
        '''👉️ Get the CloudFront distribution metadata.'''
        distribution = client.get_distribution(
            Id= self.GetID())
        distribution = STRUCT(distribution)
        metadata = distribution.RequireStruct('Distribution')
        return STRUCT(metadata)


    def RequireConfig(self):
        '''👉️ Get the CloudFront distribution configuration.'''
        return self.GetMetadata().RequireStruct('DistributionConfig')
    

    def GetETag(self):
        '''👉️ Get the CloudFront distribution ETag.'''
        return self.GetMetadata().RequireStr('ETag')
        

    def Update(self, config: dict|STRUCT):
        '''👉️ Update the CloudFront distribution configuration.'''
        
        # Update the CloudFront distribution configuration
        return client.update_distribution(
            DistributionConfig= STRUCT(config).Obj(), 
            Id= self.GetID(), 
            IfMatch= self.GetETag())


    def AttachWebAcl(self, webAcl: WAF_WACL):
        '''👉️ Add a Web ACL to the CloudFront distribution.'''

        # Check if the Web ACL is a CloudFront Web ACL
        UTILS.Require(webAcl)
        UTILS.AssertEqual(webAcl.RequireScope(), 'CLOUDFRONT')

        # Get the current configuration
        config = self.RequireConfig()

        # Check if the Web ACL is already attached to the distribution
        if config['WebACLId'] == webAcl.RequireArn():
            return None
        
        # Update the distribution configuration with the Web ACL's ARN
        config['WebACLId'] = webAcl.RequireArn()
        return self.Update(config)


    def AttachCertificate(self, certificate: ACM_CERTIFICATE):
        '''👉️ Add a certificate to the CloudFront distribution.'''

        # Check if the certificate is an ACM certificate
        UTILS.AssertIsType(certificate, ACM_CERTIFICATE, require=True)
        certificate.EnsureGlobal()

        # Get the current configuration
        config = self.RequireConfig()

        # Check if the certificate is already attached to the distribution
        if config['ViewerCertificate']:
            if config['ViewerCertificate']['ACMCertificateArn'] == certificate.RequireArn():
                return None

        # Update the distribution configuration with the certificate
        config['ViewerCertificate'] = {
            'ACMCertificateArn': certificate.RequireArn(),
            'SSLSupportMethod': 'sni-only',  # Use 'sni-only' or 'vip' based on your needs
            'MinimumProtocolVersion': 'TLSv1.2_2021',  # Adjust as necessary
            'Certificate': certificate.RequireArn(),
            'CertificateSource': 'acm'
        }

        # Update the CloudFront distribution to include the certificate
        LOG.Print(f'👉️ Attaching certificate {certificate.RequireArn()} to CloudFront distribution {self.GetID()}')
        return self.Update(config)
        

    def Disable(self):
        '''👉️ Disable the CloudFront distribution.'''
        config = self.RequireConfig()
        config['Enabled'] = False
        return self.Update(config)


    def GetStatus(self):
        '''👉️ Get the CloudFront distribution status.'''
        return self.GetMetadata().RequireStr('Status')
    

    def EnsureDeployed(self):
        '''👉️ Ensure the CloudFront distribution is deployed.'''
        status = self.GetStatus()
        UTILS.AssertEqual(status, 'Deployed', 
            msg= 'The distribution must be deployed before updating.')


    def Delete(self):
        '''👉️ Disable the CloudFront distribution.'''
        
        # Ensure the distribution's status is 'Deployed' before deleting
        self.EnsureDeployed()
        # Delete the CloudFront distribution
        return client.delete_distribution(
            Id= self.GetID(), 
            IfMatch= self.GetETag())


    def GetDomain(self):
        '''👉️ Get the CloudFront distribution domain name.'''
        return self.RequireConfig().RequireStruct('Aliases').ListStr('Items')[0]


    def HasDomainAlias(self, alias: str) -> bool:
        '''👉️ Check if the CloudFront distribution has a domain alias.'''
        return alias in self.RequireConfig().RequireStruct('Aliases').ListStr('Items')


    def AddAlias(self, alias: str):
        '''👉️ Add an alias to the CloudFront distribution.'''

        # Ensure the alias is not already in the list of aliases
        if self.HasDomainAlias(alias):
            return
        
        # Get the current configuration
        config = self.RequireConfig()

        # Add the new alias to the list of aliases. Create the list if it doesn't exist
        if 'Aliases' in config and 'Items' in config['Aliases']:
            config['Aliases']['Items'].append(alias)
            config['Aliases']['Quantity'] += 1
        else:
            config['Aliases'] = {'Quantity': 1, 'Items': [alias]}

        # Update the CloudFront distribution with the new alias
        return self.Update(config)