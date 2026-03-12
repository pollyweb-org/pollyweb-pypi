# 📚 AWS

from PW_UTILS.UTILS import UTILS

class AWS:
    ''' 👉 AWS Helpers. '''

    MockUp = False

    @classmethod
    def ForReal(cls):
        '''👉 Is this for real?'''
        return cls.MockUp == False or AWS.LAMBDA().IsLambda()


    @classmethod
    def Region(cls):
        '''👉 Get the region.'''
        if not hasattr(cls, '_Region'):
            cls._Region = cls.STS().GetRegion()
        return cls._Region


    @classmethod
    def AccountNumber(cls):
        '''👉 Get the account number.'''
        if not hasattr(cls, '_AccountNumber'):
            cls._AccountNumber = cls.STS().GetAccountNumber()
        return cls._AccountNumber


    @classmethod
    def ACM(cls):
        '''👉 Amazon Certificate Manager (ACM)'''
        from ACM import ACM as proxy
        return proxy()
    

    @classmethod
    def APIGW(cls):
        '''👉 Helper for ApiGateway.'''
        from APIGW import APIGW as proxy
        return proxy()
        
  
    @classmethod
    def APPCONFIG(cls):
        '''👉 Helper for AppConfig.'''
        if AWS.ForReal():
            from APPCONFIG_REAL import APPCONFIG_REAL as proxy
            return proxy()
        else:
            from APPCONFIG_MOCK import APPCONFIG_MOCK as proxy
            return proxy()
        

    @classmethod
    def APPRUNNER(cls):
        '''👉 Helper for AppRunner.'''
        from APPRUNNER import APPRUNNER as proxy
        return proxy()
    

    @classmethod
    def APPSYNC(cls):
        '''👉 Helper for AppSync.'''
        from APPSYNC import APPSYNC as proxy
        return proxy()
        

    @classmethod
    def BUS(cls):
        '''👉 Helper for EventBus.'''
        if AWS.ForReal:
            from EVENTBRIDGE_REAL import EVENTBRIDGE_REAL as proxy
            return proxy()
        else:
            from EVENTBRIDGE_MOCK import EVENTBRIDGE_MOCK as proxy
            return proxy()
    
    
    @classmethod
    def CDK(cls):
        '''👉 AWS CDK'''
        from CDK import CDK
        return CDK()
        

    @classmethod
    def CLOUDFRONT(cls):
        '''👉 CloudFront Distribution'''
        from CLOUDFRONT import CLOUDFRONT
        return CLOUDFRONT()



    #@classmethod
    #def CODEBUILD(cls):
    #    '''👉 CodeBuild'''
    #    from CODEBUILD import CODEBUILD as proxy
    #    return proxy()
    

    @classmethod
    def CODEPIPELINE(cls):
        '''👉 CodePipeline'''
        from CODEPIPELINE import CODEPIPELINE as proxy
        return proxy()


    @classmethod
    def COGNITO(cls):
        '''👉 Helper for Amazon Cognito.'''
        if AWS.LAMBDA().IsLambda():
            from COGNITO_REAL import COGNITO_REAL as proxy
            return proxy()
        else:
            from COGNITO_MOCK import COGNITO_MOCK as proxy
            return proxy()


    @classmethod
    def DYNAMO(cls, 
        alias:str=None, 
        keys:list[str]=None, 
        name:str=None
    ):
        ''' 👉 DynamoDB table manager. '''
        if AWS.ForReal():
            from DYNAMO_REAL import DYNAMO_REAL as proxy
            return proxy(alias=alias, keys=keys, name=name)
        else:
            from DYNAMO_MOCK import DYNAMO_MOCK as proxy
            return proxy(alias=alias, keys=keys)
    

    @classmethod
    def ECR(cls):
        '''👉 Elastic Container Registry'''
        from ECR import ECR
        return ECR()
    

    @classmethod
    def ECS(cls):
        '''👉 Elastic Container Service'''
        from ECS import ECS
        return ECS()
    

    @classmethod
    def IAM(cls, 
        forReal: bool= None,
        cached: bool= False
    ):
        '''👉 Identity Access Management'''
        from IAM import IAM
        return IAM(cached= cached)


    @classmethod
    def LAMBDA(cls, 
        alias: str= None, 
        name: str= None,
        cached: bool= False
    ):

        ''' 👉 Looks up the `alias` in `os.environ`
        * if not found, considers the `alias` as the function name.'''

        if AWS.ForReal or UTILS.OS().IsLambda():
            
            if alias or name:
                from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL as proxy
                return proxy(alias, name=name, cached=cached)
            else:
                from LAMBDA_REAL import LAMBDA_REAL as proxy
                return proxy(cached=cached)
        else:
            if alias or name:
                from LAMBDA_FUNCTION_MOCK import LAMBDA_FUNCTION_MOCK as proxy
                return proxy(alias, name=name, cached=cached)
            else:
                from LAMBDA_MOCK import LAMBDA_MOCK as proxy
                return proxy(cached=cached)
        

    @classmethod
    def VPC(cls):
        '''👉 Network manager.'''
        from VPC import VPC as proxy
        return proxy()


    @classmethod
    def ROUTE53(cls, hosted_zone_id: str = None):
        from ROUTE53 import ROUTE53 as proxy
        if hosted_zone_id:
            return proxy(hosted_zone_id)
        else:
            return proxy()
        

    @classmethod
    def S3(cls):
        if AWS.ForReal():
            from S3_REAL import S3_REAL as proxy
            return proxy()
        else:
            from S3_MOCK import S3_MOCK as proxy
            return proxy()
    

    @classmethod
    def SECRETS(cls):
        if AWS.ForReal():
            from SECRETS_REAL import SECRETS_REAL as proxy
            return proxy()
        else:
            from SECRETS_MOCK import SECRETS_MOCK as proxy
            return proxy()


    @classmethod
    def SNS(cls):
        from SNS import SNS as proxy
        return proxy()
    

    @classmethod
    def SQS(cls):
        from SQS import SQS as proxy
        return proxy()
    

    @classmethod
    def SSM(cls):
        if AWS.ForReal():
            from SSM_REAL import SSM_REAL as proxy
            return proxy()
        else:
            from SSM_MOCK import SSM_MOCK as proxy
            return proxy()


    @classmethod
    def STEPFUNCS(cls):
        from STEPFUNCS import STEPFUNCS as proxy
        return proxy()


    @classmethod
    def STS(cls):
        from STS import STS as proxy
        return proxy()
    

    @classmethod
    def WAF(cls):
        from WAF import WAF as proxy
        return proxy()
    