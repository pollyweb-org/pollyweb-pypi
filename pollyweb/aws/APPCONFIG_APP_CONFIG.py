from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS


class APPCONFIG_APP_CONFIG:
    '''👉️ AppConfig Configuration Profile.'''

    ICON = '📋'
    DEFAULT_TEXT = 'empty'


    def __init__(self,
        meta: dict,
        client,
        app       
    ) -> None:
        
        struct = STRUCT(meta)
        self.Client = client 
        self.ID = struct.RequireStr('Id')
        self.Name = struct.RequireStr('Name')

        from APPCONFIG_APP import APPCONFIG_APP
        self.App:APPCONFIG_APP = app

        self.FullName = f'{self.App.Name}/{self.Name}'


    def ListVersions(self):
        LOG.Print(f'@: {self.FullName}')
        
        response = self.Client.list_hosted_configuration_versions(
            ApplicationId= self.App.ID,
            ConfigurationProfileId= self.ID)

        from APPCONFIG_APP_VERSION import APPCONFIG_APP_VERSION
        versions: list[APPCONFIG_APP_VERSION] = []

        for item in STRUCT(response)['Items']:
            
            version = APPCONFIG_APP_VERSION(
                client= self.Client, 
                meta= item,
                config= self)
            
            versions.append(version)

        return versions


    def CreateVersion(self,
        content: str,
        format: str = 'TXT', # TEXT, YAML, JSON
        description: str = 'A version with text value'
    ):
        LOG.Print(f'@: {self.FullName}')

        UTILS.RequireArgs([content, type])
        UTILS.AssertIsAnyValue(format, ['TXT', 'JSON', 'YAML'])

        if format == 'TXT':
            contentType = 'text/plain'
        elif format == 'JSON':
            contentType = 'application/json'
        elif format == 'YAML':
            contentType = 'application/x-yaml'
        else:
            LOG.RaiseException(f'@: Unexpected format: {format}')

        response = self.Client.create_hosted_configuration_version(
            ApplicationId= self.App.ID,
            ConfigurationProfileId= self.ID,
            ContentType= contentType, 
            # Specifycontent content type as plain text
            Content= content.encode('utf-8'),
            Description= description)
        
        # If the response includes a 'VersionNumber', the operation was likely successful
        if 'VersionNumber' in response:
            LOG.Print(
                f"@: Configuration version created successfully.",
                f"Version number: {response['VersionNumber']}")
        else:
            LOG.RaiseException(
                "@: Configuration version creation might not have been successful.",
                "Check the response details.", 
                response)

        from APPCONFIG_APP_VERSION import APPCONFIG_APP_VERSION
        return APPCONFIG_APP_VERSION(
            client= self.Client,
            meta= response,
            config= self)
    

    def DeleteVersions(self):
        LOG.Print(f'@: {self.FullName}')

        for version in self.ListVersions():
            version.Delete()

    
    def Delete(self):
        LOG.Print(f'@: {self.FullName}')
        
        # Delete the versions first.
        self.DeleteVersions()

        # Now delete the configuration.
        self.Client.delete_configuration_profile(
            ApplicationId= self.App.ID,
            ConfigurationProfileId= self.ID)
        

