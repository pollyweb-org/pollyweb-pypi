
from pollyweb.utils.FILE import FILE
from IAM_SERVICE_CREDENTIAL import IAM_SERVICE_CREDENTIAL
from IAM_POLICY import IAM_POLICY
from IAM_ROLE import IAM_ROLE
from IAM_USER import IAM_USER
from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT

# Initialize IAM client
import boto3

from pollyweb.utils.UTILS import UTILS
iam_client = boto3.client('iam')


class IAM:
    '''👉️ Helper class for IAM operations.'''

    ICON = '🔒'


    def __init__(self, cached:bool= False) -> None:
        '''👉️ Initialize the class.'''
        self._cached = cached
        if cached: self._cache = UTILS.CACHE()


    @classmethod
    def POLICY(self, 
        name:str, 
        cached:bool= False
    ) -> IAM_POLICY:
        '''👉️ Returns the IAM policy.'''

        return IAM_POLICY(
            name= name, 
            cached= cached)


    @classmethod
    def ROLE(cls, 
        name:str, 
        cached:bool= False
    ) -> IAM_ROLE:
        '''👉️ Returns the IAM role.'''

        return IAM_ROLE(
            name= name, 
            cached= cached) 


    def EnsureLambdaRole(self, 
        name:str
    ) -> IAM_ROLE:
        '''👉️ Ensures that the IAM role for Lambda exists.'''
        
        role = IAM_ROLE(
            name= name, 
            cached= self._cached)
        
        # Check if the role exists
        arn = role.GetArn()
        if arn: return role
        
        # Create the role
        role.EnsureForLambda()
        return role
    

    def EnsureServiceRole(self, 
        service:str, # The name of the service, e.g. codepipeline
        policies:list[str]= None
    ) -> IAM_ROLE:
        '''👉️ Ensures that the IAM role for the service exists.
        
        Arguments:
            * `service`: str: The name of the service, e.g. codepipeline
            * `policies`: list[str]: The list of policies to attach to the role.
        '''
        LOG.Print(f'@: Service={service}')
        
        name = UTILS.ToProperCase(service)
        name = f'{name}ServiceRole'
        role = IAM_ROLE(name)
        
        # Check if the role exists
        if not role.Exists():
            role.CreateForService(service)        
        role.AssertAssumesServiceRole(service)
        if policies:
            role.AttachPolicies(policies)
        return role
        

    def GetUser(self):
        ''' 👉️ Returns the logged user.'''
        result = iam_client.get_user()
        user = STRUCT(result).RequireStruct('User')
        return IAM_USER(user)
    

    @classmethod
    def UploadPublicKey(self, 
        file:FILE, 
        userName:str= None
    ):
        LOG.Print('@', file, dict(userName=userName))
        
        # Read your public key
        file.AssertExists()
        if not file.GetName().endswith('.pub'):
            LOG.RaiseException(f'The file name should end with .pub', file)
        public_key = file.ReadText()

        # Get the user name.
        if not userName:
            userName = self.GetUser().RequireUserName()

        # Upload the public key to an IAM user
        try:
            response = iam_client.upload_ssh_public_key(
                UserName= userName,
                SSHPublicKeyBody= public_key)
            
        except Exception as e:
            # If the key already exists, ignore the error
            if 'DuplicateSSHPublicKey' in str(e):
                return
            # Otherwise, raise the error
            raise e
            
        # Assert the call was successful
        response = STRUCT(response)
        response.RequireStruct('SSHPublicKey').RequireStr('SSHPublicKeyId')


    def CreateServiceCredentials(self, 
        serviceName:str, 
        userName:str=None
    ) -> IAM_SERVICE_CREDENTIAL:
        '''👉️ Creates service-specific credentials for the user.'''

        if not userName:
            userName = self.GetUser().RequireUserName()

        response = iam_client.create_service_specific_credential(
            UserName= userName,
            ServiceName= serviceName)
        STRUCT(response).RequireAtt('ServiceSpecificCredential')
        return IAM_SERVICE_CREDENTIAL(
            response['ServiceSpecificCredential'], 
            iam_client)
               

    def GetServiceCredentials(self, 
        serviceName:str, 
        userName:str=None
    ) -> IAM_SERVICE_CREDENTIAL:
        '''👉️ Returns the service-specific credentials for the user.'''
        
        if not userName:
            userName = self.GetUser().RequireUserName()

        # Get service-specific credentials
        response = iam_client.list_service_specific_credentials(
            UserName= userName)
        credentials = STRUCT(response).RequireList('ServiceSpecificCredentials')
        
        # Find the credentials
        for credential in credentials:
            if credential['ServiceName'] == serviceName:
                return IAM_SERVICE_CREDENTIAL(credential, iam_client)
        
        return None
    

    def EnsureServiceCredentials(self, 
        serviceName:str, 
        userName:str=None
    ) -> IAM_SERVICE_CREDENTIAL:
        '''👉️ Ensures that the service-specific credentials exist.'''
        
        credentials = self.GetServiceCredentials(
            serviceName= serviceName, 
            userName= userName)
        if credentials: 
            #return credentials
            credentials.Delete()
        
        return self.CreateServiceCredentials(
            serviceName= serviceName, 
            userName= userName)