import boto3

from CODECOMMIT_REPO import CODECOMMIT_REPO
from IAM_ROLE import IAM_ROLE
from S3_BUCKET import S3_BUCKET
codepipeline = boto3.client('codepipeline')


class CODEPIPELINE:
    

    def CreatePipeline(self, 
        name:str, 
        s3: S3_BUCKET,
        repo: CODECOMMIT_REPO,
    ):
        '''👉 Creates a new CodePipeline pipeline.'''

        from AWS import AWS
        role = AWS.IAM().EnsureServiceRole('codepipeline')

        artifactStore = dict(
            type='S3',
            location= s3.Name)

        source = {
            'name': 'Source',
            'actions': [
                {
                    'name': 'Source',
                    'actionTypeId': {
                        'category': 'Source',
                        'owner': 'AWS',
                        'provider': 'CodeCommit',
                        'version': '1'
                    },
                    'outputArtifacts': [
                        {'name': 'SourceArtifact'}
                    ],
                    'configuration': {
                        'RepositoryName': repo.Name,
                        'BranchName': 'main'
                    },
                    'runOrder': 1
                },
            ]
        }

        build = {
            'name': 'Build',
            'actions': [
                {
                    'name': 'Build',
                    'actionTypeId': {
                        'category': 'Build',
                        'owner': 'AWS',
                        'provider': 'CodeBuild',
                        'version': '1'
                    },
                    'inputArtifacts': [{'name': 'SourceArtifact'}],
                    'outputArtifacts': [{'name': 'BuildArtifact'}],
                    'configuration': {
                        'ProjectName': 'MyProject'
                    },
                    'runOrder': 1
                },
            ]
        }

        deploy = {
            'name': 'Deploy',
            'actions': [
                {
                    'name': 'Deploy',
                    'actionTypeId': {
                        'category': 'Deploy',
                        'owner': 'AWS',
                        'provider': 'CodeDeploy',
                        'version': '1'
                    },
                    'inputArtifacts': [{'name': 'BuildArtifact'}],
                    'configuration': {
                        'ApplicationName': 'MyApplication',
                        'DeploymentGroupName': 'MyDeploymentGroup'
                    },
                    'runOrder': 1
                },
            ]
        }   

        response = codepipeline.create_pipeline(
            pipeline= dict(
                name= name,
                roleArn= role.RequireArn(),
                artifactStore= artifactStore,
                stages= [
                    source,
                    build,
                    deploy
                ]))
        
        return response