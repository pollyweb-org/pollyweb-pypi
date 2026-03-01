from datetime import datetime
import pollyweb as pw


class MANIFEST_TRUST(pw.STRUCT):
    ''' 📜 Manifest trust.
    Docs: https://quip.com/lcSaAX7AiEXL/-Domain#temp:C:RSE47ce7d6dfbd749689ca1b8a8b
    '''

    def Queries(self) -> list[str]:
        trust = self
        queries: list[str] = []

        if trust.ContainsAtt('Query'):
            queries = queries + [str(trust.GetAtt('Query'))]

        if trust.ContainsAtt('Queries'):
            queries = queries + trust.ListStr('Queries')

        queries = [x.strip() for x in queries]
        queries = list(dict.fromkeys(queries))

        return queries

    def IncludesCode(self, code: str) -> bool:
        queries = self.Queries()

        # Check if the query includes the code directly.
        if code in queries or '*' in queries:
            return True

        # Check if the query includes the code as *.
        for query in queries:
            if query.endswith('*'):
                prefix = query.replace('*', '')
                if code.startswith(prefix):
                    return True

        return False

    def Domains(self) -> list[str]:
        trust = self
        domains: list[str] = []

        if trust.ContainsAtt('Domain'):
            if trust.GetStr('Domain') == '*':
                domains = ['*']
            else:
                domains = domains + [str(trust.GetAtt('Domain'))]

        if trust.ContainsAtt('Domains'):
            if trust.GetAtt('Domains') == '*':
                domains = ['*']
            else:
                domains = domains + trust.ListStr('Domains')

        if not trust.ContainsAtt('Domain') and not trust.ContainsAtt('Domains'):
            domains = ['*']

        domains = [x.strip() for x in domains]
        domains = list(dict.fromkeys(domains))

        return domains

    def IncludesDomain(self, domain: str) -> bool:
        domains = self.Domains()
        return domain in domains or '*' in domains

    def Roles(self) -> list[str]:
        trust = self
        roles: list[str] = []

        if trust.ContainsAtt('Role'):
            if trust.GetAtt('Role') == '*':
                roles = ['*']
            else:
                roles = roles + [str(trust.GetAtt('Role'))]

        if trust.ContainsAtt('Roles'):
            if trust.GetAtt('Roles') == '*':
                roles = ['*']
            else:
                roles = roles + trust.ListStr('Roles')

        if not trust.ContainsAtt('Role') and not trust.ContainsAtt('Roles'):
            roles = ['*']

        roles = [x.strip() for x in roles]
        roles_set = set(roles)

        # Return one of [], [CONSUMER], [VAULT], [CONSUMER,VAULT]
        if '*' in roles_set:
            return ['CONSUMER', 'VAULT']
        if 'CONSUMER' in roles_set and 'VAULT' in roles_set:
            return ['CONSUMER', 'VAULT']
        elif 'CONSUMER' in roles_set:
            return ['CONSUMER']
        elif 'VAULT' in roles_set:
            return ['VAULT']
        else:
            return []

    def IncludesRole(self, role: str) -> bool:
        roles = self.Roles()
        return role in roles or '*' in roles

    def Action(self) -> str | None:
        ''' 🤝 Returns GRANT or REVOKE.'''
        action = self.GetStr('Action', default='GRANT')
        if action in ['GRANT', 'REVOKE', 'INHERIT']:
            return action
        return None

    def HasAliens(self, raiseException: bool = False):
        ''' 🤝 Checks if there are typos - i.e., an alien attribute.'''
        for att in self.Attributes():
            if att not in ['Expires', 'Title', 'Action', 'Role', 'Roles', 'Queries', 'Domains', 'Query', 'Domain']:
                err = f'📜🤝 MANIFEST.TRUST.HasAliens(): unexpected att={att}!'
                if raiseException:
                    pw.LOG.RaiseValidationException(err, self)
                pw.LOG.Print(err)
                return True
        return False

    def IsGrant(self):
        return self.Action() in ['GRANT', '*']

    def IsRevoke(self):
        return self.Action() in ['REVOKE']

    def Expires(self) -> datetime:
        ''' 🤝 Returns the expiration date.'''
        return self.RequireDateTime('Expires')

    def HasExpiration(self) -> bool:
        return self.ContainsAtt('Expires')

    def IsExpired(self):
        if not self.ContainsAtt('Expires'):
            return False
        return self.Expires() < pw.UTILS.Now()

    def IsValid(self, raiseException: bool = False):
        pw.LOG.Print(f'📜🤝 MANIFEST.TRUST.IsValid()', self)

        if self.HasAliens(raiseException=raiseException):
            err = '📜🤝 MANIFEST.TRUST.IsValid(): has aliens!'
            if raiseException:
                pw.LOG.RaiseValidationException(err, self)
            pw.LOG.Print(err)
            return False

        if self.Queries() == []:
            err = '📜🤝 MANIFEST.TRUST.IsValid(): missing Queries!'
            if raiseException:
                pw.LOG.RaiseValidationException(err, self)
            pw.LOG.Print(err)
            return False

        if self.Action() not in ['GRANT', 'REVOKE', 'INHERIT']:
            err = '📜🤝 MANIFEST.TRUST.IsValid(): invalid Action!'
            if raiseException:
                pw.LOG.RaiseValidationException(err, f'action={self.Action()}', self)
            pw.LOG.Print(err)
            return False

        for role in self.Roles():
            if role not in ['VAULT', 'CONSUMER', '*']:
                err = f'📜🤝 MANIFEST.TRUST.IsValid(): invalid Role={role}'
                if raiseException:
                    pw.LOG.RaiseValidationException(err, self)
                pw.LOG.Print(err)
                return False

        return True

    def IsTrustable(
        self,
        target: str,
        role: str,
        code: str,
        action: str = 'GRANT',
        raiseException: bool = False
    ) -> bool:

        pw.LOG.Print(f'📜🤝 MANIFEST.TRUST.IsTrustable(target, role, code)',
                 f'{target=}', f'{role=}', f'{code=}', f'{action=}',
                 'self=', self)

        # Validate the request.
        pw.UTILS.AssertIsAnyValue(action, ['GRANT', 'REVOKE', 'INHERIT'])
        pw.UTILS.RequireArgs([target, role, code, action])

        # Check if the syntax is valid.
        if not self.IsValid(raiseException=raiseException):
            pw.LOG.Print('📜🤝 MANIFEST.TRUST.IsTrustable: not valid.')
            return False

        # Check if it's a GRANT (not REVOKE or INHERIT)
        if action == 'GRANT':
            if not self.IsGrant():
                pw.LOG.Print('📜🤝 MANIFEST.TRUST.IsTrustable: not a Grant.')
                return False

        # Check if it's a REVOKE (not GRANT or INHERIT)
        if action == 'REVOKE':
            if not self.IsRevoke():
                pw.LOG.Print('📜🤝 MANIFEST.TRUST.IsTrustable: not a Revoke.')
                return False

        # Check if it's already expired.
        if self.IsExpired():
            pw.LOG.Print('📜🤝 MANIFEST.TRUST.IsTrustable: expired.')
            return False

        # Check if it includes the requested role (VAULT, CONSUMER).
        if not self.IncludesRole(role):
            pw.LOG.Print(
                f"📜🤝 MANIFEST.TRUST.IsTrustable(): unmatch Role.",
                f'looking for {role=}',
                f'in the trust roles={self.Roles()}',
                'self=', self)
            return False

        # Discard on domain mismatch.
        if not self.IncludesDomain(target):
            pw.LOG.Print(f'📜🤝 MANIFEST.TRUST.IsTrustable: unmatch Domain.')
            return False

        # Finally check for query match.
        if self.IncludesCode(code):
            pw.LOG.Print(
                f'📜🤝 MANIFEST.TRUST.IsTrustable: match found!',
                f'looking for {code=}',
                f'looking for {action=}',
                'self=', self)
            return True

        pw.LOG.Print(f'📜🤝 MANIFEST.TRUST.IsTrustable: no matching queries.')
        return False
