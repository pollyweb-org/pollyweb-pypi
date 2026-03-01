from APIGW_RESTAPI import APIGW_RESTAPI
from WAF_WACL import WAF_WACL   
from ACM_CERTIFICATE import ACM_CERTIFICATE
from CLOUDFRONT_DISTRIBUTION import CLOUDFRONT_DISTRIBUTION
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS


# Initialize a CloudFront client
import boto3
client = boto3.client('cloudfront')


class CLOUDFRONT:


    @classmethod
    def CreateApiDistribution(cls, 
        rest_api: APIGW_RESTAPI, 
    ):
        
        # Configuration for the API origin.
        origin = {
            'Id': 'APIGatewayEndpoint',
            'DomainName': rest_api.GetDomainName(),
            'OriginPath': rest_api.Stages[0].RequireName(),
            'CustomHeaders': {
                'Quantity': 0,
                'Items': []
            },
            'OriginPath': '',
            'CustomOriginConfig': {
                'HTTPPort': 80,
                'HTTPSPort': 443,
                'OriginProtocolPolicy': 'https-only',
                'OriginSslProtocols': {
                    'Quantity': 3,
                    'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2']
                },
                'OriginReadTimeout': 30,
                'OriginKeepaliveTimeout': 5
            }
        }

        defaultCacheBehavior = {
            'TargetOriginId': 'APIGatewayEndpoint',
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'TrustedKeyGroups': {
                'Enabled': False,
                'Quantity': 0
            },
            'ForwardedValues': {
                'QueryString': True,
                'Cookies': {'Forward': 'none'},
                'Headers': {
                    'Quantity': 0
                },
                'QueryStringCacheKeys': {
                    'Quantity': 0
                }
            },
            'MinTTL': 0,
            'DefaultTTL': 86400,  # 1 day
            'MaxTTL': 31536000,  # 1 year
        }
        
        # Configuration for the logging.
        logging = {
            'Enabled': False,
            'IncludeCookies': False,
            'Bucket': '',
            'Prefix': ''
        }

        distributionConfig={
            'CallerReference': UTILS().UUID(),  # Unique reference for the request
            'DefaultRootObject': '',
            'Origins': {
                'Quantity': 1,
                'Items': [ origin ]
            },
            'DefaultCacheBehavior': defaultCacheBehavior,
            'Comment': 'CloudFront distribution for API Gateway',
            'Logging': logging,
            'Enabled': True
        }
                
        # Create CloudFront distribution
        response = client.create_distribution(
            DistributionConfig= distributionConfig)

        return CLOUDFRONT_DISTRIBUTION(
            id= STRUCT(response['Distribution']).RequireStr('Id'))


    @classmethod
    def GetDistributionByDomainName(cls, domain_name: str) -> CLOUDFRONT_DISTRIBUTION:
        '''👉️ Get the CloudFront distribution.'''
        response = client.list_distributions()
        for distribution in response['DistributionList']['Items']:
            if domain_name in distribution['Aliases']['Items']:
                ret = CLOUDFRONT_DISTRIBUTION(
                    id = distribution['Id'])
                return ret
        return None
    

    @classmethod
    def GetDistributionByID(cls, id: str) -> CLOUDFRONT_DISTRIBUTION:
        '''👉️ Get the CloudFront distribution.'''
        response = client.get_distribution(Id= id)
        # Check if the distribution exists.
        STRUCT(response).RequireStruct('Distribution')
        # Return the distribution wrapper.
        ret = CLOUDFRONT_DISTRIBUTION(id = id)  
        return ret


    @classmethod
    def EnsureDomainDistribution(cls, 
        restApi: APIGW_RESTAPI,
        domainName: str = None, 
        webAcl: WAF_WACL = None,
        certificate: ACM_CERTIFICATE = None
    ) -> CLOUDFRONT_DISTRIBUTION:
        '''👉️ Ensure the domain distribution.'''

        # Validate the input.
        UTILS.AssertIsStr(domainName, require= True)
        UTILS.AssertIsType(restApi, APIGW_RESTAPI, require= True)

        # Get the distribution by domain name.
        distribution = cls.GetDistributionByDomainName(domainName)
        
        # Create the distribution if it does not exist.
        if not distribution:
            distribution = cls.CreateApiDistribution(restApi)
        
        # Attach the Web ACL to the distribution.
        if webAcl:
            distribution.AttachWebAcl(webAcl)

        # Attach the certificate to the distribution.
        if certificate or domainName:
            UTILS.RequireArgs([certificate, domainName])
            distribution.AttachCertificate(certificate)

        # Return the distribution created or updated.
        return distribution