from APIGW_RESTAPI_METHOD import APIGW_RESTAPI_METHOD
from pollyweb.utils.LOG import LOG
from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.UTILS import UTILS


class APIGW_RESTAPI_RESOURCE(PRINTABLE):

    ICON = '🅰️'


    def __init__(self,
        resourceID:str,
        parentID:str, # root resource has no parent
        path:str,
        api,
        client
    ) -> None:
        LOG.Print('@')
        
        from APIGW_RESTAPI import APIGW_RESTAPI
        UTILS.RequireArgs([resourceID, path, api, client])
        UTILS.AssertIsStr(resourceID, require= True)
        UTILS.AssertIsStr(path, require= True)
        UTILS.AssertIsStr(parentID)
        UTILS.AssertIsType(api, APIGW_RESTAPI, require= True)

        self.ID = resourceID
        self.Api:APIGW_RESTAPI= api
        self.ParentId= parentID
        self.Path= path
        self.Client= client

        PRINTABLE.__init__(self, lambda: {
            'ID': self.ID,
            'ParentId': self.ParentId,
            'Path': self.Path,
            'Api': self.Api,
        })


    def AddMethod(self, httpMethod:str):
        LOG.Print('@')

        UTILS.RequireArgs([httpMethod])
        UTILS.AssertIsAnyValue(httpMethod, ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS', 'ANY'])
        
        # Create a new method
        try:
            self.Client.put_method(
                restApiId= self.Api.ID,
                resourceId= self.ID,
                httpMethod= httpMethod, 
                authorizationType='NONE',  # can be 'AWS_IAM', 'CUSTOM', etc.
                apiKeyRequired= False)
        except Exception as e:
            if 'Method already exists' not in str(e):
                raise e
        
        return APIGW_RESTAPI_METHOD(
            httpMethod= httpMethod,
            resource= self,
            client= self.Client)
    