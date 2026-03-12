# 📚 APPCONFIG

from APPCONFIG_REAL_DEPLOY import APPCONFIG_REAL_DEPLOY
from LOG import LOG

import boto3
appconfig = boto3.client('appconfigdata')
client = boto3.client('appconfig')

class APPCONFIG_REAL(
    APPCONFIG_REAL_DEPLOY
):

    @classmethod
    def GetValue(cls,
        appName:str = 'default'
    ) -> str:
        '''👉️ Gets the value of the AppConfig configuration.'''
        LOG.Print(cls.GetValue) 
    
        app = cls.GetApp(name= appName)
        env = app.GetDefaultEnv()
        config = app.GetDefaultEnv()
        
        session = appconfig.start_configuration_session(
            ApplicationIdentifier= app.ID,
            EnvironmentIdentifier= env.ID,
            ConfigurationProfileIdentifier= config.ID,
            RequiredMinimumPollIntervalInSeconds= 60)
        
        token = session['InitialConfigurationToken']
        
        config = appconfig.get_latest_configuration(
            ConfigurationToken=token)
        
        value = config['Configuration'].read()
        value = value.decode("utf-8") 
        
        LOG.Print(f'@: returning...', value)
        return value


    @classmethod
    def SetValue(
        cls,    
        content: str,
        format: str = 'TXT',
        appName:str = 'default'
    ): 
        '''👉️ Sets the value of the AppConfig.
        
        Parameters:
            * content: the string content
            * format: one of [TXT, JSON, YAML]
        '''

        LOG.Print(cls.SetValue, f'{format=}')
        
        app = cls.GetApp(name= appName)

        return app.SetValue(
            content= content,
            format= format)