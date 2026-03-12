from PW_DOMAIN import DOMAIN_CONFIG
from pollyweb import UTILS
from pollyweb import LOG


class DOMAIN_DEPLOY():


    @classmethod
    def Deploy(cls, config:DOMAIN_CONFIG):
        LOG.Print('🌐 DOMAIN.DEPLOY.Deploy(config)', 
            'config=', config)

        # Check if the parsing of the config was done.
        if not config:
            LOG.RaiseException('Parse the configuration before deploying.')

        # Validate the request.
        UTILS.AssertIsType(config, DOMAIN_CONFIG, require=True)
        
        # Get the config values.
        domain = config.RequireDomain()
        manifest = config.RequireManifest(domain=domain)
        configProfile= config.RequireProfile()

        # Verify the account profile.
        from PW_AWS.AWS import AWS 
        cliProfile= AWS.STS().GetCliProfile()
        UTILS.AssertEqual(
            given= cliProfile,
            expect= configProfile)

        # Deploy the manifest.
        from PW import PW
        PW.BEHAVIORS().MANIFESTER().PublishManifest(
            manifest= manifest)
        
        # Deploy the settings.
        setter = PW.CONFIG()
        
        # Listener config.
        if (config.HasListener()): 
            setter.SetListener(
                config.RequireListener())
            
        # Graph config.
        if (config.HasGraph()): 
            setter.SetGraph(
                config.RequireGraph())