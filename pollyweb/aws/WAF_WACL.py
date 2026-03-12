from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RETRY import RetryWithBackoff
from LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from AWS import AWS

class WAF_WACL(AWS_RESOURCE_ITEM):
    '''👉️ Digital twin of aWeb ACL.'''

    ICON= '🔥'


    def __init__(self, 
        pool,
        meta:dict, 
        central:bool,
        client
    ) -> None:
        '''👉️ Initialize the Web ACL.'''
        
        struct = STRUCT(meta)
        name = struct.RequireStr('Name')
        id = struct.RequireStr('Id')

        account_id = AWS.STS().GetAccountNumber()
        if central:
            arn = f"arn:aws:wafv2:us-east-1:{account_id}:global/webacl/{name}/{id}"
        else:
            region = AWS.STS().GetRegion()
            arn = f"arn:aws:wafv2:{region}:{account_id}:regional/webacl/{name}/{id}"

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool, 
            client= client,
            arn= arn,
            name= name)
        
        self.Scope:str = 'CLOUDFRONT' if central else 'REGIONAL'
        self.ID:str = id
        

    def IsRegional(self):
        '''👉️ Check if the Web ACL is regional.'''
        return not self.IsGlobal()


    def EnsureRegional(self):
        '''👉️ Ensure the certificate is regional.'''
        if not self.IsRegional():
            LOG.RaiseException('@ The Web ACL must be regional.')


    def EnsureGlobal(self):
        '''👉️ Ensure the certificate is global.'''
        if not self.IsGlobal():
            LOG.RaiseException('@ The Web ACL must be global.')  


    def IsGlobal(self):
        '''👉️ Check if the Web ACL is global.'''
        return self.Arn.startswith('arn:aws:wafv2:us-east-1:')


    @RetryWithBackoff(codes=['ResourceInUseException'])
    def _Delete(self):
        '''👉️ Delete the Web ACL.'''
        LOG.Print(f'@', self)
                
        # To delete a Web ACL, you first need to retrieve its lock token
        web_acl = self.Client.get_web_acl(
            Name= self.Name, 
            Id= self.ID, 
            Scope= self.Scope)
        
        lock_token = web_acl['LockToken']

        # Delete the Web ACL
        self.Client.delete_web_acl(
            Id= self.ID, 
            Name= self.Name, 
            Scope= self.Scope, 
            LockToken= lock_token)
               

    @RetryWithBackoff(maxRetries=2, initialDelay=0.1, codes=['WAFUnavailableEntityException'])
    def AssociateResource(self, arn:str):
        '''👉️ Associate a resource with the Web ACL.'''
        LOG.Print(f'@', self)
       
        response = self.Client.associate_web_acl(
            WebACLArn= self.Arn,
            ResourceArn= arn)
        
        return response