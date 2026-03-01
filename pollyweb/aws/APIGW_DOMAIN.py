# 📚 API Gateway

from ACM_CERTIFICATE import ACM_CERTIFICATE
from APIGW_RESTAPI import APIGW_RESTAPI
from AWS_RETRY import RetryWithBackoff
from PW_UTILS.UTILS import UTILS

import boto3
client = boto3.client('apigateway')


class APIGW_DOMAIN:
        
    ICON = '🅰️'


    def __init__(self, name:str) -> None:
        UTILS.AssertIsStr(name, require=True)
        self.Name = name
   

    def __enter__(self):
        pass


    def __exit__(self, exc_type, exc_val, exc_tb):
        self.Delete(safe= True)


    @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
    def Delete(self, 
        safe: bool= True
    ):
        '''👉️ Delete a domain name, if it exists'''
        try:
            client.delete_domain_name(
                domainName= self.Name)
        except Exception as e:
            if not safe or 'NotFoundException' not in str(e):
                raise
    

    def Create(self,
        certificate: ACM_CERTIFICATE,
        type: str= 'REGIONAL'
    ):
        '''👉️ Create a domain name'''

        UTILS.AssertIsType(certificate, ACM_CERTIFICATE, require=True)

        # Wait for the certificate to be issued, if just created.
        certificate.WaitUntilIssued()

        # Create the domain name.
        client.create_domain_name(
            domainName= self.Name,
            regionalCertificateArn= certificate.Arn,
            endpointConfiguration={
                'types': [type]  # REGIONAL, EDGE, PRIVATE
            })
        
    
    def MapApi(self,
        api: APIGW_RESTAPI
    ):
        '''👉️ Map an API to a domain name'''

        UTILS.AssertIsType(api, APIGW_RESTAPI, require=True)

        client.create_base_path_mapping(
            domainName= self.Name,
            restApiId= api.ID,
            basePath= 'basePath')
        

    def IsApiMapped(self,
        api: APIGW_RESTAPI
    ) -> bool:
        '''👉️ Check if an API is mapped to a domain name'''

        # List all base path mappings for the domain
        try:    
            base_path_response = client.get_base_path_mappings(
                domainName= self.Name)
        except Exception as e:
            if 'NotFoundException' in str(e):
                return False
            raise
            
        for mapping in base_path_response['items']:
            if mapping['restApiId'] == api.ID:
                return True
            
        return False
            