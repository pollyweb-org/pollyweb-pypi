# 📚 DOMAIN

import os
from typing import Optional
from PW_AWS.DEPLOYER_EXEC_PYTHON import DEPLOYER_EXEC_PYTHON
from PW_AWS.DEPLOYER_TASK import DEPLOYER_TASK
from pollyweb import LOG

from PW_DOMAIN import MANIFEST, ManifestNotAvailableException
from ACTOR import ACTOR
from pollyweb import UTILS
from PW_AWS.AWS import AWS
from PW import PW


class DOMAIN(ACTOR):
    ''' 👥 Wrapper of a domain. 
    * Docs: https://quip.com/lcSaAX7AiEXL/-Domain
    * Usage: DOMAIN('any-domain.com')
    '''
        
    def __init__(self, domain:str=None):
        UTILS.AssertIsType(domain, str)

        self._domain = domain
        self._manifest:MANIFEST = None
        self._yaml = None
        self._google = None
    

    def DomainName(self):
        '''👉 Returns the name of the current domain.'''
        ret = self._domain
        UTILS.AssertStrings([ret], require=True)
        return ret
    

    def HasManifest(self) -> bool:
        '''👉 Checks if the domain has a manifest.'''
        return self._manifest != None


    def Manifest(self) -> MANIFEST:
        '''👉 Returns the domain's manifest.'''
        ret = self._manifest
        UTILS.AssertIsType(ret, MANIFEST, require=True)   
        return ret


    def _SetManifest(self, manifest:MANIFEST):
        '''👉 Safely sets the domain's manifest.'''
        UTILS.AssertIsType(manifest, MANIFEST, require=True)
        self._manifest = manifest


    def Parse(self, folder:str):
        '''👉 Parses the domain's configuration from a local folder.'''
        LOG.Print('🌐 DOMAIN.Parse(folder)', f'{folder=}')

        UTILS.AssertStrings([folder], require=True)

        # Parse the configuration.
        from PW_DOMAIN import DOMAIN_PARSER
        config = DOMAIN_PARSER().ParseDomain(
            domain= self.DomainName(), 
            folder= folder)
        
        # Store in memory.
        manifest = config.RequireManifest(
            domain=self.DomainName())
        self._SetManifest(
            manifest= manifest)
        self._config = config

        # Return the config.
        return config


    def Deploy(self):
        '''👉 Deploys the domain's configuration.'''
        LOG.Print('🌐 DOMAIN.Deploy()')

        from DOMAIN_DEPLOY import DOMAIN_DEPLOY
        DOMAIN_DEPLOY().Deploy(
            config= self._config)


    def Endpoint(self, path='') -> str:
        '''👉 Returns the domain's API endpoint.'''
        return f'https://pollyweb.{self.DomainName()}/{path}'


    def GetManifest(self) -> MANIFEST:
        ''' 👉 Fetches the manifest on the domains endpoint, and returns as an object.'''
        LOG.Print(f'👥 DOMAIN({self.DomainName()}).GetManifest()')

        from WEB import WEB
        from PW_UTILS.WEB_BASE import UrlNotFoundException

        if self.HasManifest():
            return self.Manifest()
        
        if self._yaml != None:
            LOG.Print(f'👥 DOMAIN:', 'YAML already loaded.')

        else:
            LOG.Print(f'👥 DOMAIN:', 'Remote call required.')
            endpoint = self.Endpoint('manifest')
            
            try:
                self._yaml = WEB().HttpGet(endpoint)
            except UrlNotFoundException:
                raise ManifestNotAvailableException(
                    f'Manifest not available for domain=({self.DomainName()})')
            finally:
                pass

        # Read from the file.
        yaml = UTILS.FromYaml(
            text= self._yaml)
        
        # Set in memory.
        self._SetManifest(
            manifest= PW.INTERFACES().MANIFEST(yaml))

        # Check if the manifest is valid.
        self.Manifest().VerifyIdentity(
            expectedDomain= self.DomainName())
    
        # Return the object in memory.
        return self.Manifest()
    

    def GoogleDns(self) -> any:
        '''
        👉️ https://developers.google.com/speed/public-dns/docs/doh
        👉️ https://developers.google.com/speed/public-dns/docs/doh/json
        👉️ https://dns.google/resolve?name=pollyweb._domainkey.38ae4fa0-afc8-41b9-85ca-242fd3b735d2.dev.pollyweb.org&type=TXT&do=1
        '''

        if self._google:
            return self._google
        
        hostname = f'pollyweb._domainkey.{self._domain}'
        url = f'https://dns.google/resolve?name={hostname}&type=TXT&do=1'

        from WEB import WEB
        self._google = WEB().HttpGetJson(url)
        
        return self._google


    def IsDnsSec(self) -> bool:
        resp = self.GoogleDns()
        isDnsSec = (resp['AD'] == True)
        return isDnsSec
    

    def GetDkim(self) -> Optional[str]:
        ''' 👉 Gets the DKIM from the remote GoogleDns API.'''
        resp = self.GoogleDns()

        dkim:Optional[str] = None
        exists = 'Answer' in resp
        if exists:
            for answer in resp['Answer']:
                if answer['type'] == 16:
                    dkim = answer['data']

        return dkim


    def IsDkimSetUp(self) -> bool:
        ''' 👉 Checks with GoogleDns API if the the DKIM is set up.'''
        return self.GetDkim() != None
    

    def GetPublicKey(self) -> str:
        ''' 👉 Gets the PublicKey from the remote DKIM on Google.'''
        dkim = self.GetDkim()
        ##LOG.Print(f'DOMAIN.GetPublicKey().{dkim=}')

        public_key = None
        for part in dkim.split(';'):
            elems = part.split('=')
            if elems[0].strip() == 'p' and len(elems) == 2:
                public_key = elems[1];
        
        ##LOG.Print(f'DOMAIN.GetPublicKey().{public_key=}')
        return public_key
    

    def HasPublicKey(self) -> bool:
        ''' 👉 Checks with Google if the remote DKIM is set up.'''
        public_key = self.GetPublicKey()
        return public_key != None
        

    def HandleRegisterer(self):
        ''' 👉 host -t NS 105b4478-eaa5-4b73-b2a5-4da2c3c2dac0.dev.pollyweb.org '''
        LOG.Print(f'register_domain')

        import os
        hosted_zone_id = os.environ['hostedZoneId']  

        zone = AWS.ROUTE53(hosted_zone_id)

        domain = zone.GetDomainName()
        serverList = zone.GetNameServers()
        dnsSec = zone.GetDnsSec()
        pollywebOrg = 'z6jsx3ldteaiewnhm4dwuhljzi0vrxgn.lambda-url.us-east-1.on.aws'

        url = f'https://{pollywebOrg}/?domain={domain}&servers={serverList}&dnssec={dnsSec}'

        from WEB import WEB
        WEB().HttpGet(url)


    @classmethod
    def HandleNamer(cls, task:DEPLOYER_EXEC_PYTHON):
        ''' 👉 Stores the name of the domain in SSM.
        * Executed on DomainName CDK stack.

        Example payload (converted to YAML):
            ResourceProperties: 
                paramName: /PW/Config/DomainName
                domainName: my-domain-name.com
        '''

        # Get the params from the env variables.
        name= '/PW/Config/DomainName'
        value= task.RequireInputString('DomainName')
        
        # Store the domain name in SSM, in the current region.
        AWS.SSM().SetOnceOnly(
            name= name, 
            value= value)
