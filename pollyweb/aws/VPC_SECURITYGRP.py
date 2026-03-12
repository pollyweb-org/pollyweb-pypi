from LOG import LOG
from PW_UTILS.STRUCT import STRUCT


class VPC_SECURITYGRP:

    ICON = '🌐'


    def __init__(self,
        meta:dict,
        client:object,
        vpc:object
    ) -> None:
        
        meta:STRUCT = STRUCT(meta)
        
        self.Client = client
        self.Vpc = vpc
        self.Meta = meta
        
        self.ID = meta['GroupId']
        '''👉️ The security group ID.'''

        self.Name = meta['GroupName']
        self.Description = meta['Description']
        self.Tags = meta.GetAtt('Tags', default= [])


    def IsPublic(self) -> bool:
        '''👉️ Returns True if the security group is public.'''
        return self.Name.endswith('-Public')
    

    def IsDefault(self) -> bool:
        '''👉️ Returns True if the security group is the default one.'''
        return self.Name == 'default'
    

    def Delete(self):
        '''👉️ Deletes the security group.'''
        LOG.Print('@')
        self.Client.delete_security_group(
            GroupId= self.ID)


    def AllowHttp(self):
        '''👉️ Allows HTTP traffic.'''
        
        self.Client.authorize_security_group_ingress(
            GroupId= self.ID,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        

    @staticmethod
    def GetSecurityGroups(vpc):
        '''👉️ Returns the security groups.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        grps = self.Client.describe_security_groups(
            Filters=[{
                'Name': 'vpc-id', 
                'Values': [self.ID]}
            ])['SecurityGroups']
        
        return [
            VPC_SECURITYGRP(
                meta= grp,
                client= self.Client,
                vpc= self)
            for grp in grps
        ]
    

    @staticmethod
    def GetPublicSecurityGroup(vpc):
        '''👉️ Returns the public security group.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        grps = VPC_SECURITYGRP.GetSecurityGroups(
            vpc= self)
        
        for grp in grps:
            if grp.IsPublic():
                return grp
        
        return None
    

    @staticmethod
    def CreateSecurityGroup(vpc, name:str):
        '''👉️ Creates a security group.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        description = name + ' security group'

        response = self.Client.create_security_group(
            GroupName= name,
            Description= description,
            VpcId= self.ID)
                
        # Add these manually, because the response doesn't contain them.
        response['GroupName'] = name
        response['Description'] = description

        grp = VPC_SECURITYGRP(
            meta= STRUCT(response),
            client= self.Client,
            vpc= self)
        
        return grp
    

    @staticmethod
    def CreatePublicSecurityGroup(vpc):
        '''👉️ Creates a public security group.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        grp = VPC_SECURITYGRP.CreateSecurityGroup(
            vpc= self,
            name= self.Name + '-Public')
        
        grp.AllowHttp()

        return grp
    

    @staticmethod
    def DeleteSecurityGroups(vpc):
        '''👉️ Deletes a VPC's security group.'''
        LOG.Print('@')

        from VPC_NETWORK import VPC_NETWORK
        self:VPC_NETWORK = vpc

        grps = VPC_SECURITYGRP.GetSecurityGroups(
            vpc= self)
        
        for grp in grps:
            if not grp.IsDefault():
                grp.Delete()