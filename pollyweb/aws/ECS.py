from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from ECR_REPO import ECR_REPO
from ECS_CLUSTER import ECS_CLUSTER
from VPC_NETWORK import VPC_NETWORK


class ECS(AWS_RESOURCE_POOL[ECS_CLUSTER]):
    

    @classmethod
    def Ensure(cls, 
        name:str,
        ecr: ECR_REPO,
        vpc: VPC_NETWORK           
    ):
        '''👉 Ensures that the ECS cluster exists.'''
        return cls._Ensure(
            name= name,
            ecr= ecr,
            vpc= vpc)


    @classmethod
    def Create(cls, 
        name:str,
        ecr: ECR_REPO,
        vpc: VPC_NETWORK
    ) -> ECS_CLUSTER:
        '''👉 Creates a new ECS cluster.'''
        return ECS_CLUSTER.Create(
            ecs= cls,
            name= name,
            ecr= ecr,
            vpc= vpc)
       

    @classmethod
    def List(cls):
        '''👉 Lists the clusters.'''
        return ECS_CLUSTER.List(ecs= cls)
        
