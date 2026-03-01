from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS


class APPCONFIG_APP_ENV:

    ICON = '📋'

    def __init__(self, 
        client, 
        meta: dict, 
        app
    ):
        from APPCONFIG_APP import APPCONFIG_APP
        UTILS.AssertIsType(app, APPCONFIG_APP, require=True)

        struct = STRUCT(meta)
        self.ID = struct.RequireStr('Id')
        self.Name = struct.RequireStr('Name')
        self.App = app
        self.Client = client 
        self.FullName = f'{self.App.Name}/{self.Name}'


    def Delete(self):
        LOG.Print(f'@: {self.FullName}')

        self.Client.delete_environment(
            ApplicationId= self.App.ID,
            EnvironmentId= self.ID)
    
