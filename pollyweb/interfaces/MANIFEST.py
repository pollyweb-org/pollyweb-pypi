# 📚 MANIFEST

# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from typing import Union
from .CODE import CODE
from ..utils import STRUCT
from ..utils import UTILS
from ..utils import LOG
from .MANIFEST_TRUST import MANIFEST_TRUST


class ManifestNotAvailableException(Exception):
    pass


class MANIFEST(STRUCT):
    ''' 📜 Wrapper of a YAML Manifest.
    Docs: https://quip.com/lcSaAX7AiEXL/-Domain#temp:C:RSE47ce7d6dfbd749689ca1b8a8b
    '''

    def __init__(self, manifest: Union[str, "MANIFEST", any] = None, section: str = None):
        obj = manifest

        if isinstance(manifest, str):
            obj = UTILS.FromYaml(manifest)

        elif isinstance(manifest, MANIFEST):
            obj = manifest.Manifest()

        elif section is not None:
            obj = {}
            obj[section] = manifest

        else:
            obj = manifest

        super().__init__(obj=obj)

    def Manifest(self) -> str:
        '''👉 Returns the internal object.'''
        return self.Obj()

    def VerifySyntax(self):
        self.GetBigIcon()
        self.GetSmallIcon()
        self.GetCodes()
        self.GetIdentity()
        self.GetName()
        self.GetTranslations()
        self.VerifyTrustSyntax()

    def GetIdentity(self):
        '''Example: {
            "Domain": "example.com",
            "Name": "<translationOf(any-host.org)>",
            "SmallIcon": "https://example.com/small-icon.png",
            "BigIcon": "https://example.com/big-icon.png",
            "Translations": [{
                "Language": "en-us",
                "Translation": "<translationOf(any-host.org)>"
            }]
        }'''
        return self.RequireStruct('Identity')

    def RequireDomain(self) -> str:
        id = STRUCT(self.GetIdentity())
        return id.RequireStr('Domain')

    def GetName(self):
        id = STRUCT(self.GetIdentity())
        return id.RequireStr('Name', default=self.RequireDomain())

    def GetSmallIcon(self):
        return self.GetIdentity().GetStr('SmallIcon')

    def GetBigIcon(self):
        return self.GetIdentity().GetStr('BigIcon')

    def GetTranslations(self, default=[]):
        '''👉 Returns a list of translations.
        * List [*] -> [*]
        * Empty list -> []
        * No list at all -> []
        '''
        return self.GetIdentity().GetAtt('Translations', default=default)

    def Translate(self, language) -> str:
        '''
        📜 Returns the translation of the domain title into a the given language.
        👉 https://quip.com/lcSaAX7AiEXL/-Domain#temp:C:RSEbf2bcdeaf8e244ae885e09e41
        '''
        translations = self.GetTranslations(default=[])
        for translation in translations:
            if 'Language' in translation:
                if translation['Language'] == language:
                    return translation['Translation']
        return self.GetName()

    def GetCodes(self) -> list[CODE]:
        '''📜 Returns the list of codes defined by the authority.
        * https://quip.com/3mKNASbBpnng#temp:C:eVd66f7803481a34db7a14b6698e
        '''
        codes = []
        for code in self.Structs('Codes'):
            codes.append(CODE(code))
        return codes

    def GetTrusts(self) -> list[MANIFEST_TRUST]:
        '''📜 Returns the list of trusts defined by the authority.'''
        trusts = []
        for trust in self.Structs('Trusts'):
            trusts.append(MANIFEST_TRUST(trust))
        return trusts

    def GetCodeDelegate(self, path: str):
        return self.GetStruct('Delegates').First('Code', equals=path)

    def GetCodeByPath(self, path: str, delegator: str = None) -> CODE:
        '''📜 Returns the code struct with a certain code string.
        * https://quip.com/3mKNASbBpnng#temp:C:eVd66f7803481a34db7a14b6698e
        '''

        for code in self.GetCodes():
            if code.RequirePath() == path:
                if delegator is None:
                    return code
                elif delegator == code.GetDelegator():
                    return code

        return CODE(None)

    def VerifyIdentity(self, expectedDomain: str):
        ''' 👉 Check if the manifest is valid for the given domain. '''
        LOG.Print(f'📜 MANIFEST.VerifyIdentity()', f'{expectedDomain=}')

        # Raise an exception if the name starts with a space.
        if expectedDomain.startswith(' '):
            LOG.RaiseException(f'Remove the space from the name: {expectedDomain}')

        id = self.RequireStruct('Identity')
        id.Match('Domain', expectedDomain)

    def VerifyTrustSyntax(self):
        '''📜 Checks if the manifest is valid.'''
        LOG.Print(f'📜 MANIFEST.VerifySyntax()')

        for trust in self.GetTrusts():
            trust.IsValid(raiseException=True)

    def IsTrustable(
        self,
        target: str,
        role: str,
        code: str,
        raiseException: bool = False
    ) -> bool:
        '''📜 Looks for the trust in the manifest.
        * Role: [CONSUMER, VAULT, *]
        * Docs: https://quip.com/lcSaAX7AiEXL#temp:C:RSEe24ce39a70604b598bebe8ff1 '''

        LOG.Print(f'📜🤝 MANIFEST.IsTrustable(target, role, code, raiseException)',
                  f'manifest={self.RequireDomain()}',
                  f'{target=}',
                  f'{role=}',
                  f'{code=}',
                  f'{raiseException=}')

        UTILS.RequireArgs([target, role, code])
        UTILS.AssertIsAnyValue(role, options=['CONSUMER', 'VAULT', '*'])

        trusts = self.GetTrusts()

        # Check if it's blocked by any REVOKE.
        for trust in trusts:
            isRevoked = trust.IsTrustable(
                target=target,
                role=role,
                code=code,
                action='REVOKE',
                raiseException=raiseException)
            if isRevoked:
                LOG.Print('📜🤝 MANIFEST.IsTrustable: found revoked!')
                return False

        # Check if it's trusted by any GRANT.
        for trust in trusts:
            isTrustable = trust.IsTrustable(
                target=target,
                role=role,
                code=code,
                raiseException=raiseException)
            if isTrustable:
                LOG.Print('📜🤝 MANIFEST.IsTrustable: found grant!')
                return True

        LOG.Print('📜🤝 MANIFEST.IsTrustable: no match found')
        return False
