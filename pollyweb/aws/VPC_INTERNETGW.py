from LOG import LOG


class VPC_INTERNETGW:

    ICON = '🌐'
    

    def __init__(self, 
        meta:dict, 
        client, 
        resource,
        vpc
    ):
        LOG.Print('@', self)

        from VPC_NETWORK import VPC_NETWORK
        vpc:VPC_NETWORK = vpc

        self.Client = client
        self.Resource = resource
        self.Meta = meta
        self.ID = meta['InternetGatewayId']
        attachments = meta['Attachments']
        self.State = attachments[0]['State'] if attachments else 'detached'

        self.VpcID = attachments[0]['VpcId'] if attachments else None
        if not self.VpcID:
            self.VpcID = vpc.ID

        self.Arn = f'arn:aws:ec2:{client.meta.region_name}::internet-gateway/{self.ID}'
        self.Tags = {tag['Key']: tag['Value'] for tag in meta.get('Tags', [])}
        self.Name = self.Tags.get('Name', self.ID)

        self.Vpc:VPC_NETWORK = vpc
        

    def InheritTags(self):
        '''👉️ Inherits tags from the VPC.'''
        LOG.Print('@', self)
        LOG.Print(f'@: VPC tags={self.Vpc.TagDictionary}')
        self.Vpc.Tag(
            tags= self.Vpc.TagDictionary,
            resource= self.ID)


    def DetachFromVPC(self):
        '''👉️ Detaches the internet gateway from a VPC.'''
        LOG.Print('@', self)

        # Detach the internet gateway from the VPC.
        self.Client.detach_internet_gateway(
            InternetGatewayId= self.ID, 
            VpcId= self.VpcID)


    def Delete(self):
        '''👉️ Deletes the internet gateway.'''
        LOG.Print('@', self)
        
        self.Client.delete_internet_gateway(
            InternetGatewayId=self.ID)
        

    @staticmethod
    def CreateInternetGateway(vpc):
        '''👉️ Creates an internet gateway.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        # Create the internet gateway on AWS.
        response = self.Client.create_internet_gateway()
        meta = response['InternetGateway']

        # Create the internet gateway twin.
        igw = VPC_INTERNETGW(
            meta= meta, 
            client= self.Client, 
            resource= self.Resource,
            vpc= self)
        
        # Copy the tags from the VPC.
        igw.InheritTags()

        self.InternetGateway = igw

        self.Client.attach_internet_gateway(
            InternetGatewayId= self.InternetGateway.ID, 
            VpcId= self.ID)
        
        return igw
    

    @staticmethod
    def GetInternetGateways(vpc):
        '''👉️ Lists the internet gateways in a VPC.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        response = self.Client.describe_internet_gateways()
        return [ 
            VPC_INTERNETGW(
                meta= igw, 
                client= self.Client, 
                resource= self.Resource,
                vpc= self) 
            for igw in response['InternetGateways'] 
            if self.ID in igw['Attachments'][0]['VpcId'] 
        ]