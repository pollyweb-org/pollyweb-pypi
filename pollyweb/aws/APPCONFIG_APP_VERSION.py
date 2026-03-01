

from AWS import AWS
from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS


class APPCONFIG_APP_VERSION:
    '''👉️ AppConfig Hosted Configuration Version.'''

    ICON = '📋'

    def __init__(self,
        meta:dict, 
        client,
        config          
    ) -> None:
        
        from APPCONFIG_APP_CONFIG import APPCONFIG_APP_CONFIG
        UTILS.AssertIsType(config, APPCONFIG_APP_CONFIG)

        self.Config:APPCONFIG_APP_CONFIG = config
        self.App = self.Config.App

        struct = STRUCT(meta)
        self.Number = struct.RequireInt('VersionNumber')
        self.Client = client
        self.FullName = f'{self.App.Name}/{self.Config.Name}/{self.Number}'


    def Delete(self):
        LOG.Print(f'@: {self.FullName}')

        self.Client.delete_hosted_configuration_version(
            ApplicationId= self.App.ID,
            ConfigurationProfileId= self.Config.ID,
            VersionNumber= self.Number)


    def Deploy(self,
        title: str = '',
        env = None
    ):
        '''👉️ Deploy the configuration version to an environment.

        Params:
            `title`:  optional description of the deployment.
            `env`: optional environment to deploy to.

        Behavior:
            - if no environment is provided, the app's default is used.
            - waits for the deployment to finish.
            - raises an exception if the deployment fails.
            - returns the deployment object.
        '''
        
        LOG.Print(f'@: {self.FullName}')

        # Validate the environment argument.
        from APPCONFIG_APP_ENV import APPCONFIG_APP_ENV
        UTILS.AssertIsType(env, APPCONFIG_APP_ENV)

        # If an environment is not privided, use the default.
        if not env:
            env = self.App.GetDefaultEnv()

        # Get or create the EnsureAllAtOnceDeployment strategy.
        from APPCONFIG_REAL_DEPLOY import APPCONFIG_REAL_DEPLOY
        strategy = APPCONFIG_REAL_DEPLOY().EnsureAllAtOnceDeployment()

        # Then, start the deployment.
        response = self.Client.start_deployment(
            ApplicationId= self.App.ID,
            EnvironmentId= env.ID,
            ConfigurationProfileId= self.Config.ID,
            ConfigurationVersion= str(self.Number),
            DeploymentStrategyId= strategy.ID,  
            Description= title)
        
        # Wrap the async request in a deployment object.
        from APPCONFIG_APP_DEPLOY import APPCONFIG_APP_DEPLOY
        deploy = APPCONFIG_APP_DEPLOY(
            meta= response,
            client= self.Client,
            env= env,
            version= self)
        
        # Wait for the deployment request to finish.
        deploy.WaitToFinish()

        return deploy