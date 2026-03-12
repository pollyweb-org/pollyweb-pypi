from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from CODEBUILD_PROJECT import CODEBUILD_PROJECT


import boto3

from LOG import LOG
client = boto3.client('codebuild')


class CODEBUILD(AWS_RESOURCE_POOL[CODEBUILD_PROJECT]):
    
    ICON = '🏗️'


    @classmethod
    def EnsureRole(cls):
        # Ensure the IAM role
        from AWS import AWS
        role = AWS.IAM().EnsureServiceRole(
            service= 'codebuild',
            policies= [
                "AmazonS3ReadOnlyAccess",
                "AmazonEC2ContainerRegistryPowerUser",
                "CloudWatchLogsFullAccess",
                "AWSCodeBuildAdminAccess",
                "AWSCodeCommitPowerUser",
            ])
        return role


    @classmethod
    def Create(cls, 
        name: str, 
        #repo: CODECOMMIT_REPO
    ):
        '''👉 Creates a new CodeBuild project.'''
        LOG.Print(f'@: project {name}')

        # Ensure the IAM role
        role = cls.EnsureRole()
        
        # Get environment variables
        from AWS import AWS
        accountID = AWS.STS().GetAccountNumber()
        region = AWS.STS().GetRegion()

        # Create the project
        build_project_response = client.create_project(
            name= name,
            serviceRole= role.RequireArn(),
            logsConfig={
                'cloudWatchLogs': {
                    'status': 'ENABLED',
                    'groupName': 'CodeBuildLogs',  # Optional
                    'streamName': name  # Optional
                }
            },
            source={
                'type': 'CODECOMMIT',
                #'location': repo.HTTP_URL
            },
            artifacts={
                'type': 'NO_ARTIFACTS',
            },
            environment={
                'type': 'LINUX_CONTAINER',
                'image': 'aws/codebuild/standard:5.0',
                'computeType': 'BUILD_GENERAL1_SMALL',
                'privilegedMode': True,
                #'imagePullCredentialsType': 'SERVICE_ROLE',
                'environmentVariables': [
                    {
                        'name': 'AWS_ACCOUNT_ID',
                        'value': accountID
                    },
                    {
                        'name': 'AWS_DEFAULT_REGION',
                        'value': region
                    }
                ]
            })
        
        meta = build_project_response['project']
        return CODEBUILD_PROJECT(
            meta= meta, 
            pool= cls,
            client= client)
   
    
    @classmethod
    def List(cls):
        '''👉 Lists all CodeBuild projects.'''
        
        def getProject(name: str):
            project_response = client.batch_get_projects(
                names= [name])
            meta = project_response['projects'][0]
            
            return CODEBUILD_PROJECT(
                meta= meta, 
                pool= cls,
                client= client)
        
        projects_response = client.list_projects()
        
        ret = []
        for name in projects_response['projects']:
            proj = getProject(name)
            ret.append(proj)

        return ret
    

    @classmethod
    def Ensure(cls,
        name: str,
        repo: CODECOMMIT_REPO
    ):
        '''👉 Ensures a CodeBuild project.'''
        return super()._Ensure(
            client= client,
            name= name,
            repo= repo)