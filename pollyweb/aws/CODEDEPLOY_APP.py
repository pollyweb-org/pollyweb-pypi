
from CODEDEPLOY_DEPLOYMENT_GROUP import CODEDEPLOY_GROUP
from ECS_SERVICE import ECS_SERVICE
from IAM_ROLE import IAM_ROLE


class CODEDEPLOY_APP:


    def __init__(self, client, meta:dict):
        '''👉 Initializes the application.'''
        self.Client = client
        self.Meta = meta
        self.Name = meta['applicationName']
        self.ComputePlatform = meta['computePlatform']
        self.CreateTime = meta['createTime']
        self.ApplicationId = meta['applicationId']
        self.Tags = meta['tags']


    def CreateDeploymentGroup(self,
        name:str,
        ecs: ECS_SERVICE,
        serviceRole: IAM_ROLE,
        tags:list={}
    ) -> dict:
        '''👉 Creates a new deployment group.'''
        
        app = self

        response = self.Client.create_deployment_group(
            applicationName= app.Name,
            deploymentGroupName= name,
            deploymentConfigName= 'CodeDeployDefault.ECSAllAtOnce',
            serviceRoleArn= serviceRole.RequireArn(),
            ecsServices=[
                {
                    'serviceName': ecs.Name,
                    'clusterName': ecs.Cluster.Name
                },
            ],
            tags= tags)
        
        meta = response['deploymentGroupInfo']

        return CODEDEPLOY_GROUP(
            client= self.Client,
            meta= meta)