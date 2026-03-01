# 📚 CODE

from .CODE_CODES import CODE_CODES
from .ITEM import ITEM
from ..utils import UTILS
from ..utils import LOG


class CODE(ITEM, CODE_CODES):
    ''' 📜 https://quip.com/3mKNASbBpnng#temp:C:eVd92c29500621a4395928f6d216

    `Example #1:`
    {
        "Path": "/SSR",
        "Name": "Special service request",
        "Translations": [{
            "Language": "en-us",
            "Translation": "Special service request"
        }],
        "Schemas": []
    }

    `Example #2`
    {
        "Path": "/SSR/WCHR/CRED",
        "Name": "Wheelchair for ramp",
        "Translations": [{
                "Language": "en-us",
                "Translation": "Wheelchair for ramp"
        }],
        "Schemas": [
            {
                "Output": "SHARE",
                "Version": "1.2",
                "Location": "https://airlines.any-igo.org/pollyweb/schemas/SSR-WCHR.json"
            },
            {
                "Output": "QR",
                "Version": "1",
                "Inherits": "pollyweb.org/TOKEN:1",
                "Format": "IsElectric, Size, NeedsAssistant, DateOfBirth"
            }
        ]
    }
    '''

    @classmethod
    def CODES(cls):
        return CODE_CODES()

    def RequirePath(self):
        '''👉 https://quip.com/3mKNASbBpnng#temp:C:eVd16240521811d4e9b87aec625a'''
        return self.RequireStr('Path')

    def GetDelegate(self):
        return self.GetStr('Delegate')

    def GetDelegator(self):
        return self.GetStr('Delegator')

    @classmethod
    def Verify(cls, code: str):
        '''👉 Verifies the format of a code.'''

        UTILS.Require(code)
        UTILS.AssertIsType(code, str)

        if '/' not in code:
            LOG.RaiseValidationException(
                f'Invalid code! It should countain an /, but found ({code}).')
        if '//' in code:
            LOG.RaiseValidationException(
                f'Invalid code! It should not contain //, but found ({code}).')
        if ' ' in code:
            LOG.RaiseValidationException(
                f'Invalid code! It should not contain spaces, but found ({code}).')

        parts = code.split('/')
        if len(parts) < 2:
            LOG.RaiseValidationException(
                f'Invalid code! It should countain at least 2 parts of /, e.g. <domain>/<path>, but found ({code}).')

        if code.startswith('/'):
            LOG.RaiseValidationException(
                f'Invalid code! The authority is missing, e.g. <domain>/<path>, but found ({code}).')

        authority = code.split('/')[0]
        if code.count(authority) > 1:
            LOG.RaiseValidationException(
                f'Invalid code! The authority=({authority}) cannot be part of the path in code=({code}).')

    @classmethod
    def ParseAuthority(cls, code: str):
        '''👉 Gets the authority part of a code.
        * ParsePath(<authority>/<path>) -> <authority>
        * ParsePath(d.com/A/B/C) -> d.com
        * ParsePath(d.com) -> None
        '''

        if '/' not in code or code.startswith('/'):
            return None
        return code.split('/')[0].strip()

    @classmethod
    def ParsePath(cls, code: str) -> 'Optional[str]':
        '''👉 Gets the domain part of a code.
        * ParsePath(<domain>/<path>) -> <path>
        * ParsePath(d.com/A/B/C) -> /A/B/C
        * ParsePath(d.com) -> None
        '''

        domain = cls.ParseAuthority(code)
        if domain is None:
            return None
        return code.replace(domain, '').strip()

    @classmethod
    def ParseRoot(cls, code: str):
        '''👉 Gets the root part of a path.
        * ParseRoot(<domain>/<root>/<subpath>) -> <root>
        * ParseRoot(d.com/A/B/C) -> /A
        '''

        path = cls.ParsePath(code)
        if path is None:
            return None
        return '/' + path.split('/')[1].strip()

    @classmethod
    def ParseGroup(cls, code: str):
        cls.Verify(code)
        authority = cls.ParseAuthority(code)
        root = cls.ParseRoot(code)
        return f'{authority}{root}/*'
