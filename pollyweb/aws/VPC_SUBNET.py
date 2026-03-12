from AWS_RETRY import RetryWithBackoff
from LOG import LOG


class VPC_SUBNET:

    ICON = '🌐'
    

    def __init__(self, meta:dict, client):
        self.Client = client
        self.Meta = meta
        self.ID = meta['SubnetId']
        self.CIDR = meta['CidrBlock']
        self.State = meta['State']
        self.AvailabilityZone = meta['AvailabilityZone']
        self.VpcID = meta['VpcId']
        self.Arn = f'arn:aws:ec2:{client.meta.region_name}::subnet/{self.ID}'
        self.Tags = {tag['Key']: tag['Value'] for tag in meta.get('Tags', [])}
        self.Name = self.Tags.get('Name', self.ID)
        self.Available = self.State == 'available'
        self.Unavailable = not self.Available

        LOG.Print(f'@: name={self.Name}', self)


    @RetryWithBackoff(maxRetries=5, initialDelay=0.1)
    def Delete(self):
        '''👉️ Deletes the subnet.'''
        LOG.Print('@', self)

        self.Client.delete_subnet(SubnetId=self.ID)
        self.Available = False
        self.Unavailable = True


    def IsPublic(self) -> bool:
        '''👉️ Returns True if the subnet is public.'''
        return self.Tags.get('Public', 'false').lower() == 'true'
    

    @staticmethod
    def GetSubnets(vpc):
        '''👉️ Lists the subnets.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        response = self.Client.describe_subnets(
            Filters=[{'Name': 'vpc-id', 'Values': [self.ID]}])
        return [
            VPC_SUBNET(meta, self.Client) 
            for meta in response['Subnets']
        ]


    @staticmethod
    def GetPublicSubnets(vpc):
        '''👉️ Returns the public subnets.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        return [
            subnet
            for subnet in self.GetSubnets()
            if subnet.IsPublic()
        ]
    

    @staticmethod
    def CreateSubnet(vpc, 
        cidr_block:str,             # e.g. 10.0.0.0/24
        availability_zone:str,      # e.g. us-east-1a
        visibility:str='isolated'   # public, private, or isolated
    ):
        '''👉️ Creates a new subnet.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        response = self.Client.create_subnet(
            VpcId= self.ID,
            CidrBlock= cidr_block,
            AvailabilityZone= availability_zone)
        
        subnet = VPC_SUBNET(
            meta= response['Subnet'], 
            client= self.Client)
        
        LOG.Print('@: Tag the subnet')
        self.Tag(
            resource= subnet.ID,
            tags= dict(
                Name= f'{self.Name}-{availability_zone[-1]}-{visibility}',
                AZ= availability_zone[-1], # 'a', 'b', 'c', etc.
                Visibility= visibility,
                Public= 'true' if visibility == 'public' else 'false'))
        
        # If public, associate with route table for internet access
        if visibility == 'public':

            LOG.Print('@: Create a route table and associate it with the subnet')
            route_table = self.Client.create_route_table(
                VpcId = self.ID)
            route_table_id = route_table['RouteTable']['RouteTableId']

            self.Tag(
                resource= route_table_id,
                tags= dict(
                    Name= f'{self.Name}-{availability_zone[-1]}-{visibility}',
                    Visibility= visibility,
                    Public= 'true' if visibility == 'public' else 'false',
                    AZ= availability_zone[-1]))

            LOG.Print('@: Create a route to the internet gateway')
            self.Client.create_route(
                RouteTableId= route_table_id,
                DestinationCidrBlock= '0.0.0.0/0',
                GatewayId= self.InternetGateway.ID)
            
            LOG.Print('@: Associate the route table with the subnet')
            self.Client.associate_route_table(
                RouteTableId= route_table_id,
                SubnetId= subnet.ID)

        elif visibility == 'private':

            # Implement NAT Gateway for each private subnet 
            # or share one NAT Gateway across private subnets in different AZs
            
            LOG.Print('@: Allocate an Elastic IP for NAT Gateway')
            eip_response = self.Client.allocate_address(Domain='vpc')
            eip_allocation_id = eip_response['AllocationId']
            
            LOG.Print('@: Create a NAT Gateway')
            nat_gateway = self.Client.create_nat_gateway(
                SubnetId= subnet.ID, 
                AllocationId= eip_allocation_id)
            nat_gateway_id = nat_gateway['NatGateway']['NatGatewayId']
            
            LOG.Print('@: Wait for the NAT Gateway to become available.', self)
            self.Client.get_waiter('nat_gateway_available').wait(
                NatGatewayIds=[nat_gateway_id])

            LOG.Print('@: Create a private route table')
            private_route_table = self.Vpc.create_route_table()

            LOG.Print('@: Create a route to the NAT Gateway')
            private_route_table.create_route(
                DestinationCidrBlock= '0.0.0.0/0',
                NatGatewayId= nat_gateway_id)
            
            LOG.Print('@: Associate the route table with the subnet')
            private_route_table.associate_with_subnet(
                SubnetId= subnet.ID)

        return subnet


    @staticmethod
    def CreateSubnets(vpc, prefix:str):
        '''👉️ Creates subnets for a VPC.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        region = self.Client.meta.region_name

        self.CreateSubnet(
            cidr_block= f'{prefix}.11.0/24', 
            availability_zone= f'{region}a',
            visibility= 'public')
        
        self.CreateSubnet(
            cidr_block= f'{prefix}.12.0/24', 
            availability_zone= f'{region}a',
            visibility= 'isolated')

        self.CreateSubnet(
            cidr_block= f'{prefix}.21.0/24', 
            availability_zone= f'{region}b',
            visibility= 'public')
                
        self.CreateSubnet(
            cidr_block= f'{prefix}.22.0/24', 
            availability_zone= f'{region}b',
            visibility= 'isolated')