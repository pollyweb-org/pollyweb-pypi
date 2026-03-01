from __future__ import annotations
from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RETRY import RetryWithBackoff
from ECR_REPO import ECR_REPO
from ECS_SERVICE import ECS_SERVICE
from ECS_TASK import ECS_TASK
from ECS_TASKDEF import ECS_TASKDEF
from pollyweb.utils.LOG import LOG
from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.STRUCT import STRUCT


import boto3

from VPC_NETWORK import VPC_NETWORK
client = boto3.client('ecs')


class ECS_CLUSTER(AWS_RESOURCE_ITEM):

    def __init__(self, 
        meta:dict,
        client,
        pool
    ):
        LOG.Print('@', meta)

        from ECS import ECS
        assert pool == ECS

        if 'cluster' in meta:
            meta = meta['cluster']

        meta = STRUCT(meta)

        self.Meta = meta
        self.Client = client
        self.Name = meta['clusterName']
        self.Arn = meta['clusterArn']
        self.Status = meta['status']

        AWS_RESOURCE_ITEM.__init__(self,
            pool= pool,
            client= client,
            name= self.Name,
            arn= self.Arn)

        PRINTABLE.__init__(self, lambda: {
            'Name': self.Name,
            'Arn': self.Arn,
            'Status': self.Status
        })


    def _Delete(self):
        '''👉️ Deletes the cluster.'''

        # Stop all cluster tasks.
        for task in self.ListTasks():
            task.Stop()

        # Delete all cluster services.
        for service in self.ListServices():
            service.Delete()

        # Delete all task definitions.
        self.DeleteAllTaskDefinitions()

        # Delete the cluster.
        @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
        def _delete():    
            self.Client.delete_cluster(
                cluster= self.Name)
        _delete()
        
        return self
    

    def ListServices(self):
        '''👉️ Lists the services in the cluster.'''
        return ECS_SERVICE.List(cluster= self)
    

    def ListTasks(self):
        '''👉️ Lists the tasks in the cluster.'''
        return ECS_TASK.List(cluster= self)
    

    def ListTaskDefinitions(self):
        '''👉️ Lists the task definitions in the cluster.'''
        return ECS_TASKDEF.List(cluster= self)
    

    def DeleteAllTaskDefinitions(self):
        '''👉️ Deletes all task definitions in the cluster.'''
        ECS_TASKDEF.DeleteAll(cluster= self)


    def Refresh(self):
        '''👉️ Refreshes the cluster.'''
        response = self.Client.describe_clusters(
            clusters=[self.Name])
        self.Meta = response['clusters'][0]
        self.Status = self.Meta['status']
        return self
    

    def RegisterTaskDefinition(self,
        ecr: ECR_REPO,
    ):
        '''👉 Registers a new task definition.'''
        return ECS_TASKDEF.Register(
            cluster= self,
            ecr= ecr)
    

    @staticmethod
    def List(ecs):
        '''👉 Lists the clusters.'''

        from ECS import ECS
        cls:ECS = ecs

        response = client.list_clusters()
        
        for cluster in response['clusterArns']:

            yield ECS_CLUSTER(
                meta= client.describe_clusters(
                    clusters=[cluster])['clusters'][0], 
                client= client,
                pool= cls)
            

    @staticmethod
    def Create(ecs, 
        name:str,
        ecr: ECR_REPO,
        vpc: VPC_NETWORK
    ) -> ECS_CLUSTER:
        '''👉 Creates a new ECS cluster.'''

        from ECS import ECS
        assert ecs == ECS
        cls:ECS = ecs

        # Create the cluster.
        response = client.create_cluster(
            clusterName= name,
            settings=[{
                'name': 'containerInsights',
                'value': 'enabled'  # Optional: Enable Container Insights for monitoring
            }])
        meta = response['cluster']
        cluster = ECS_CLUSTER(
            meta= meta, 
            client= client,
            pool= cls)

        # Register the task definition.
        task = cluster.RegisterTaskDefinition(
            ecr= ecr)
        
        # Create the service.
        service = task.CreateService(
            name= name,
            vpc= vpc)

        return cluster


    @classmethod
    def EnsureRole(cls):
        # Ensure the IAM role
        from AWS import AWS
        role = AWS.IAM().EnsureServiceRole(
            service= 'ecs-tasks',
            policies= [
                "AmazonEC2ContainerRegistryReadOnly",
                "AmazonS3ReadOnlyAccess",
                "CloudWatchLogsFullAccess",
            ])
        return role