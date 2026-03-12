from LOG import LOG


class VPC_NATGW:

    def __init__(self,
        meta:dict,
        client:object,
        vpc:object
    ) -> None:
        
        self.Client = client
        self.Vpc = vpc
        self.Meta = meta
        self.ID = meta['NatGatewayId']
        self.State = meta['State']
        self.SubnetID = meta['SubnetId']
        self.Arn = f'arn:aws:ec2::natgateway/{self.ID}'

    
    def IsPending(self) -> bool:
        '''👉️ Returns True if the NAT gateway is pending.'''
        return self.State == 'pending'
    

    def WaitForReady(self):
        LOG.Print(f"@: Waiting for NAT Gateway {self.ID} to become available.")
        self.Client.get_waiter('nat_gateway_available').wait(
            NatGatewayIds=[self.ID])
        

    def Delete(self):
        '''👉️ Deletes the NAT gateway.'''
        LOG.Print('@', self)
        
        self.Client.delete_nat_gateway(NatGatewayId=self.ID)

        LOG.Print('@ Wait for the NAT gateways to be deleted.')
        self.Client.get_waiter('nat_gateway_deleted').wait(
            NatGatewayIds=[self.ID])
        
        self.State = 'deleted'


    @staticmethod
    def GetNatGateways(vpc):

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        nat_gateways = self.Client.describe_nat_gateways(
            Filter=[{
                'Name': 'vpc-id', 
                'Values': [self.ID]
            }]
        ).get('NatGateways', [])        
                
        twins:list[VPC_NATGW] = []
        for nat in nat_gateways:
            twin = VPC_NATGW(
                meta= nat)
            twins.append(twin)

        # Wait for pending NAT Gateways to become available
        for twin in twins:
            if twin.IsPending():
                twin.WaitForReady()
        
        return twins
    

    @staticmethod
    def DeleteNatGWs(vpc):
        '''👉️ Deletes the NAT gateways.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        for nat in self.GetNatGateways():
            nat.Delete()