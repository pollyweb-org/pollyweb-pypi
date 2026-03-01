from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from PW_UTILS.LOG import LOG
from PW_UTILS.UTILS import UTILS
from WAF_WACL import WAF_WACL
from botocore.exceptions import ClientError

import boto3
regionalClient = boto3.client('wafv2')
cloudFrontClient = boto3.client('wafv2', region_name='us-east-1')

class WAF(AWS_RESOURCE_POOL[WAF_WACL]):

    ICON= '🔥'


    @classmethod
    def Ensure(cls, 
        name:str,
        central:bool= False
    ):
        client = cls.GetClient(
            central= central)
        
        return super()._Ensure(
            name= name,
            client= client)
    

    @classmethod
    def GetClient(cls, central:bool):
        '''👉️ Get the right client based on the scope.'''
        
        LOG.Print(f'@: {central=}')

        UTILS.AssertIsBool(central, require=True)

        if central:
            LOG.Print(f'@: returning cloudFrontClient')
            return cloudFrontClient
        else:
            LOG.Print(f'@: returning regionalClient')
            return regionalClient
        

    @classmethod
    def List(cls, 
        client
    ) -> list[WAF_WACL]:
        '''👉️ List all Web ACLs.'''
        LOG.Print(f'@')

        central = client == cloudFrontClient
        scope:str = 'CLOUDFRONT' if central else 'REGIONAL'
        
        # List all Web ACLs
        response = client.list_web_acls(Scope=scope)  

        ret:list[WAF_WACL] = []
        for web_acl in response['WebACLs']:
            item = WAF_WACL(
                pool= cls,
                meta= web_acl,
                central= central,
                client= client)
            ret.append(item)

        return ret

    
    @classmethod
    def Create(cls, 
        name:str,
        client,
    ) -> WAF_WACL:
        '''👉️ Create a Web ACL for CloudFront with AWS Managed Rules'''

        LOG.Print(f'@: {name=}')

        central = client == cloudFrontClient
        scope:str = 'CLOUDFRONT' if central else 'REGIONAL'

        # Define the AWS Managed Rules
        AWSManagedRulesCommonRuleSet = {
            'Name': 'AWS-AWSManagedRulesCommonRuleSet',
            'Priority': 1,
            'Statement': {
                'ManagedRuleGroupStatement': {
                    'VendorName': 'AWS',
                    'Name': 'AWSManagedRulesCommonRuleSet',
                    # Optionally, you can exclude individual rules
                    # 'ExcludedRules': [{'Name': 'RuleToExclude'}]
                }
            },
            'OverrideAction': {'None': {}},  # Specifies that the rule action should be used
            'VisibilityConfig': {
                'SampledRequestsEnabled': True,
                'CloudWatchMetricsEnabled': True,
                'MetricName': 'AWSManagedRulesCommonRuleSet'
            }
        }

        # Create the Web ACL
        try: 
            response = client.create_web_acl(
                Name= name,
                Scope= scope,  
                DefaultAction={
                    'Allow': {}  # or 'Block': {} to set the default action to block
                },
                VisibilityConfig={
                    'SampledRequestsEnabled': True,
                    'CloudWatchMetricsEnabled': True,
                    'MetricName': name
                },
                Description='Description of the Web ACL',
                # Add your rules here (optional)
                Rules=[
                    AWSManagedRulesCommonRuleSet,
                    #AWSManagedRulesOWASP
                ])
        
        except ClientError as e:
            if e.response['Error']['Code'] == 'WAFDuplicateItemException':
                LOG.RaiseException(e, 'Web ACL already exists: ', name)
            else:
                LOG.RaiseException(e)

        except Exception as e:
            LOG.RaiseException(e)

        # Return the Web ACL
        return WAF_WACL(
            meta= response['Summary'],
            pool= cls,
            central= central,
            client= client)
