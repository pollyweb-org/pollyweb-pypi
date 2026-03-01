from APPCONFIG_APP_ENV import APPCONFIG_APP_ENV
from LAMBDA_FUNCTION import LAMBDA_FUNCTION
from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS


import boto3
lambda_client = boto3.client('lambda')

class APPCONFIG_APP:
    '''👉️ AppConfig Application.'''
    

    ICON = '📋'
    

    @property 
    def DEFAULT_ENV(self):
        #return f'{self.Name}-Env'
        return 'default'
    
    
    @property
    def DEFAULT_CONFIG(self):
        #return f'{self.Name}-Config'
        return 'default'


    def __init__(self,
        meta: dict,
        client            
    ) -> None:
        
        struct = STRUCT(meta)
        self.Client = client
        self.ID = struct.RequireStr('Id')
        self.Name = struct.RequireStr('Name')
        self.FullName = self.Name

    
    def CreateDefaultConfig(self,
        validators: list[LAMBDA_FUNCTION_REAL] = []
    ):
        '''👉️ Creates a default configuration.
         * `validators`: list of Lambda ARNs
        '''

        LOG.Print(f'@: {self.FullName}')

        UTILS.AssertIsList(validators, 
            itemType=LAMBDA_FUNCTION_REAL)

        if self.GetDefaultConfig():
            LOG.Print('@: Already exists, ignoring.')
            return

        return self.CreateConfig(
            name= self.DEFAULT_CONFIG,
            validators= validators)


    def CreateConfig(self, 
        name: str,
        description: str = '',
        validators: list[LAMBDA_FUNCTION_REAL] = []
    ):
        '''👉️ Creates a configuration.
         * `validators`: list of Lambda ARNs
        '''

        LOG.Print(f'@: {self.FullName}')

        UTILS.AssertIsStr(name, require= True)
        UTILS.AssertIsList(validators, itemType=LAMBDA_FUNCTION_REAL)

        # Trigger validators.
        validatorList = [] 
        for fn in validators:

            # Format the validator.
            validatorList.append({
                'Type': 'LAMBDA',
                'Content': fn.GetArn()
            })

            # Allow the validator to be executed.
            fn.GrantInvoke(
                title= 'AllowInvokeFromAppConfig',
                principal= 'appconfig.amazonaws.com')

        LOG.Print(f'@: validatorList', validatorList)

        # Create the configuration.
        response = self.Client.create_configuration_profile(
            ApplicationId= self.ID,
            Name= name,
            LocationUri= 'hosted',
            Type= 'AWS.Freeform',  
            # Type indicating that it's freeform text (JSON, YAML, text)
            Description= description,
            Validators= validatorList)
        
        # Wrap the response.
        from APPCONFIG_APP_CONFIG import APPCONFIG_APP_CONFIG
        return APPCONFIG_APP_CONFIG(
            meta= response,
            client= self.Client,
            app= self)
    

    def ListConfigs(self):
        LOG.Print(f'@: {self.FullName}')

        response = self.Client.list_configuration_profiles(
            ApplicationId= self.ID)

        from APPCONFIG_APP_CONFIG import APPCONFIG_APP_CONFIG
        ret:list[APPCONFIG_APP_CONFIG] = []
        
        for item in response['Items']:
            ret.append(
                APPCONFIG_APP_CONFIG(
                    app= self,
                    client= self.Client,
                    meta= item))
            
        return ret
    

    def GetConfig(self, 
        name:str
    ):
        LOG.Print(f'@: {self.FullName}')

        for config in self.ListConfigs():
            if config.Name == name:
                return config
        
        return None


    def CreateDefaultEnv(self):
        LOG.Print(f'@: {self.FullName}')

        env = self.GetEnv(name= self.DEFAULT_ENV)
        
        if not env: 
            env = self.CreateEnv(
                name= self.DEFAULT_ENV)
            
        return env


    def CreateEnv(self,
        name: str,
        description: str = ''
    ):
        LOG.Print(f'@: {self.FullName}')

        app = self
    
        response = self.Client.create_environment(
            ApplicationId= app.ID,
            Name= name,
            Description= description)
        
        return APPCONFIG_APP_ENV(
            meta= response, 
            client= app.Client,
            app= app)
    

    def ListEnvs(self): 
        LOG.Print(f'@: {self.FullName}')
    
        response = self.Client.list_environments(
            ApplicationId= self.ID)
        response = STRUCT(response)

        ret:list[APPCONFIG_APP_ENV] = []
        for env in response['Items']:
            ret.append(
                APPCONFIG_APP_ENV(
                    meta= env,
                    app= self,
                    client= self.Client))
        
        return ret
    

    def GetEnv(self, 
        name: str
    ):
        LOG.Print(f'@: {self.FullName}')

        for env in self.ListEnvs():
            if env.Name == name:
                return env
        
        return None
    

    def EnsureEnv(self, 
        name: str              
    ):
        LOG.Print(f'@: {self.FullName}')

        env = self.GetEnv(name= name)
        
        if env == None:
            env = self.CreateEnv(mame= name)

        return env
    

    def DeleteEnvs(self):
        LOG.Print(f'@: {self.FullName}')

        for env in self.ListEnvs():
            env.Delete()


    def DeleteConfigs(self):
        LOG.Print(f'@: {self.FullName}')

        for config in self.ListConfigs():
            config.Delete()


    def Delete(self):
        LOG.Print(f'@: {self.FullName}')

        self.DeleteConfigs()
        
        self.DeleteEnvs()

        self.Client.delete_application(
            ApplicationId= self.ID)
        

    def GetDefaultEnv(self):
        LOG.Print(f'@: {self.FullName}')

        env = self.GetEnv(self.DEFAULT_ENV)
        if not env:
            env = self.CreateDefaultEnv()
        return env
    

    def GetDefaultConfig(self):
        LOG.Print(f'@: {self.FullName}')
        
        env = self.GetConfig(self.DEFAULT_CONFIG)
        if not env:
            env = self.CreateDefaultConfig()
        return env
    

    def SetValue(self,
        content: str,
        format: str = 'TXT'
    ): 
        '''👉️ Sets the value of the AppConfig.
            * `content`: the string content
            * `format`: one of [TXT, JSON, YAML]
        '''

        LOG.Print(f'@: {self.FullName}', f'{type=}')
        
        config = self.GetDefaultConfig()
        version = config.CreateVersion(
            content= content,
            format= format)
        
        return version.Deploy()