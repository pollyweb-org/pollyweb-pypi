# 📚 API Gateway

from ACM_CERTIFICATE import ACM_CERTIFICATE
from APIGW_RESTAPI_RESOURCE import APIGW_RESTAPI_RESOURCE
from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from AWS_RETRY import RetryWithBackoff
from PW_UTILS.PRINTABLE import PRINTABLE
from PW_UTILS.STRUCT import STRUCT
from WAF_WACL import WAF_WACL

from APIGW_RESTAPI_STAGE import APIGW_RESTAPI_STAGE
from LOG import LOG
from PW_UTILS.UTILS import UTILS
from AWS import AWS

class APIGW_RESTAPI(AWS_RESOURCE_ITEM, PRINTABLE):
    '''👉️ Represents a REST API in API Gateway.'''
        
    ICON = '🅰️'


    def __init__(self, 
        pool: AWS_RESOURCE_POOL,
        meta:dict,
        client,
        resource=None,
    ) -> None:
        LOG.Print('@')

        meta = STRUCT(meta)
        
        self.ID = meta['id']
        '''👉️ The ID of the API.'''

        self.Name = meta['name']
        '''👉️ The name of the API.'''

        self.Region = AWS.STS().GetRegion()
        '''👉️ The region of the API.'''

        self.Endpoint = f"{self.ID}.execute-api.{self.Region}.amazonaws.com"
        '''👉️ The endpoint of the API.'''

        self.Arn = f"arn:aws:apigateway:{self.Region}::/restapis/{self.ID}"
        '''👉️ The ARN of the API.'''

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool,  
            client= client, 
            resource= resource,
            name= self.Name,
            arn= self.Arn)

        stages:list[APIGW_RESTAPI_STAGE] = []
        
        # Retrieve the stages for each API
        stages_response = client.get_stages(
            restApiId= self.ID)

        # Iterate through the stages to construct and print the endpoint for each stage
        for stage in stages_response['item']:
            
            stageName = stage['stageName']
            webAclArn = stage.get('webAclArn')

            stage = APIGW_RESTAPI_STAGE(
                api= self,
                name= stageName,
                webAclArn= webAclArn,
                client= client)
            
            UTILS.AssertIsType(stage, APIGW_RESTAPI_STAGE)
            stages.append(stage)

        self.Stages = stages

        PRINTABLE.__init__(self, lambda: {
            'ID': self.ID,
            'Name': self.Name,
            'Stages': self.Stages,
            'Endpoint': self.Endpoint,
            'Region': self.Region
        })
  

    def GetStage(self, name:str):
        '''👉️ Get a stage by name.'''
        LOG.Print('@', self)
        
        for stage in self.Stages:
            if stage.Name == name:
                return stage
        
        return None
    

    def RequireStage(self, name:str):
        '''👉️ Get a stage by name or raise an exception.'''
        LOG.Print('@', self)
        
        stage = self.GetStage(name)
        if not stage:
            LOG.RaiseValidationException(
                f'No stage found with name {name}')
        
        return stage


    def _Delete(self):
        LOG.Print('@', self)

        # Delete the custom domain mappings.
        for domain in self.Client.get_domain_names()['items']:

            domain_name = domain['domainName']
            
            base_path_mappings = self.Client.get_base_path_mappings(
                domainName=domain_name)['items']
            
            for mapping in base_path_mappings:
                if mapping['restApiId'] == self.ID:
                    self.Client.delete_base_path_mapping(
                        domainName= domain_name, 
                        basePath= mapping['basePath'])

        # Delete the API
        self.Client.delete_rest_api(
            restApiId= self.ID)
        

    def SetCustomDomain(self, 
        domainName:str,
        certificate: ACM_CERTIFICATE,
    ):
        '''👉️ Set a custom domain for an API.'''
        LOG.Print('@', self)

        # Validate the inputs
        UTILS.AssertIsStr(domainName, require=True)
        UTILS.AssertIsType(certificate, ACM_CERTIFICATE, require=True)
        certificate.EnsureRegional()

        # Prepare the domain name
        domain = AWS.APIGW().DOMAIN(domainName)

        # Check if the domain mapping already exists
        if domain.IsApiMapped(api= self):
            return domain
                
        # Delete if it already exists
        domain.Delete() 

        # Create the domain name
        domain.Create(certificate= certificate)

        # Create the base path mapping
        domain.MapApi(api= self)

        return domain
                

    def AttachWebAcl(self, webAcl:WAF_WACL):
        '''👉️ Attach a Web ACL to an API.'''
        LOG.Print('@', self)
        
        # Validate the inputs
        UTILS.AssertIsType(webAcl, WAF_WACL, require=True)

        # Ensure the Web ACL exists
        if not webAcl.Exists():
            LOG.RaiseException(f'Web ACL {webAcl.RequireName()} does not exist')

        # Ensure it's a regional Web ACL
        if not webAcl.IsRegional():
            LOG.RaiseException(f'Web ACL {webAcl.RequireName()} is not regional')
        
        # Ensure the API has stages
        if len(self.Stages) == 0:
            LOG.RaiseException(f'No stages found for API {self.Name}')

        # Loop through the stages
        for stage in self.Stages:

            # Verify if it's already attached.
            if stage.WebAclArn == webAcl.Arn:
                LOG.Print(f'Web ACL {webAcl.Name} already attached to API {self.Name}')
                return

            # Attach the Web ACL
            webAcl.AssociateResource(arn= stage.Arn)


    def Exists(self) -> bool:
        '''👉️ Check if the API exists.'''

        apis_response = self.Client.get_rest_apis()

        for api in apis_response['items']:
            if api['id'] == self.ID:
                return True
        
        return False
        

    def EnsureDevStage(self, 
        stageName='dev', 
        deploymentID:str = None
    ):
        LOG.Print('@', self)

        # Check if the stage already exists
        if stageName in [ 
            stage.Name 
            for stage in self.Stages 
        ]: return
            
        # Deploy the API to the stage
        if not deploymentID:
            deploymentID = self.Deploy(
                stageName= stageName)

        # Create a new stage using the deployment (if not auto-created)
        try:
            stage = self.Client.create_stage(
                restApiId= self.ID,
                stageName= stageName,
                deploymentId= deploymentID,
                description= 'MyStage')
            assert stage['stageName'] == stageName
            
        except Exception as e:
            # Ignore if the stage already exists
            if not 'Stage already exists' in str(e):
                raise

        # Add the stage to the list
        self.Stages.append(
            APIGW_RESTAPI_STAGE(
                api= self,
                name= stageName,
                client= self.Client))


    @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
    def Deploy(self, stageName:str='dev'):
        '''👉️ Deploy the API to a stage.'''
        LOG.Print('@', self)
        
        # Create a new deployment
        deployment = self.Client.create_deployment(
            restApiId= self.ID,
            stageName= stageName,
            description='MyDeployment')
        
        deploymentID = deployment['id']
        LOG.Print('@: Deployment ID:', deploymentID, self)

        # Create the stage if it doesn't exist
        self.EnsureDevStage(
            stageName= stageName,
            deploymentID= deploymentID)

        return deploymentID
        

    def GetResource(self, path:str):
        '''👉️ Get a resource by path.'''
        LOG.Print('@', self)
        
        # Get the resources for the API
        resources_response = self.Client.get_resources(
            restApiId= self.ID)
        
        # Iterate through the resources to find the one with the matching path
        for resource in resources_response['items']:
            resource = STRUCT(resource)
            if resource['path'] == path:

                return APIGW_RESTAPI_RESOURCE(
                    resourceID= resource.RequireStr('id'),
                    api= self,
                    path= resource.RequireStr('path'),
                    client= self.Client,
                    # root resource has no parent
                    parentID= resource.GetStr('parentId'))
        
        return None


    def AddResource(self, 
        path:str, 
        parentID:str = None
    ):
        '''👉️ Add a resource by path.'''
        LOG.Print('@', self)
        
        # Check if the resource already exists
        resource = self.GetResource(path)
        if resource:
            return resource
        
        # Get the root resource
        if not parentID:
            parentID= self.GetRootResource().ID
            UTILS.AssertIsStr(parentID, require=True)

        UTILS.AssertIsStr(path, require=True)
        UTILS.AssertIsStr(parentID, require=True)
        UTILS.AssertIsStr(self.ID, require=True)

        # Create the resource
        resource = self.Client.create_resource(
            restApiId= self.ID,
            parentId= parentID,
            pathPart= path)
                
        # Return the resource
        resource = APIGW_RESTAPI_RESOURCE(
            resourceID= resource['id'],
            api= self,
            parentID= self.ID,
            path= path,
            client= self.Client)
        
        # Deploy the API again
        self.Deploy()

        return resource



    def GetRootResource(self):
        LOG.Print('@', self)
        return self.GetResource(path= '/')        
    

    def MockMethod(self):
        '''👉️ Mock a method to create a stage.'''

        LOG.Print('@', self)
        
        # Get the root resource
        rootResource = self.GetRootResource()
        
        # Create a new method
        method = rootResource.AddMethod(httpMethod= 'GET')

        # Integrate the method with a mock response
        method.IntegrateMock()

        # Deploy the API
        self.Deploy()


    
    def GetDomainName(self):
        '''👉️ Returns the domain name for the API.'''
        LOG.Print('@')
        
        # List all custom domain names
        response = self.Client.get_domain_names()
        domain_names = response['items']
        
        for domain in domain_names:
            domain_name = domain['domainName']
        
            # List all base path mappings for the domain
            base_path_response = self.Client.get_base_path_mappings(
                domainName=domain_name)
            base_path_mappings = base_path_response['items']
            
            for mapping in base_path_mappings:
                mapping = STRUCT(mapping)
                if mapping['restApiId'] == self.ID:
                    return domain_name