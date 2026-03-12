from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RETRY import RetryWithBackoff
from LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS


class ACM_CERTIFICATE(AWS_RESOURCE_ITEM):
    '''👉️ Represents a certificate.'''
    
    ICON = '🔑'


    def __init__(self, 
        pool,
        client,
        meta:dict
    ) -> None:
        LOG.Print('@')

        struct = STRUCT(meta)

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool, 
            client= client,
            arn= struct.RequireStr('CertificateArn'),
            name= struct.RequireStr('DomainName'))
        
        assert self.Arn.startswith('arn:aws:acm:')

    
    def IsRegional(self):
        '''👉️ Check if the certificate is regional.'''
        return not self.IsGlobal()


    def EnsureRegional(self):
        '''👉️ Ensure the certificate is regional.'''
        if not self.IsRegional():
            LOG.RaiseException('@ The certificate must be regional.')


    def EnsureGlobal(self):
        '''👉️ Ensure the certificate is global.'''
        if not self.IsGlobal():
            LOG.RaiseException('@ The certificate must be global.')  


    def IsGlobal(self):
        '''👉️ Check if the certificate is global.'''
        return self.Arn.startswith('arn:aws:acm:us-east-1:')


    @RetryWithBackoff(codes=['ResourceInUseException'])
    def _Delete(self):
        '''👉️ Delete the certificate.'''
        LOG.Print('@', self)
        
        try:    
            ret = self.Client.delete_certificate(
                CertificateArn= self.Arn)
            
        except self.Client.exceptions.ResourceNotFoundException:
            LOG.RaiseValidationException(
                f'@ Certificate {self.Arn} not found.')
        
        # Confirm that it was deleted.
        assert ret['ResponseMetadata']['HTTPStatusCode'] == 200, ret        


    def WaitUntilIssued(self, waitForSeconds: int= 120):
        '''👉️ Wait until the certificate is issued.'''

        timeout =  UTILS.TIME().Later(waitForSeconds)
        
        while True:
            if UTILS.TIME().Now() > timeout:
                LOG.RaiseException(
                    '@ Timeout waiting for certificate issuance.')

            response = self.Client.describe_certificate(
                CertificateArn= self.Arn)
            status = response['Certificate']['Status']
            
            if status == 'ISSUED':
                LOG.Print("@ Certificate has been issued.")
                break

            elif status == 'FAILED':
                LOG.RaiseException("@ Certificate issuance failed.")
            
            else:
                LOG.Print(f"@ Certificate status: {status}. Waiting for issuance...")
                UTILS.TIME().Sleep(seconds=3)
                LOG.Print(f"@ Retrying.")