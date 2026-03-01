from AWS import AWS
from PW_UTILS.LOG import LOG
from PW_UTILS.PRINTABLE import PRINTABLE
from PW_UTILS.UTILS import UTILS


class APIGW_RESTAPI_METHOD(PRINTABLE):

    ICON = '🅰️'


    def __init__(self,
        httpMethod:str,
        resource,
        client
    ) -> None:
        
        from APIGW_RESTAPI_RESOURCE import APIGW_RESTAPI_RESOURCE
        UTILS.RequireArgs([httpMethod, resource, client])
        UTILS.AssertIsType(resource, APIGW_RESTAPI_RESOURCE, require= True)

        self.HttpMethod = httpMethod
        self.Resource:APIGW_RESTAPI_RESOURCE = resource
        self.Client = client

        PRINTABLE.__init__(self, lambda: {
            'Method': self.HttpMethod,
            'Resource': self.Resource
        })


    def IntegrateMock(self):
        '''👉️ Integrate the method with a mock response.'''
        LOG.Print('@')

        # Integrate the method with a mock response
        response = self.Client.put_integration(
            restApiId= self.Resource.Api.ID,
            resourceId= self.Resource.ID,
            httpMethod= self.HttpMethod,
            type= 'MOCK',
            requestTemplates= {
                'application/json': '{"statusCode": 200}'
            })

        return response


    def IntegrateLambda(self, lambdaARN:str):
        '''👉️ Integrate the method with a Lambda function.'''
        LOG.Print('@')

        UTILS.RequireArgs([lambdaARN])

        region = AWS.STS().GetRegion()
        uri= f'arn:aws:apigateway:{region}:lambda:'
        uri+= f'path/2015-03-31/functions/{lambdaARN}/invocations'

        # Integrate the method with a Lambda function
        response = self.Client.put_integration(
            restApiId= self.Resource.Api.ID,
            resourceId= self.Resource.ID,
            httpMethod= self.HttpMethod,
            type= 'AWS_PROXY',
            integrationHttpMethod= 'POST',
            uri= uri)

        return response