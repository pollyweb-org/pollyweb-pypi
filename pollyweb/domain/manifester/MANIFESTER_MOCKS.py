from PW_AWS.AWS import AWS
from pollyweb import LOG
from MANIFESTER import MANIFESTER
from PW_AWS.AWS_TEST import AWS_TEST
from MANIFEST import MANIFEST
from pollyweb import UTILS


class MANIFESTER_MOCKS(MANIFESTER, AWS_TEST):
        
    
    @classmethod
    def _handleManifest(cls, request):
        LOG.Print(f'📜 MANIFESTER.MOCKS._handleManifest()', f'{request=}')

        # Get a YAML string from AppConfig.
        ret = AWS.APPCONFIG().GetValue()
        UTILS.AssertIsType(ret, str)

        # Check if the domain on the manifest matches the active domain.
        m = MANIFEST(ret)
        ##LOG.Print(f'  MANIFESTER_MOCKS._handleManifest: manifest.Domain={m.RequireDomain()}')
        
        '''
        UTILS.Match(
            m.RequireDomain(),
            cls.NLWEB().CONFIG().RequireDomain()
        )
        '''

        # Return the YAML string.
        return ret
    

    @classmethod
    def MockAppConfigSetup(cls, domain:str, manifest:MANIFEST=None):
        LOG.Print('📜 MANIFESTER.MOCKS.MockAppConfigSetup()')

        UTILS.RequireArgs([domain])
        if manifest != None:
            UTILS.AssertIsType(manifest, MANIFEST)

        # Set AppConfig YAML
        if manifest == None:
            manifest = cls.MOCKS().MANIFEST().MockManifest(domain= domain)
        cls.Manifest = manifest
        
        yaml = cls.Manifest.ToYaml()
        
        AWS.APPCONFIG().MockValue(
            domain= domain, 
            value= yaml)
        
        cls.MOCKS().WEB().MockUrl(
            url= f'https://pollyweb.{domain}/manifest',
            handler= cls._handleManifest,
            domain= domain)
        
        return cls.Manifest


    @classmethod
    def MockManifester(cls, domain:str='any-domain.com', manifest:MANIFEST=None):
        UTILS.RequireArgs([domain])

        if manifest != None:
            UTILS.AssertIsType(manifest, MANIFEST)

        return cls.MockAppConfigSetup(domain= domain, manifest=manifest)