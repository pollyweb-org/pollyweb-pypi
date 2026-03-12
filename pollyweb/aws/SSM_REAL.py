# 📚 SSM

from botocore.exceptions import ClientError
from LOG import LOG
from AWS import AWS


import boto3
ssm = boto3.client('ssm')


from SSM_BASE import SSM_BASE
class SSM_REAL(SSM_BASE):

    
    @classmethod
    def Get(cls, 
        name: str, 
        optional:bool= False, 
        region:str= None
    ) -> str:
        '''👉 Gets the value of the parameter.
         * if not registered, raises an exception.
         * if optional is True, returns None if not found.
        '''

        if not name.startswith('/'):
            LOG.RaiseException(
                'Parameter name must start with a forward slash.', 
                f'{name=}')    

        # If a region is specified, create a new client
        if region:
            ssm2 = boto3.client('ssm', 
                region_name= region)
        else:
            ssm2 = ssm

        try:
            # Attempt to get the parameter
            value = ssm2.get_parameter(Name= name)

            # If successful, return the parameter's value
            return value['Parameter']['Value']
        
        except ssm.exceptions.ParameterNotFound as e:
        
            # If the parameter is not found, return None
            if not optional:
                LOG.RaiseException('Parameter not found in region.', 
                    f'{name=}', f'{region=}', f'{AWS.STS().GetAccountAlias()}')
            
            # If some other error occurred, raise the exception
            return None

    
    @classmethod
    def Set(cls, 
        name: str,
        value: str, 
        region:str= None
    ):
        '''👉 Sets the parameter.'''

        # If a region is specified, create a new client
        if region:
            ssm2 = boto3.client('ssm', 
                region_name= region)
        else:
            ssm2 = ssm

        # Set the parameter
        ssm2.put_parameter(
            Name= name, 
            Value= value, 
            Type= "String", 
            Overwrite= True)


    def Delete(self, 
        name: str, 
        region:str= None,
        optional:bool= False
    ):
        '''👉 Deletes the parameter.'''

        # If a region is specified, create a new client
        if region:
            ssm2 = boto3.client('ssm', 
                region_name= region)
        else:
            ssm2 = ssm

        try:
            # Attempt to delete the parameter
            ssm2.delete_parameter(Name=name)    

        except ClientError as e:
            if e.response['Error']['Code'] == 'ParameterNotFound':
                # If the safe flag is set, return if the parameter is not found
                if optional: return
                # Otherwise, raise the error
                LOG.RaiseException('Parameter not found.', f'{name=}')
            raise e
        

    @classmethod
    def EnsureParameter(cls, name:str, value:str=None) -> str:
        '''👉️ Ensures a parameter exists.'''

        # Get the parameter
        existing = cls.Get(name= name, optional= True)
        
        # If the parameter exists, update and return.
        if existing is not None:
            if value is not None:
                if existing != value:
                    cls.Set(name= name, value= value)
            return value

        # Ensure the value is specified when creating a parameter.
        if value is None:
            LOG.RaiseException('Value must be specified when creating a parameter.')
    
        # If the parameter does not exist, create it.
        cls.Set(name= name, value= value)

        return value