# 📚 MANIFESTER

from ACTOR import ACTOR
from NLWEB import NLWEB
from PW_AWS.AWS import AWS
from pollyweb import LOG
from MANIFEST import MANIFEST
from pollyweb import UTILS
from WEB import WEB


CONFIG_APP = 'Manifester-Manifest'
CONFIG_PROFILE = 'Manifester-Manifest-Profile'
CONFIG_ENV = 'Dev'


class MANIFESTER(ACTOR):
    ''' 👉️ Sends manifest updates to a listener.'''
        

    @classmethod
    def _GetAppConfig(cls):
        '''👉️ Gets a configured AppConfig client.'''

        # Get the appConfig client.
        appConfig = AWS.APPCONFIG()

        # Set the environment if in a command line Script.
        if AWS.ForReal() and UTILS.OS().IsCommandLineScript():

            # Set the variables.
            UTILS.OS().SetCommandLineEnv({
                'CONFIG_APP': CONFIG_APP,
                'CONFIG_PROFILE': CONFIG_PROFILE,
                'CONFIG_ENV': CONFIG_ENV
            })

        return appConfig    


    @classmethod
    def PublishManifest(cls, 
        manifest:str|MANIFEST
    ):
        '''👉️ Sets the manifest content in AppConfig.'''
        
        # Validate the request.
        UTILS.AssertIsAnyType(manifest, options=[str, MANIFEST])

        # Validate the manifest.
        if UTILS.IsType(manifest, str):
            manifest = MANIFEST(manifest)
        manifest.VerifySyntax()

        # Get the yaml string, if its a manifest object.
        if UTILS.IsType(manifest, MANIFEST):
            manifest = manifest.ToYaml()

        # Get an AppConfig client.
        appConfig = cls._GetAppConfig()
        
        # Set the value on AppConfig.
        appConfig.SetValue(
            content= manifest, 
            type= 'YAML')


    @classmethod
    def InvokeAlerter(cls):
        '''👉️ Invokes HandleAlerter().'''
        cls.HandleAlerter({
            "Type":"OnDeploymentComplete"
        })


    @classmethod
    def HandleAlerter(cls, event):
        '''👉️ Sends an Update to the listener without Update into - i.e., all will be infered.
        * https://docs.aws.amazon.com/appconfig/latest/userguide/working-with-appconfig-extensions-about-predefined-notification-sqs.html
        
        Example:
        {
            "Type": "OnDeploymentComplete"
        }
        '''
        LOG.Print(f'📜 MANIFESTER.HandleAlerter()', event)

        for record in AWS.LAMBDA().ParseEvent(event):

            if record['Type'] != 'OnDeploymentComplete':
                LOG.Print('🔴 MANIFESTER.HandleAlerter() -> Unknown event type, ignoring.')
                continue

            yaml = AWS.APPCONFIG().GetValue()
            manifest = MANIFEST(yaml)
            domain = NLWEB.CONFIG().RequireDomain()
            manifest.VerifyIdentity(expectedDomain=domain)
            manifest.VerifySyntax()

            NLWEB.ROLES().LISTENER().InvokeUpdated(
                source= 'Alerter@Manifester',
                to= NLWEB.CONFIG().RequireListener(),
                update= None)
            return True
        
        # OnDeploymentComplete not found in the event records. 
        return False


    @classmethod
    def _viewer(cls, format):
        ''' 
        📜 Reads the manifest's YAML from the AppConfig,
        then converts the YAML into an object, 
        then returns the object.
        '''
        yaml = AWS.APPCONFIG().GetValue()
        manifest = UTILS.FromYaml(yaml)

        return WEB().HttpResponse(
            body= manifest, 
            format= format)


    @classmethod
    def HandleYamlViewer(cls):
        return cls._viewer('yaml')
    
    @classmethod
    def HandleJsonViewer(cls):
        return cls._viewer('json')
    

    @classmethod
    def HandleDefaultViewer(cls):
        return cls._viewer('text')
    

    @classmethod
    def HandleValidator(cls, event):
        '''👉️ Validates the AppConfig content change.'''

        # Read the Base64 content
        encoded = event['content']
        
        # Decode the Base64 content
        yaml = UTILS.DecodeTextBase64(encoded)

        # Validate the manifest.
        manifest = MANIFEST(yaml)
        manifest.VerifySyntax()