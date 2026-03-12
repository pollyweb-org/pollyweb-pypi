from __future__ import annotations

from .DOMAIN_CONFIG import DOMAIN_CONFIG
from ...interfaces.MANIFEST import MANIFEST
from pollyweb import DIRECTORY
from pollyweb import LOG
from pollyweb import STRUCT
from pollyweb import UTILS


class DOMAIN_PARSER():
    '''👉 Domain configuration parser:

    Expected folder structure of a domain:
        * Single manifest: <domain>/<domain>📜.yaml
            * Codes: <domain>/{codes}/**/*.yaml
            * Trusts: <domain>/{trusts}/**/*.yaml
        * Multi manifests: <domain>/<domain>📜/<sub-domain>📜.yaml
        * Config: <domain>/<domain>🗺️.yaml
        * Talkers: <domain>/talkers/<talker>.yaml
    '''

    @classmethod
    def ParseDomain(
        cls,
        domain: str,
        folder: str,
        d: DOMAIN_CONFIG = None
    ):
        '''👉 Read the config, manifest(s), and db.'''

        # Raise an exception if the lenght of the domain's first word is 1.
        if domain.startswith('👥'):
            LOG.RaiseException(f'Invalid domain name: {domain}')

        LOG.Print(f'🌐 DOMAIN.PARSER.ParseDomain()', f'{domain=}', f'{folder=}')

        if '📜' in domain:
            return

        # Validate the container.
        if not d:
            d = DOMAIN_CONFIG({
                'Domain': domain,
            })
        UTILS.AssertIsType(d, DOMAIN_CONFIG)
        d.Require()

        # Validate the request.
        UTILS.AssertStrings([domain, folder], require=True)

        # Parse the domain.
        d.SetConfig(cls._ParseConfig(folder))
        d.RequireHandlers(cls._ParseHandlers(folder))
        d.RequireTalkers(cls._ParseTalkers(folder))
        d.RequireDatabase(cls._ParseDatabase(domain, folder))
        d.RequireBucketFiles(cls._ParseBucket(folder))
        d['Crud'] = cls._ParseCrud(folder)
        d['Manifests'] = cls._ParseManifests(domain, folder)

        # Confirm if the domain name matches.
        UTILS.AssertEqual(
            given=d.RequireDomain(),
            expect=domain)

        return d

    @classmethod
    def _ParseHandlers(cls, folder: str) -> dict[str, any]:
        '''👉 Look for '<handler>.py' files inside the '/handlers' folder.'''
        UTILS.Require(folder)

        handlers = UTILS.OS().Directory(folder).GetSubDir('handlers')
        if not handlers.Exists():
            return {}

        ret = {}
        for file in handlers.GetFiles():
            if file.GetExtension() == '.py':
                handler = file.GetSimpleName()
                ret[handler] = file.RequirePath()
        return ret

    @classmethod
    def _ParseCrud(cls, folder: str):
        '''👉 Look for model.yaml files inside the '/crud/<model>' folder.'''
        UTILS.Require(folder)

        crud = UTILS.OS().Directory(folder).GetSubDir('crud')
        if not crud.Exists():
            return {}

        ret = {}
        for dir in crud.GetSubDirs():
            ret[dir.GetName()] = dir.GetPath()
        return ret

    @classmethod
    def _ParseTalkers(cls, folder: str) -> dict[str, any]:
        '''👉 Look for '<script>.yaml' files inside the '/talkers' folder.'''
        UTILS.Require(folder)

        talkers = UTILS.OS().Directory(folder).GetSubDir('talkers')
        if not talkers.Exists():
            return {}

        ret = {}

        # Initialize all talkers.
        for file in talkers.GetFiles():
            talker = file.GetSimpleName()
            ret[talker] = {
                'YAML': None,
                'Python': None
            }

        # Load all talkers.
        for file in talkers.GetFiles():
            talker = file.GetSimpleName()

            # Load the YAML code.
            if file.GetExtension() == '.yaml':
                ret[talker]['YAML'] = file.ReadText()

            # Load the module.
            elif file.GetExtension() == '.py':
                ret[talker]['Python'] = file.RequirePath()

        return ret

    @classmethod
    def _ParseBucket(cls, folder) -> dict[str, str]:
        '''👉 Look for 'bucket' folder inside the domain folder.'''
        UTILS.Require(folder)

        bucket = UTILS.OS().Directory(folder).GetSubDir('bucket')
        if not bucket.Exists():
            return {}

        files = cls._ParseBucketFolder(
            dir=bucket,
            base=bucket.GetPath())

        return files

    @classmethod
    def _ParseBucketFolder(cls, dir: DIRECTORY, base: str):
        ret: dict[str, str] = {}

        # Add the files.
        for file in dir.GetFiles():
            if file.GetExtension() == '.yaml':
                path = file.GetPath()
                ret[path] = path.replace(base, '')

        # Add the files of sub folders.
        for sub in dir.GetSubDirs():
            children = cls._ParseBucketFolder(dir=sub, base=base)
            ret.update(children)

        return ret

    @classmethod
    def _ParseDatabase(cls, domain: str, folder: str) -> dict[str, any]:
        '''👉 Look for 'database.yaml' files inside the domain folder.'''

        UTILS.Require(folder)

        file = UTILS.OS().Directory(folder).GetFile('database.yaml')
        if file.Exists():
            return file.ReadYaml()
        return {}

    @classmethod
    def _LoadCodes(cls, dir: DIRECTORY, content: dict):
        '''👉 Load files from the {codes} directory.'''

        codesDir = dir.GetSubDir('{codes}')
        if codesDir.Exists():
            STRUCT(content).Default('Codes', [])
            codes: list = content['Codes']
            for file in codesDir.GetDeepFiles(endsWith='.yaml'):
                code = STRUCT(file.ReadYaml())
                code.MoveAtt('Path', 0)
                code.RemoveAtt('🤝', safe=True)
                codes.append(code.Obj())

    @classmethod
    def _LoadTrusts(cls, dir: DIRECTORY, content: dict):
        '''👉 Load files from the {trusts} directory.'''

        trustsDir = dir.GetSubDir('{trusts}')
        if trustsDir.Exists():
            STRUCT(content).Default('Trusts', [])
            trusts: list = content['Trusts']
            for file in trustsDir.GetDeepFiles(endsWith='.yaml'):
                trust = STRUCT(file.ReadYaml())
                trust.RemoveAtt('🤝', safe=True)
                trusts.append(trust.Obj())

    @classmethod
    def _ParseManifests(cls, domain: str, folder: str) -> STRUCT:
        '''👉 Read the manifests of a domain'''
        ret = {}
        dir = UTILS.OS().Directory(f'{folder}')

        # Look for the 'manifest.yaml' file inside the domain's folder.
        yaml = dir.GetFile(f'📜 {domain}.yaml')
        if yaml.Exists():
            content = yaml.ReadYaml()
            cls._LoadCodes(dir, content)
            cls._LoadTrusts(dir, content)
            ret[domain.strip()] = content

        # Look for '<domain>📜.yaml' files inside the '/manifest' folder.
        else:
            for file in UTILS.OS().Directory(f'{folder}/📜 {domain}').GetFiles():
                # Ignore DS_Store and other unmanaged files.
                if file.GetExtension() == '.yaml':
                    subdomain = file.GetSimpleName()
                    ret[subdomain.strip()] = file.ReadYaml()

        for domain in ret.keys():
            m = MANIFEST(ret[domain.strip()])
            m.RequireAtt(msg=f'Empty manifest on domain=({domain})!')
            m.VerifyTrustSyntax()
            ret[domain.strip()] = m

        # Return a struct.
        ret = STRUCT(ret)
        return ret

    @classmethod
    def _ParseConfig(cls, folder: str) -> STRUCT:
        '''👉 Read the config of a domain.'''
        LOG.Print('🌐 DOMAIN.PARSER.ParseConfig()', f'{folder=}')

        if '📜' in folder:
            LOG.Print('🌐 DOMAIN.PARSER.ParseConfig: ignoring 📜')
            return

        UTILS.RequireArgs([folder])

        dir = UTILS.OS().Directory(folder)
        path = f'{folder}/🗺️ {dir.GetSimpleName()}.yaml'
        yaml = UTILS.OS().File(path).ReadYaml()
        ret = STRUCT(yaml)
        ret.RequireAtt(msg=f'Empty config at {path}')

        LOG.Print('🌐 DOMAIN.PARSER.ParseConfig: return', ret)
        return ret
