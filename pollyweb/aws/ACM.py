import boto3
from ACM_CERTIFICATE import ACM_CERTIFICATE
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from LOG import LOG
from PW_UTILS.UTILS import UTILS

regionalClient = boto3.client('acm')        
# CloudFront requires certificates in us-east-1
cloudFrontClient = boto3.client('acm', region_name='us-east-1')
            
class ACM(AWS_RESOURCE_POOL[ACM_CERTIFICATE]):
    '''👉️ Amazon Certificate Manager: Manages ACM certificates.'''

    ICON = '🔐'


    @classmethod
    def Ensure(cls, 
        name:str,
        central:bool
    ):
        client = cls.GetClient(
            central= central)
        
        return super()._Ensure(
            name= name,
            client= client)
    

    @classmethod
    def GetClient(cls, central:bool|None):
        UTILS.AssertIsType(central, bool, require=True)
        
        if central == True:
            return cloudFrontClient
        
        if central == False:
            return regionalClient
        
        raise Exception('central must be True or False')
        

    @classmethod
    def List(cls, 
        client
    ) -> list[ACM_CERTIFICATE]:
        '''👉 Lists the certificates'''

        LOG.Print('@')

        UTILS.Require(client)
                
        paginator = client.get_paginator('list_certificates')

        ret = []
        for page in paginator.paginate():
            for summary in page['CertificateSummaryList']:
                
                item = ACM_CERTIFICATE(
                    pool= cls,
                    client= client,   
                    meta= summary)
                
                ret.append(item)
            
        return ret
    

    @classmethod
    def Create(cls, 
        name:str,
        client,
    ) -> ACM_CERTIFICATE:
        '''👉 Creates a certificate for the domain.'''
        LOG.Print('@')
         
        # Request the certificate.
        response = client.request_certificate(
            DomainName= name,
            ValidationMethod= 'DNS') # or 'EMAIL')
        
        # Map the domain name to the response.
        response['DomainName'] = name
        
        return ACM_CERTIFICATE(
            client= client,
            pool= cls,
            meta= response)