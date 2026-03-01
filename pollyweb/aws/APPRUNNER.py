from APPRUNNER_CONFIG import APPRUNNER_CONFIG
from APPRUNNER_SERVICE import APPRUNNER_SERVICE
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from ECR_REPO import ECR_REPO
from PW_UTILS.LOG import LOG

import boto3

from PW_UTILS.UTILS import UTILS
client = boto3.client('apprunner')


class APPRUNNER(AWS_RESOURCE_POOL[APPRUNNER_SERVICE]):


    @classmethod
    def List(cls, client=None):
        '''👉️ Returns a list of all resources.'''

        response = client.list_services()
        services = response.get('ServiceSummaryList', [])
        return [
            APPRUNNER_SERVICE(
                pool= cls,
                meta= service,
                client= client)
            for service in services
        ]   
    

    @classmethod
    def Ensure(cls,
        name:str,
        ecr: ECR_REPO,
        config: APPRUNNER_CONFIG= APPRUNNER_CONFIG()
    ) -> APPRUNNER_SERVICE:
        '''👉 Ensures that the apprunner service exists.'''
        LOG.Print('@', name)

        return super()._Ensure(
            client= client,
            name= name,
            ecr= ecr,
            config= config)
    

    @classmethod
    def Create(cls, 
        name: str,
        ecr: ECR_REPO,
        config: APPRUNNER_CONFIG= APPRUNNER_CONFIG()
    ) -> APPRUNNER_SERVICE:
        '''👉️ Creates a new resource.'''

        UTILS.AssertIsType(name, str, require= True)
        UTILS.AssertIsType(ecr, ECR_REPO, require= True)
        UTILS.AssertIsType(config, APPRUNNER_CONFIG, require= False)

        # Ensure the IAM role
        role = cls.EnsureRole()

        response = client.create_service(
            ServiceName= name,
            SourceConfiguration={
                'ImageRepository': {
                    'ImageIdentifier': ecr.GetImageUri(),
                    'ImageRepositoryType': 'ECR',
                    'ImageConfiguration': {
                        'Port': '8080'
                    }
                },
                'AuthenticationConfiguration': {
                    'AccessRoleArn': role.RequireArn()
                },
            },
            InstanceConfiguration={
                'Cpu': str(config.vCPUs * 1024),  # 1 vCPU
                'Memory': str(config.MemoryInGB * 1024) # 2 GB
            })
        
        runner = APPRUNNER_SERVICE(
            pool= cls,
            meta= response,
            client= client)
        
        runner.WaitUntilReady()

        return runner
        
        
    @classmethod
    def EnsureRole(cls):
        # Ensure the IAM role
        from AWS import AWS
        role = AWS.IAM().EnsureServiceRole(
            service= 'build.apprunner',
            policies= [
                "AmazonEC2ContainerRegistryReadOnly",
                "AmazonS3ReadOnlyAccess",
                "CloudWatchLogsFullAccess",
            ])
        return role
    