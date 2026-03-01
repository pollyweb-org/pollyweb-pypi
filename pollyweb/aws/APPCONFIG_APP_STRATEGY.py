from pollyweb.utils.STRUCT import STRUCT


class APPCONFIG_APP_STRATEGY:


    ICON = '📋'

    def __init__(self,
        client, 
        meta: dict             
    ) -> None:
        
        struct = STRUCT(meta)

        self.ID = struct['Id']
        self.Name = struct['Name']
        self.Client = client