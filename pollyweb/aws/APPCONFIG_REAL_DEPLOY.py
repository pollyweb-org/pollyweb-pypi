from APPCONFIG_APP import APPCONFIG_APP
from APPCONFIG_APP_STRATEGY import APPCONFIG_APP_STRATEGY

import boto3

from LAMBDA_FUNCTION import LAMBDA_FUNCTION
from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from PW_UTILS.LOG import LOG
from PW_UTILS.UTILS import UTILS
client = boto3.client('appconfig')

class APPCONFIG_REAL_DEPLOY:
    '''👉 AppConfig deployment'''


    ICON = '⛅'


    @classmethod
    def CreateApp(cls, 
        name,
        description= '',
        validators: list[LAMBDA_FUNCTION_REAL] = []
    ):
        '''👉️ Creates an AppConfig app.
         * `name`: name for the app
         * `description`: optional description
         * `validators`: list of Lambda ARNs
        '''
        
        LOG.Print(f'@: {name=}')

        # Validate the validators arg.
        UTILS.AssertIsList(
            validators, 
            itemType= LAMBDA_FUNCTION_REAL)
        
        # Get the AppConfig app.
        app = cls.GetApp(name= name)

        # Create the app if it doesn't exist.
        if not app:
            
            response = client.create_application(
                Name= name,
                Description= description)
            
            app = APPCONFIG_APP(
                meta= response,
                client= client)
    
        # Create a default environment.
        app.CreateDefaultEnv()
        
        # Create a default configuration.
        app.CreateDefaultConfig(
            validators= validators)
        
        return app
    
    

    def ListDeployStrategies(cls):
        LOG.Print(f'@')

        # List all deployment strategies
        response = client.list_deployment_strategies()
        
        strategies: list[APPCONFIG_APP_STRATEGY] = []
        for item in response['Items']:

            strategy = APPCONFIG_APP_STRATEGY(
                meta= item,
                client= client)
            
            strategies.append(strategy)

        return strategies


    def EnsureAllAtOnceDeployment(cls):
        LOG.Print(cls.EnsureAllAtOnceDeployment)
        
        # Check if exists
        for strategy in cls.ListDeployStrategies():
            if strategy.Name == 'AllAtOnceDeployment':
                return strategy
            
        # Create if it doesn't exist.
        response = client.create_deployment_strategy(
            Name='AllAtOnceDeployment',
            DeploymentDurationInMinutes= 0,  # Deploy all at once
            GrowthFactor= 100.0,             # 100% of the targets
            FinalBakeTimeInMinutes= 0,       # No bake time needed
            ReplicateTo= 'NONE',             # No replication to additional targets
        )

        return APPCONFIG_APP_STRATEGY(
            meta= response,
            client= client)
        

    
    @classmethod
    def ListApps(cls):
        LOG.Print(cls.ListApps)

        items = []
        next_token = None

        while True:
            if next_token:
                response = client.list_applications(
                    NextToken=next_token)
            else:
                response = client.list_applications()
            
            items.extend(response['Items'])
            
            next_token = response.get('NextToken')
            if not next_token:
                break

        apps: list[APPCONFIG_APP] = []
        for item in items:
            app= APPCONFIG_APP(
                meta= item, 
                client= client)
            apps.append(app)

        return apps
            

    @classmethod
    def GetApp(cls, 
        name: str 
    ):
        '''👉️ Gets an app by name.
         * if not found, returns None.
        '''

        LOG.Print(f'@: {name=}')

        for app in cls.ListApps():
            if app.Name == name:
                return app
        return None

