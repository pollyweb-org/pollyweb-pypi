from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RETRY import RetryWithBackoff
from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS
from VPC_ELB import VPC_ELB
from VPC_INTERNETGW import VPC_INTERNETGW
from VPC_NATGW import VPC_NATGW
from VPC_SECURITYGRP import VPC_SECURITYGRP
from VPC_SUBNET import VPC_SUBNET
from PW_UTILS.PRINTABLE import PRINTABLE


import boto3
elbv2_client = boto3.client('elbv2')

from botocore.exceptions import ClientError

class VPC_NETWORK(AWS_RESOURCE_ITEM):

    ICON = '🌐'
    

    def __init__(self, 
        name:str,
        meta:dict, 
        pool,
        client,
        resource
    ):
        '''👉️ Initializes the VPC.'''

        self.Meta = meta
        self.ID = meta['VpcId']
        '''👉️ The VPC ID.'''
        self.CIDR = meta['CidrBlock']
        self.State = meta['State']
        
        # Get the tags and create a dictionary.
        self.Tags = meta.get('Tags', [])
        self.TagDictionary:dict = {
            tag['Key']: tag['Value'] 
            for tag in self.Tags
        }

        # default the name to the ID.
        if name is None:
            name = self.TagDictionary.get('Name', self.ID)

        # Get any attached internet gateway
        self.InternetGateway = None
        if self.InternetGateway == None:
            for igw in client.describe_internet_gateways()['InternetGateways']:
                for attachment in igw.get('Attachments', []):
                    if attachment['VpcId'] == self.ID:

                        from VPC_INTERNETGW import VPC_INTERNETGW
                        self.InternetGateway = VPC_INTERNETGW(
                            meta= igw, 
                            client= client, 
                            resource= resource,
                            vpc= self)
                        
                        break

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool, 
            client= client,
            resource= resource,
            arn= f'arn:aws:ec2:{client.meta.region_name}::vpc/{self.ID}',
            name= name)
        
        # Create the resource.
        self.Vpc = resource.Vpc(self.ID)
        
        PRINTABLE.__init__(self, lambda: {
            'ID': self.ID,
            'CIDR': self.CIDR
        })


    def Tag(self, tags:dict, resource:str=None):
        '''👉️ Tags the VPC.'''
        LOG.Print('@', self)
        
        if len(tags.keys()) == 0:
            LOG.RaiseException('No tags provided.')

        marshalled_tags = [
            {
                'Key': key, 
                'Value': value
            } 
            for key, value in tags.items()
        ]

        self.Client.create_tags(
            Resources= [resource or self.ID],
            Tags= marshalled_tags)
        
        if resource is None:
            self.TagDictionary.update(tags)
            self.Tags = marshalled_tags
        

    def EnableDnsSupport(self):
        '''👉️ Enables DNS support.'''
        LOG.Print('@', self)

        self.Client.modify_vpc_attribute(
            VpcId=self.ID, 
            EnableDnsSupport={'Value': True})
        

    def EnableDnsHostnames(self):
        '''👉️ Enables DNS hostnames.'''
        LOG.Print('@', self)

        self.Client.modify_vpc_attribute(
            VpcId=self.ID, 
            EnableDnsHostnames={'Value': True})
        

    # ------------------------
    # Delete
    # ------------------------

    def _Delete(self):
        '''👉️ Deletes the VPC.'''
        LOG.Print('@', self)

        try: 

            LOG.Print('@ Unmap public address from the VPCs subnets.')
            network_interfaces = self.Client.describe_network_interfaces(
                Filters=[{
                    'Name': 'vpc-id', 
                    'Values': [self.ID]}])
            network_interface_ids = [
                ni['NetworkInterfaceId'] 
                for ni in network_interfaces['NetworkInterfaces']]
            eips = self.Client.describe_addresses(
                Filters=[{
                    'Name': 'network-interface-id', 
                    'Values': network_interface_ids}])

            for eip in eips['Addresses']:
                if 'AllocationId' in eip:
                    #self.Client.release_address(AllocationId=eip['AllocationId'])
                    pass
                elif 'PublicIp' in eip:
                    self.Client.release_address(PublicIp=eip['PublicIp'])
                
            LOG.Print('@: Handle ENIs')
            enis_with_public_ips = self._get_enis_with_public_ips()
            if enis_with_public_ips:
                self._disassociate_release_elastic_ips_from_enis(enis_with_public_ips)

            LOG.Print('@: Handle NAT Gateways')
            for nat in self.GetNatGateways():
                nat.Delete()

            LOG.Print('@: Handle Load Balancers')
            for lb in self.GetLoadBalancers():
                lb.Delete()

            LOG.Print('@ Delete the security groups')
            self.DeleteSecurityGroups()

            LOG.Print('@ Delete the subnets')
            for subnet in self.GetSubnets():
                subnet.Delete()

            LOG.Print('@ Delete the route tables after the subnets are deleted.')
            for rt in self.Vpc.route_tables.all():
                is_main = any([assoc.main for assoc in rt.associations])
                if not is_main:
                    rt.delete()

            LOG.Print('@ Delete the internet gateway')
            if self.InternetGateway:
                self.InternetGateway.DetachFromVPC()
                self.InternetGateway.Delete()

            LOG.Print('@ Delete the VPC')
            @RetryWithBackoff(maxRetries=5, initialDelay=0.1, codes=['DependencyViolation'])
            def delete_vpc():
                self.Client.delete_vpc(VpcId=self.ID)


            delete_vpc()
        except Exception as e:
            if 'DependencyViolation' in str(e):
                dependencies = self.GetDependencies()
                dependencies = STRUCT(dependencies)
                LOG.Print(dependencies)
            raise
            

    def _get_enis_with_public_ips(self):
        ec2_client = self.Client
        vpc_id = self.ID

        try:
            enis = ec2_client.describe_network_interfaces(
                Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}]
            ).get('NetworkInterfaces', [])
            
            enis_with_public_ips = []
            for eni in enis:
                if 'Association' in eni and 'PublicIp' in eni['Association']:
                    enis_with_public_ips.append(eni)
            return enis_with_public_ips
        except ClientError as e:
            print(f"Error getting ENIs with public IPs: {e}")
            return []
        
    def _disassociate_release_elastic_ips_from_enis(self, enis):
        for eni in enis:
            if 'Association' in eni and 'PublicIp' in eni['Association']:
                if 'AllocationId' in eni['Association']:
                    allocation_id = eni['Association']['AllocationId']
                    association_id = eni['Association']['AssociationId']
                    self.Client.disassociate_address(AssociationId=association_id)
                    self.Client.release_address(AllocationId=allocation_id)
                    print(f"Disassociated and released Elastic IP: {eni['Association']['PublicIp']}")
                else:
                    print(f"ENI {eni['NetworkInterfaceId']} has a public IP {eni['Association']['PublicIp']} but no allocation ID. It might be an automatically assigned public IP.")
                    

    def GetDependencies(self):

        vpc_id = self.ID
        ec2 = self.Client
        dependencies = {}

        # List Subnets
        dependencies['Subnets'] = [
            f'{subnet.ID}|{subnet.Name}' for subnet in self.GetSubnets() ]
        
        # List Network Interfaces
        network_interfaces = ec2.describe_network_interfaces(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['NetworkInterfaces']
        if network_interfaces:
            dependencies['NetworkInterfaces'] = [
                ni['NetworkInterfaceId'] 
                for ni in network_interfaces]

        # List Route Tables
        route_tables = ec2.describe_route_tables(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        if route_tables:
            dependencies['RouteTables'] = [
                rt['RouteTableId'] 
                for rt in route_tables]

        # List Internet Gateways
        dependencies['InternetGateways'] = [
            ig.ID for ig in self.GetInternetGateways() ]

        # List NAT Gateways
        dependencies['NatGateways'] = [
            ng.ID for ng in self.GetNatGateways() ]

        # List VPN Connections
        vpn_connections = ec2.describe_vpn_connections(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['VpnConnections']
        if vpn_connections:
            dependencies['VpnConnections'] = [
                vc['VpnConnectionId'] 
                for vc in vpn_connections]

        # List Security Groups
        dependencies['SecurityGroups'] = [
            sg.ID for sg in self.GetSecurityGroups() ]            

        # List VPC Peering Connections
        vpc_peering_connections = ec2.describe_vpc_peering_connections(
            Filters=[{'Name': 'requester-vpc-info.vpc-id', 'Values': [vpc_id]}])['VpcPeeringConnections']
        if vpc_peering_connections:
            dependencies['VpcPeeringConnections'] = [
                vpc['VpcPeeringConnectionId'] 
                for vpc in vpc_peering_connections]

        # List Endpoints
        endpoints = ec2.describe_vpc_endpoints(
            Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['VpcEndpoints']
        if endpoints:
            dependencies['VpcEndpoints'] = [
                ep['VpcEndpointId'] 
                for ep in endpoints]
            
        # List load balancers
        dependencies['LoadBalancers'] = [
            lb.Name for lb in self.GetLoadBalancers() ]

        return dependencies


    # ------------------------
    # NAT Gateway
    # ------------------------

    def GetNatGateways(self):
        '''👉️ Returns the NAT gateways.'''
        return VPC_NATGW.GetNatGateways(self)

    def DeleteNatGWs(self):
        '''👉️ Deletes the NAT gateways.'''
        VPC_NATGW.DeleteNatGWs(self)


    # ------------------------
    # Subnets
    # ------------------------

    def CreateSubnets(self, prefix:str):
        '''👉️ Creates subnets.'''
        VPC_SUBNET.CreateSubnets(vpc=self, prefix=prefix)

    def CreateSubnet(self, 
        cidr_block:str,             # e.g. 10.0.0.0/24
        availability_zone:str,      # e.g. us-east-1a
        visibility:str='isolated'   # public, private, or isolated
    ):
        '''👉️ Creates a new subnet.'''
        return VPC_SUBNET.CreateSubnet(
            vpc= self,
            cidr_block= cidr_block,
            availability_zone= availability_zone,
            visibility= visibility)

    def GetSubnets(self):
        '''👉️ Lists the subnets.'''
        return VPC_SUBNET.GetSubnets(self)

    def GetPublicSubnets(self):
        '''👉️ Returns the public subnets.'''
        return VPC_SUBNET.GetPublicSubnets(self)
    
    
    # ------------------------
    # Security Groups
    # ------------------------

    def GetSecurityGroups(self):
        '''👉️ Returns the security groups.'''
        return VPC_SECURITYGRP.GetSecurityGroups(vpc= self)
    
    def GetPublicSecurityGroup(self):
        '''👉️ Returns the public security group.'''
        return VPC_SECURITYGRP.GetPublicSecurityGroup(vpc= self)
    
    def CreateSecurityGroup(self, name:str):
        '''👉️ Creates a security group.'''
        return VPC_SECURITYGRP.CreateSecurityGroup(vpc=self, name=name)
    
    def CreatePublicSecurityGroup(self):
        '''👉️ Creates a public security group.'''
        return VPC_SECURITYGRP.CreatePublicSecurityGroup(vpc= self)

    def DeleteSecurityGroups(self):
        '''👉️ Deletes the security groups.'''
        VPC_SECURITYGRP.DeleteSecurityGroups(vpc= self)
    

    # ------------------------
    # Load Balancers
    # ------------------------

    def GetLoadBalancers(self):
        '''👉️ Returns the load balancers.'''
        return VPC_ELB.GetLoadBalancers(vpc= self)

    def CreateLoadBalancer(self, 
        name:str, 
        subnets:list[VPC_SUBNET], 
        securityGroups:list[VPC_SECURITYGRP]
    ):
        '''👉️ Creates a load balancer.'''
        return VPC_ELB.CreateLoadBalancer(
            vpc= self,
            name= name,
            subnets= subnets,
            securityGroups= securityGroups)
        
    def CreatePublicLoadBalancer(self, 
        name:str = None
    ):
        '''👉️ Creates a public load balancer.'''
        LOG.Print('@', self)

        if name is None:
            name = self.Name + '-elb'

        public_subnets = self.GetPublicSubnets()
        
        public_security_group = self.GetPublicSecurityGroup()

        self.CreateLoadBalancer(
            name= name,
            subnets= public_subnets,
            securityGroups= [ public_security_group ])

    
    # ------------------------
    # Internet Gateway
    # ------------------------
    
    def EnableInternet(self):
        '''👉️ Enables internet access.'''
        return VPC_INTERNETGW.CreateInternetGateway(self)
    
    def GetInternetGateways(self):
        '''👉️ Returns the internet gateways.'''
        return VPC_INTERNETGW.GetInternetGateways(self)