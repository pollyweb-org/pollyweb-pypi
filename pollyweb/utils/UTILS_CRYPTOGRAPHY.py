# 📚 UTILS

from .LOG import LOG


class UTILS_CRYPTOGRAPHY(): 
    '''👉️ Generic methods to work with cryptography.'''
    

    @classmethod
    def GenerateKeyPair(cls):
        '''👉️ Generates a key pair.
        
        Usage:
        * private, public = UTILS.CRYPTOGRAPHY().GenerateKeyPair()
        '''
        
        # Block if running on AWS.
        from .AWS import AWS 
        if not AWS.LAMBDA().IsLocal():
            LOG.RaiseException('GenerateKeyPair() is only available in a local environment.')

        # Create the private key.
        from .UTILS import UTILS  
        private_pem = 'temp_private.pem'
        public_pem = 'temp_public.pem'
        public_dkim = 'temp_public.dkim'
        
        uuid = f'crypto-{UTILS.UUID()}'
        dir = LOG.GetLogDir().GetSubDir('TEMP').Touch().GetSubDir(uuid).Touch()
        uuid = dir.GetPath()

        UTILS.OS().ExecuteMany([
            f'openssl genrsa -out {uuid}/{private_pem} 2048',
            f'openssl rsa -in {uuid}/{private_pem} -pubout -out {uuid}/{public_pem}',
            f'openssl rsa -in {uuid}/{private_pem} -pubout -outform der 2>/dev/null | openssl base64 -A > {uuid}/{public_dkim}'
        ]) 

        # Read them.
        private_content = dir.GetFile(private_pem).ReadText()
        dkim_content = dir.GetFile(public_dkim).ReadText()
        public_content = dir.GetFile(public_pem).ReadText()
        
        # Cleanup.
        UTILS.OS().ExecuteMany([
            f'rm {uuid}/{private_pem}',
            f'rm {uuid}/{public_pem}',
            f'rm {uuid}/{public_dkim}'
        ])

        dir.Delete(recursive=True)

        # Return them.
        UTILS.RequireArgs([
            public_content, 
            private_content, 
            dkim_content
        ])

        return private_content, public_content, dkim_content