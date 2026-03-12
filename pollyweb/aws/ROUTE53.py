# 📚 ROUTE53

import boto3
import urllib.parse

from LOG import LOG
from PW_UTILS.UTILS import UTILS
from PW_UTILS.STRUCT import STRUCT

r53 = boto3.client('route53')

class ROUTE53:
    

    def __init__(self, hosted_zone_id:str = None):
        '''👉 Initialize the class with the hosted zone ID.'''
        LOG.Print(f' ROUTE53().__init__()')

        # Check the arguments
        UTILS.AssertStrings([hosted_zone_id])

        # Set the hosted zone ID
        if hosted_zone_id:
           self._hosted_zone_id = hosted_zone_id
           '''👉️ The ID of the hosted zone'''
        

    def RecordExists(self, name:str, type:str):
        '''👉 Check if a record exists in the hosted zone.
        
        Exemple: 
            name: dev.nlweb.org.
            type: A
        '''

        LOG.Print(
            f' ROUTE53.RecordExists()', 
            f'{name=}', f'{type=}')
        
        # Check the arguments
        UTILS.AssertStrings([name, type], require= True)
        UTILS.AssertIsAnyValue(type, ['A', 'NS', 'TXT'])

        # Get the list of records
        result = r53.list_resource_record_sets(
            HostedZoneId= self._hosted_zone_id)
        
        # Check if the record exists
        for r in result["ResourceRecordSets"]:
            record_name = r["Name"]
            record_type = r["Type"]
            if record_name == name and record_type == type:
                # Found the record
                return True
                
        # Record not found
        return False


    def GetNsRecord(self) -> STRUCT:
        '''👉 Get the NS record for the hosted zone.
        * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53.html#Route53.Client.list_resource_record_sets
        
        Example: 
            Name: ns-2048.awsdns-64.com.
            Type: NS
            TTL: 172800
            ResourceRecords: [
                {'Value': 'ns-2048.awsdns-64.com.'}, 
                {'Value': 'ns-2047.awsdns-63.net.'}, 
                {'Value': 'ns-2046.awsdns-62.org.'}, 
                {'Value': 'ns-2045.awsdns-61.co.uk.'}
            ]
        '''
        LOG.Print(f' ROUTE53.GetNsRecord()')

        # Get the list of records
        result= r53.list_resource_record_sets(
            HostedZoneId=self._hosted_zone_id)
        
        # Check if the record exists
        for r in result["ResourceRecordSets"]:
            if r["Type"] == 'NS':
                LOG.Print(f' ROUTE53.GetNsRecord().Return: {r=}')
                return STRUCT(r)
                
        # Record not found
        LOG.RaiseException('No record NS found')
    

    def GetDomainName(self):
        '''👉 Get the domain name from the NS record.'''

        print(f'ROUTE53.Domain()')
        ns = self.GetNsRecord()
        return ns.RequireStr('Name')
    

    def GetNameServerList(self):
        '''👉 Get the list of name servers from the NS record.'''

        print(f'ROUTE53.NameServers()')
        ns = self.GetNsRecord()
        servers = []
        for s in ns.RequireStructs('ResourceRecords'):
            name = s.RequireStr('Value')
            servers.append(name)
        return servers
    

    def GetNameServers(self):
        '''👉 Get the list of name servers from the NS record as a comma separated string.
        * Returns: ns-2048.awsdns-64.com., ns-2047.awsdns-63.net., ns-2046.awsdns-62.org.'''

        print(f'ROUTE53.NameServerList()')
        servers = self.GetNameServerList()
        serverList = ','.join(servers)
        return serverList

        
    def GetDnsSec(self, unquoted=False) -> str:
        '''👉 Get the DNSSEC key for the hosted zone.

        Arguments:
         * unquoted: If True, return the key as a string without quotes.

        References:
         * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53/client/get_dnssec.html#            
         * https://docs.aws.amazon.com/Route53/latest/APIReference/API_GetDNSSEC.html
         * https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec-enable-signing.html
        '''

        LOG.Print(f' ROUTE53.GetDnsSec({unquoted=})')
        
        # Check the arguments
        UTILS.AssertIsBool(unquoted, require= True)

        # Get the DNSSEC key
        resp = r53.get_dnssec(
            HostedZoneId = self._hosted_zone_id)
        LOG.Print(f' ROUTE53.GetDnsSec.get_dnssec:', resp)

        # Extract the DSRecord from the response
        ret = resp['KeySigningKeys'][0]['DSRecord']
        LOG.Print(f' ROUTE53.GetDnsSec.DSRecord: {ret}')

        # Convert to quoted string
        if not unquoted:
            ret = urllib.parse.quote_plus(ret)

        # Return the key
        UTILS.RequireString(ret)
        return ret
        

    def AddNameServers(self, 
        name:str, 
        servers: list[str],
        override:bool= False, 
        safe:bool= False
    ):
        '''👉 Add a list of name servers to the hosted zone.
        
        Arguments:
            * `child`: The child domain name.
            * `servers`: The list of name servers for the child domain.
            * `override`: If True, override the NS record if it exists.
            * `safe`: If True, ignore the NS record if it exists.
        '''

        LOG.Print(
            f' ROUTE53.AddChildDomain()', 
            f'{name=}', f'{servers=}')
        
        # Check the arguments
        UTILS.RequireString(name)
        UTILS.RequireList(servers)
        UTILS.AssertIsBool(override)
        UTILS.AssertIsBool(safe)   

        # Check if the NS record exists
        if not override:
            exists = self.RecordExists(name, 'NS')
            if exists:
                if safe:
                    LOG.Print(f'NS record exists, ignoring for security.')
                    return { 'e': 'NS record exists, ignoring for security.' }
                else:
                    LOG.RaiseException(f'NS record exists, ignoring for security.')

        # Add the NS record
        self.AddRecord(
            type= 'NS', 
            name= name, 
            value= [{'Value': ns} for ns in servers])


    def AddDnsSec(self, 
        name:str, 
        dnssec:str, 
        overide:bool= False, 
        safe:bool= False
    ):
        '''👉 Add a DS (DnsSec) record to the hosted zone.
        
        Arguments:
            * `name`: The domain name to add the DS record to.
            * `dnssec`: The DS record to add.
                e.g.: '11328 13 2 4D88A5CC7A1F21A86AD9A06A058D4EEC16224C4978F07193E2F14519962C4EBA'
            * `override`: If True, override the DS record if it exists.
            * `safe`: If True, ignore the DS record if it exists.

        References: 
            * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/route53domains/client/associate_delegation_signer_to_domain.html
            * https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_DnssecSigningAttributes.
            * https://github.com/hashicorp/terraform-provider-aws/issues/28749
            * https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring-dnssec-enable-signing.html
            * https://dnssec-analyzer.verisignlabs.com/dev.nlweb.org
            * https://dnssec-analyzer.verisignlabs.com/nlweb.org
            * https://www.performancemagic.com/route-53-dnssec/
            * https://dnsviz.net/d/dev.nlweb.org/dnssec/
        '''
        
        LOG.Print(
            f' ROUTE53.AddDnsSec()', 
            f'{name=}', f'{overide=}', f'{safe=}', f'{dnssec=}')
        
        # Check the arguments
        UTILS.RequireStrings([name, dnssec])
        UTILS.AssertIsBool(overide)
        UTILS.AssertIsBool(safe)

        # Check if the DS record exists
        if not overide:
            exists = self.RecordExists(name, 'DS')
            if exists:
                if safe:
                    LOG.Print(f'DS record exists, ignoring for security.')
                    return { 'e': 'DS record exists, ignoring for security.' }
                else:
                    LOG.RaiseException(f'DS record exists, ignoring for security.')

        # Add the DS record
        self.AddRecord(
            type= 'DS', 
            name= name, 
            value= [{'Value': dnssec}])


    def AddRecord(self, type:str, name:str, value:any):
        '''👉 Add a record to the hosted zone.'''
        # https://stackoverflow.com/questions/38554754/cant-update-dns-record-on-route-53-using-boto3
                
        LOG.Print(
            f' ROUTE53.AddRecord()', 
            f'{type=}', f'{name=}', f'{value=}')
        
        # Check the arguments
        UTILS.AssertIsAnyValue(type, ['A', 'NS', 'TXT'])
        UTILS.AssertStrings([name])
        UTILS.Require(value)

        # Add the record
        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": name,
                    "Type": type,
                    "TTL": 60,
                    "ResourceRecords": value,
                }
            },
        ]

        LOG.Print(f' ROUTE53.AddRecord.adding:', changes)
        
        r53.change_resource_record_sets(
            HostedZoneId= self._hosted_zone_id,
            ChangeBatch={
                "Comment": "Automatic DNS update",
                "Changes": changes
            })


    def AddTxtRecord(self, name:str, value:str):
        '''👉 Add a TXT record to the hosted zone.

        Arguments:
            * `name`: The domain name to add the TXT record to.
            * `value`: The value of the TXT record.

        References:
            * https://stackoverflow.com/questions/38554754/cant-update-dns-record-on-route-53-using-boto3 
        '''

        LOG.Print(
            f' ROUTE53.AddTxtRecord()', 
            f'{name=}', f'{value=}')
        
        # Check the arguments
        UTILS.AssertStrings([name, value], require= True)
        
        # Add the record
        self.AddRecord(
            type= 'TXT', 
            name= name, 
            value= { "Value": value })
        

    def AddApiGW(self, customDomain:str, apiHostedZoneId:str, apiAlias:str):
        '''👉 Add an API Gateway custom domain to the hosted zone.
        
        Arguments:
         * `customDomain`: The custom domain name.
         * `apiHostedZoneId`: The hosted zone ID for the API Gateway.
         * `apiAlias`: The alias for the API Gateway.
        '''
        
        LOG.Print(
            f' ROUTE53.AddApiGW()', 
            f'{customDomain=}', f'{apiHostedZoneId=}', f'{apiAlias=}')

        # Check the arguments
        UTILS.RequireStrings([customDomain, apiHostedZoneId, apiAlias])

        # Add the record
        changes = [
            {
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": customDomain,
                    "Type": 'A',
                    'AliasTarget': {
                        'HostedZoneId': apiHostedZoneId,
                        'DNSName': apiAlias,
                        'EvaluateTargetHealth': True
                    }
                }
            },
        ]
        print(f'{changes=}')
        
        r53.change_resource_record_sets(
            HostedZoneId = self._hosted_zone_id,
            ChangeBatch = {
                "Comment": 'API Gateway custom domain',
                "Changes": changes
            })
        
    
    @staticmethod
    def GetHostedZones():
        '''👉 Get a list of hosted zones.

        References:
        * https://docs.aws.amazon.com/fr_fr/ses/latest/dg/example_ses_Scenario_ReplicateIdentities_section.html
        '''
        
        zones = []
        zone_paginator = r53.get_paginator('list_hosted_zones')
        zone_iterator = zone_paginator.paginate(PaginationConfig={'PageSize': 20})
        zones = [
            zone for zone_page in zone_iterator for zone in zone_page['HostedZones']]
        LOG.Print("Found %s hosted zones.", len(zones))
        return zones
    

    @classmethod
    def GetHostedZoneID(cls, name:str):
        '''👉 Get the hosted zone ID for a given domain name.
        
        Arguments:
        * `name`: The domain name to find the hosted zone ID for.

        Exceptions: 
        * Zone not found: {name}

        References:
        * https://docs.aws.amazon.com/fr_fr/ses/latest/dg/example_ses_Scenario_ReplicateIdentities_section.html        
        '''

        zones = cls.GetHostedZones()
        LOG.Print(f'zones: {zones}')

        # Check the arguments
        UTILS.RequireString(name)
        
        # Find the zone
        for z in zones:
            if z['Name'] == name:
                return z['Id']
            
        # Zone not found
        LOG.RaiseException('Zone not found: ' + name)


    @classmethod
    def CreateHostedZone(cls,
        domainName:str,
    ):
        '''👉 Create a hosted zone.'''
        
        response = r53.create_hosted_zone(
            Name= domainName,
            CallerReference= UTILS.UUID(),
            HostedZoneConfig={
                'Comment': 'This is my hosted zone for example.com',
                'PrivateZone': False  # Set to True if it's a private hosted zone
            })
        
        '''
        {
            'HostedZone': {
                'Id': '/hostedzone/Z1D633PJN98FT9',
                'Name': 'example.com.',
                'CallerReference': 'unique-string',
                'Config': {
                    'Comment': 'This is my hosted zone for example.com',
                    'PrivateZone': False
                },
                'ResourceRecordSetCount': 2
            },
            'ChangeInfo': {
                'Id': '/change/C1PA6795UKMFR9',
                'Status': 'PENDING',
                'SubmittedAt': '2024-08-15T12:00:00.000Z'
            },
            'DelegationSet': {
                'NameServers': [
                    'ns-2048.awsdns-64.com',
                    'ns-2049.awsdns-65.net',
                    'ns-2050.awsdns-66.org',
                    'ns-2051.awsdns-67.co.uk'
                ]
            },
            'Location': 'https://route53.amazonaws.com/2024-08-15/hostedzone/Z1D633PJN98FT9'
        }
        '''
        
        hosted_zone_id = STRUCT(response).RequireStruct('HostedZone').RequireStr('Id')

        return ROUTE53(
            hosted_zone_id= hosted_zone_id)
            

    def SetUpDnsSec(self, keyArn:str):
        
        # From the KMS key, create a Key Signing Key for the hosted zone.
        response = r53.create_key_signing_key(
            CallerReference= UTILS.UUID(),
            HostedZoneId= self._hosted_zone_id,
            KeyManagementServiceArn= keyArn,
            Name= 'YourKeySigningKeyName',
            Status='ACTIVE')
        
        # Enable DNSSEC for the hosted zone
        response = r53.enable_hosted_zone_dnssec(
            HostedZoneId= self._hosted_zone_id)

        response = r53.get_dnssec(
            HostedZoneId= self._hosted_zone_id)