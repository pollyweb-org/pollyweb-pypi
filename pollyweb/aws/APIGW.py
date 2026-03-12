# 📚 API Gateway

from ACM_CERTIFICATE import ACM_CERTIFICATE
from APIGW_RESTAPI import APIGW_RESTAPI
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from LOG import LOG
import os

import boto3

from PW_UTILS.UTILS import UTILS
from WAF_WACL import WAF_WACL
apigw_management = boto3.client('apigatewaymanagementapi')
client = boto3.client('apigateway')


class APIGW(AWS_RESOURCE_POOL[APIGW_RESTAPI]):

    ICON = '🅰️'
        

    @classmethod
    def DOMAIN(cls, name:str):
        from APIGW_DOMAIN import APIGW_DOMAIN
        return APIGW_DOMAIN(name)


    @classmethod
    def SendToSocket(cls, 
        socketID: str, 
        data: dict
    ):
        LOG.Print('@')
        
        #endpointUrl=f'{domain_name}/{stage}'
        endpointUrl = os.environ['ENDPOINT_URL']

        try:
            apigw_management.post_to_connection(
                ConnectionId= socketID,
                Data= data,
                EndpointUrl= endpointUrl)
            return True
        
        except apigw_management.exceptions.GoneException:
            LOG.Print(f'Found stale connection, delete {socketID}')
            return False
        
        except Exception as e:
            LOG.RaiseException('Error posting to connection')



    @classmethod
    def List(cls):
        '''👉️ List all APIs.'''

        LOG.Print('@')
        
        # Call the get_rest_apis method to retrieve the APIs
        apis_response = client.get_rest_apis()

        # Iterate through the APIs and print their names, IDs, and endpoints
        ret: list[APIGW_RESTAPI] = []
        for api in apis_response['items']:

            # Create the API name, ID, and endpoint
            item = APIGW_RESTAPI(
                pool= cls,
                meta= api,
                client= client)
            
            # Append the API to the list
            ret.append(item)

        # Return the list of APIs
        return ret
    

    def RequireByDomain(self, domain:str) -> APIGW_RESTAPI:
        '''👉️ Get an API by domain or raise an exception.'''
        api = self.GetByDomain(domain)
        if not api:
            LOG.RaiseException(f'No API found with domain {domain}')
        return api
    



    @classmethod
    def Ensure(cls, 
        name:str
    ):
        return super()._Ensure(
            name= name)        
    
    
    @classmethod
    def Create(cls, name:str):
        '''👉 Creates a new APIGP.'''
        LOG.Print(f'@ Creating APIGW {name=}')

        # Create the API
        api_response = client.create_rest_api(
            name= name,
            endpointConfiguration={
                'types': ['REGIONAL']  # or 'EDGE' or 'PRIVATE'
            })
    
        # Create the API object
        api = APIGW_RESTAPI(
            pool= cls,
            meta= api_response,
            client= client)
        
        # Wait for the API to be listed.
        api.AssertExists()

        return api


    @classmethod
    def GetByID(cls, id:str) -> APIGW_RESTAPI:
        '''👉 Gets an API by ID.'''
        LOG.Print('@', cls)
        
        for res in cls._List():
            if res.ID == id:
                return res
                    
        return None
    

    @classmethod
    def RequireByID(cls, id:str) -> APIGW_RESTAPI:
        '''👉 Gets an API by ID or raises an exception.'''
        res = cls.GetByID(id)
        if not res:
            LOG.RaiseValidationException(
                f'No API found with ID {id}')
        return res
    

    @classmethod
    def GetByDomain(cls, domain:str) -> APIGW_RESTAPI:
        '''👉️ Get an API by domain.'''
        LOG.Print('@', cls)
        
        # List all base path mappings for the domain
        try:    
            base_path_response = client.get_base_path_mappings(
                domainName= domain)
        except Exception as e:
            if 'NotFoundException' in str(e):
                return None
            raise
            
        for mapping in base_path_response['items']:
            return cls.GetByID(mapping['restApiId'])
            
        return None