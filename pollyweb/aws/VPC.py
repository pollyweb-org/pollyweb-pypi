from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from pollyweb.utils.UTILS import UTILS
from VPC_NETWORK import VPC_NETWORK
from pollyweb.utils.LOG import LOG

import boto3
client = boto3.client('ec2')
resource = boto3.resource('ec2')


class VPC(AWS_RESOURCE_POOL[VPC_NETWORK]):

    ICON = '🌐'


    @classmethod
    def List(cls) -> list[VPC_NETWORK]:
        '''👉️ Returns a list of all resources.'''

        response = client.describe_vpcs()
        vpcs = response.get('Vpcs', [])

        # Create a list of VPC objects
        return [
            VPC_NETWORK(
                name= None,
                meta= vpc,
                client= client,
                resource= resource,
                pool= cls)
            for vpc in vpcs
        ]
    
    
    @classmethod
    def Ensure(cls, 
        name:str, 
        prefix:str= None
    ):
        '''👉️ Ensures the VPC.'''
        LOG.Print('@', prefix)
        
        return super()._Ensure(
            client= client,
            name= name,
            prefix= prefix)
        

    @classmethod
    def Create(cls, 
        name:str,
        prefix:str= None
    ):  
        LOG.Print('@: Find an empty prefix.')
        if prefix is None:
            vpcs = cls.List()
            while prefix is None:
                prefix = f'10.{UTILS.Random(50, 200)}'
                for vpc in vpcs:
                    if vpc.CIDR.startswith(prefix):
                        prefix = None
                        break

        LOG.Print('@: Creating the VPC')
        response = client.create_vpc(
            CidrBlock= f'{prefix}.0.0/16')
        
        vpc_id = response['Vpc']['VpcId']
    
        # Check VPC creation status and wait if necessary
        client.get_waiter('vpc_available').wait(VpcIds=[vpc_id])
        
        vpc = VPC_NETWORK(
            pool= cls,
            name= name,
            meta= response['Vpc'], 
            client= client,
            resource= resource)

        vpc.Tag(tags= dict(Name= name))
        vpc.EnableDnsSupport()
        vpc.EnableDnsHostnames()
        vpc.EnableInternet()
        vpc.CreateSubnets(prefix= prefix)
        vpc.CreatePublicSecurityGroup()
        vpc.CreatePublicLoadBalancer()
        
        return vpc


