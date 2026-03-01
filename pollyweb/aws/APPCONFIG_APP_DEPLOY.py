from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
import time

from pollyweb.utils.UTILS import UTILS

class APPCONFIG_APP_DEPLOY:

    ICON = '📋'

    def __init__(self,
        meta: dict, 
        client,
        env,
        version
    ) -> None:
        
        UTILS.AssertIsType(client, object)
        self.Client = client

        from APPCONFIG_APP_ENV import APPCONFIG_APP_ENV
        UTILS.AssertIsType(env, APPCONFIG_APP_ENV)
        self.Env:APPCONFIG_APP_ENV = env

        from APPCONFIG_APP_VERSION import APPCONFIG_APP_VERSION
        UTILS.AssertIsType(version, APPCONFIG_APP_VERSION)
        self.Version:APPCONFIG_APP_VERSION = version
        self.Config = self.Version.Config
        self.App = self.Config.App
        
        UTILS.AssertIsType(meta, dict)
        struct = STRUCT(meta)
        
        self.ID  = struct.RequireStruct('ResponseMetadata')['RequestId']
        self.Number = struct['DeploymentNumber']
        self.State= struct['State']
        

    def GetState(self):
        '''👉️ Get the deployment state.'''

        # Get the deployment state.
        response = self.Client.get_deployment(
            ApplicationId= self.App.ID,
            EnvironmentId= self.Env.ID,
            DeploymentNumber= self.Number)
        self.State = STRUCT(response).RequireStr('State')

        # Get the failure reason if the deployment failed.
        if self.State in ['ROLLED_BACK', 'FAILED']:
            self.FailureReason = response['Deployment'].get(
                'StateReason', 'No reason provided.')
        else:
            self.FailureReason = None    

        # Return the state.
        return self.State


    def WaitToFinish(self,
        wait_time= 10, 
        max_attempts= 30,
        raise_exception= True
    ):
        '''👉️ Wait for the deployment to finish.
            * `wait_time`: The time to wait between attempts.
            * `max_attempts`: The maximum number of attempts.
            * `raise_exception`: Raise an exception if the deployment fails.
        '''

        for attempt in range(max_attempts):

            self.GetState()
            LOG.Print(f'@: Attempt {attempt + 1}/{max_attempts}: Deployment status is {self.State}')

            if self.State in ['COMPLETE', 'ROLLED_BACK', 'FAILED']:

                if self.State == 'FAILED' and raise_exception:
                    LOG.RaiseException(
                        f'Deployment failed. {self.FailureReason}', self)
                    
                if self.State == 'ROLLED_BACK' and raise_exception:
                    LOG.RaiseException(
                        f'Deployment rolled back. {self.FailureReason}', self)
                
                return self.State

            time.sleep(wait_time)

        raise TimeoutError(
            f'@: Deployment did not complete within {max_attempts * wait_time} seconds.')
