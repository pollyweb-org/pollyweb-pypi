
from ECR_REPO import ECR_REPO
from ECS_SERVICE import ECS_SERVICE
from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS
from VPC_NETWORK import VPC_NETWORK


class ECS_TASKDEF:


    def __init__(self, 
        client: any,
        cluster,
        meta:dict
    ) -> None:
        
        if 'taskDefinition' in meta:
            meta = meta['taskDefinition']

        self.Meta = meta
        self.Arn = STRUCT(meta).RequireStr('taskDefinitionArn')
        
        from ECS_CLUSTER import ECS_CLUSTER
        UTILS.AssertIsType(cluster, ECS_CLUSTER, require= True)
        
        self.Cluster:ECS_CLUSTER = cluster
        self.Client = client


    def Delete(self):
        '''👉️ Deletes the task definition.'''
        LOG.Print('@')

        self.Client.deregister_task_definition(
            taskDefinition= self.Arn)

        return self


    def CreateService(self, 
        name:str, 
        vpc: VPC_NETWORK,
        desiredCount:int= 1
    ):
        '''👉️ Creates a service.'''
        return ECS_SERVICE.Create(
            taskdef= self,
            name= name,
            vpc= vpc,
            desiredCount= desiredCount)
    

    @staticmethod
    def Register(cluster,
        ecr: ECR_REPO,
    ):
        '''👉 Registers a new task definition.'''
        LOG.Print('@')

        from ECS_CLUSTER import ECS_CLUSTER
        self:ECS_CLUSTER = cluster

        # Ensure the IAM role
        role = self.EnsureRole()

        cpu = 256
        memory = 512

        # Register the task definition.
        response = self.Client.register_task_definition(

            family= self.Name,

            networkMode='awsvpc',  # required for Fargate tasks
            requiresCompatibilities=['FARGATE'],

            executionRoleArn= role.RequireArn(),

            cpu= str(cpu),
            memory= str(memory),

            runtimePlatform={
                'cpuArchitecture': 'X86_64',  # Modify as needed
                'operatingSystemFamily': 'LINUX'
            },

            containerDefinitions= [{
                'name': self.Name,
                'image': f'{ecr.RepositoryUri}:latest',
                'cpu': cpu,  # Adjust based on needs
                'memory': memory,  # Adjust based on needs
                'essential': True,
                'portMappings': [
                    {
                        'containerPort': 8080,
                        'hostPort': 8080,
                        'protocol': 'tcp'
                    },
                ],
            }])
        
        return ECS_TASKDEF(
            meta= response['taskDefinition'],
            cluster= self,
            client= self.Client)
    

    @staticmethod
    def List(cluster):
        '''👉️ Lists the task definitions in the cluster.'''
        LOG.Print('@')

        from ECS_CLUSTER import ECS_CLUSTER
        self:ECS_CLUSTER = cluster

        response = self.Client.list_task_definitions(
            familyPrefix= self.Name)
        response = STRUCT(response)
        
        ret:list[ECS_TASKDEF] = []
        for taskArn in response.ListStr('taskDefinitionArns'):
            tdef = ECS_TASKDEF(
                cluster= self,
                meta= dict(
                    taskDefinitionArn= taskArn),
                client= self.Client)
            ret.append(tdef)
        return ret
    

    @staticmethod
    def DeleteAll(cluster):
        '''👉️ Deletes all task definitions in the cluster.'''
        for taskdef in ECS_TASKDEF.List(cluster):
            taskdef.Delete()
        