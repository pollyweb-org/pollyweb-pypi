from LOG import LOG
from PW_UTILS.PRINTABLE import PRINTABLE


class IAM_SERVICE_CREDENTIAL(PRINTABLE):
    '''👉️ Helper class for IAM credentials.'''
    
    def __init__(self, 
        meta:dict,
        client
    ):
        '''👉 Initializes the credentials.'''
        LOG.Print('@', meta)
        
        self.Client = client
        self.Meta = meta
        self.ServicePassword:str = meta['ServicePassword'] if 'ServicePassword' in meta else None
        self.ServiceUserName:str = meta['ServiceUserName'] if 'ServiceUserName' in meta else None
        self.ServiceSpecificCredentialId:str = meta['ServiceSpecificCredentialId'] if 'ServiceSpecificCredentialId' in meta else None
        

        PRINTABLE.__init__(self, lambda: {
            'ServiceUserName': self.ServiceUserName,
            'ServiceSpecificCredentialId': self.ServiceSpecificCredentialId,
            #'ServicePassword': self.ServicePassword,
        })
    
    
    def Delete(self):
        '''👉 Deletes the credentials.'''
        LOG.Print('@', self)
        
        self.Client.delete_service_specific_credential(
            ServiceSpecificCredentialId= self.ServiceSpecificCredentialId)