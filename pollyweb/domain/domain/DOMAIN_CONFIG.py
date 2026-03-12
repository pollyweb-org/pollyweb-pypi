from typing import Optional

from pollyweb import STRUCT
from pollyweb import UTILS
from pollyweb import LOG
from ...interfaces.MANIFEST import MANIFEST


class DOMAIN_CONFIG(STRUCT):
    '''👉 Domain configuration.
    * Loaded by DOMAIN_PARSER, to load the config from files.
    * Extended by INTERNET_DOMAIN, for in-memory tests.

    Example:
        Domain: any-domain.com

        Config:
            Domain: any-domain.com
            Broker: any-broker.org
            Graph: any-graph.org
            Listener: any-listener.org
            Roles: [ VAULT ]

        Talkers:
            website: bla, bla
            restaurant: bla, bla

        Manifests:
            any-domain.com:
                Identity:
                    Domain: any-domain.com
                    Name: Any Domain
    '''

    def MatchDomain(self, set: STRUCT, att: str = 'Domain'):
        if set is not None:
            UTILS.AssertEqual(
                given=set.RequireStr(att),
                expect=self.RequireDomain())

    def RequireDomain(self, set: Optional[str] = None):
        if set is not None:
            ret = self.RequireStr('Domain', set=set)
        else:
            ret = self.RequireStr('Domain')
        if UTILS.GetEmojiInName(ret):
            LOG.RaiseValidationException(f'Invalid domain name: {ret}')
        return ret

    def RequireIsActor(self, set: Optional[bool] = None):
        if set is not None:
            return self.RequireBool('IsActor', set=set)
        return self.RequireBool('IsActor')

    def RequireTalkers(self, set: Optional[STRUCT] = None):
        return self.RequireStruct('Talkers', set=set)

    def RequireTalker(self, name: str):
        return self.RequireTalkers().RequireStruct(name)

    def RequireConfig(self):
        return self.RequireStruct('Config')

    def SetConfig(self, set: STRUCT):
        LOG.Print('🌐 DOMAIN.CONFIG.SetConfig(set)', set)
        self.Require()
        UTILS.Require(set)
        return self.RequireStruct('Config', set=set)

    def RequireHandlers(self, set: Optional[STRUCT] = None):
        return self.RequireStruct('Handlers', set=set)

    def RequireBucketFiles(self, set: Optional[dict[str, str]] = None):
        return self.RequireStruct('Bucket', set=set)

    def RequireDatabase(self, set: Optional[STRUCT] = None):
        return self.RequireStruct('Database', set=set)

    def RequireCrud(self, set: Optional[STRUCT] = None):
        return self.RequireStruct('Crud', set=set)

    def GetSelfie(self):
        return self.RequireConfig().GetStr('Selfie')

    def GetTranscriber(self):
        return self.RequireConfig().GetStr('Transcriber')

    def RequireBroker(self):
        return self.RequireConfig().RequireStr('Broker')

    def RequireProfile(self):
        return self.RequireConfig().RequireStr('Profile')

    def RequireCollectors(self):
        return self.RequireConfig().ListStr('Collectors', require=True)

    def RequireSellers(self):
        return self.RequireConfig().ListStr('Sellers', require=True)

    def RequireVaults(self):
        return self.RequireConfig().ListStr('Vaults', require=True)

    def RequireHosts(self):
        return self.RequireConfig().ListStr('Hosts', require=True)

    def RequireListener(self):
        '''👉 Returns the domain's listener.'''
        return self.RequireConfig().RequireStr('Listener')

    def HasListener(self) -> bool:
        '''👉 Returns true if the domain's listener is set.'''
        return not self.RequireConfig().IsMissingOrEmpty('Listener')

    def RequireGraph(self):
        return self.RequireConfig().RequireStr('Graph')

    def HasGraph(self) -> bool:
        '''👉 Returns true if the domain's graph is set.'''
        return not self.RequireConfig().IsMissingOrEmpty('Graph')

    def RequireRoles(self):
        '''👉 Returns the domain's roles.'''
        return self.RequireConfig().ListStr('Roles', require=True)

    def RequireManifest(self, domain: str):
        '''👉 Returns the selected manifest'''
        result = self.RequireManifests(search=domain)
        if len(result) == 0:
            LOG.RaiseValidationException(f'Domain manifest not found: {domain}')
        return result[0]

    def RequireManifests(self, search: Optional[str] = None) -> list[MANIFEST]:
        ''' Loads all manifests.'''

        LOG.Print('🌐🎭 INTERNET.DOMAIN.RequireManifests()')
        ret: list[MANIFEST] = []

        manifests = self.RequireStruct('Manifests')
        for domain in manifests.Obj().keys():
            LOG.Print(
                '🌐🎭 INTERNET.DOMAIN.RequireManifests: ', f'{domain=}')

            # Convert and validate.
            UTILS.AssertIsType(domain, str)
            manifest = MANIFEST(manifests.RequireStruct(domain))
            manifest.Require()
            manifest.VerifyIdentity(domain)

            ret.append(manifest)

            if search == domain:
                return [manifest]

        return ret

    def RequireKeys(self, set: Optional[list[str]] = None):
        if set is not None:
            return self.RequireAtt('Keys', set=set)
        return self.RequireAtt('Keys')

    def RequireDKIM(self, set: Optional[str] = None):
        if set is not None:
            return self.RequireStr('DKIM', set=set)
        return self.RequireStr('DKIM')
