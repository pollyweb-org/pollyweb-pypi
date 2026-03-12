from LOG import LOG
from VPC_SECURITYGRP import VPC_SECURITYGRP
from VPC_SUBNET import VPC_SUBNET

import boto3
elbv2_client = boto3.client('elbv2')


class VPC_ELB:

    ICON = '🌐'


    def __init__(self,
        vpc:object,
        meta:dict,
        client:object,
        resource:object=None,             
    ) -> None:
        
        self.Client = client
        self.Meta = meta
        self.Resource = resource

        # Get the name and Arn of the load balancer from the meta data.
        self.Name = meta['LoadBalancerName']
        self.Arn = meta['LoadBalancerArn']
        
        from VPC_NETWORK import VPC_NETWORK
        self.Vpc:VPC_NETWORK = vpc


    def Delete(self):
        '''👉️ Deletes the load balancer.'''
        LOG.Print('@')

        # Delete the load balancer.
        self.Client.delete_load_balancer(
            LoadBalancerArn= self.Arn)
        
        # Wait to be deleted.
        waiter = self.Client.get_waiter('load_balancers_deleted')
        waiter.wait(
            LoadBalancerArns=[ self.Arn ])
        
        return self
        

    @staticmethod
    def CreateLoadBalancer(vpc, 
        name:str, 
        subnets:list[VPC_SUBNET], 
        securityGroups:list[VPC_SECURITYGRP]
    ):
        '''👉️ Creates a load balancer for a VPC.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        load_balancer = elbv2_client.create_load_balancer(
            Name= name,
            Scheme= 'internet-facing',  # Use 'internal' if not public
            Subnets= [ subnet.ID for subnet in subnets ], 
            SecurityGroups= [ grp.ID for grp in securityGroups ])
        
        return VPC_ELB(
            vpc= self,
            meta= load_balancer['LoadBalancers'][0],
            client= self.Client)
    

    @staticmethod
    def GetLoadBalancers(vpc):
        '''👉️ Lists the load balancers in a VPC.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        response = elbv2_client.describe_load_balancers()
        return [ 
            VPC_ELB(
                vpc= self,
                meta= lb,
                client= elbv2_client) 
            for lb in response['LoadBalancers'] 
            if self.ID in lb['VpcId'] 
        ]