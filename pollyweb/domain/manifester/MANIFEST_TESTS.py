from MANIFEST_MOCKS import MANIFEST_MOCKS
from PW_DOMAIN import MANIFEST
from pollyweb import TESTS
from pollyweb import LOG
from pollyweb import UTILS


class MANIFEST_TESTS(MANIFEST_MOCKS, MANIFEST):
    


    @classmethod
    def TestManifest(cls):
        yaml = cls.MockYaml()
        m = MANIFEST(yaml)

        TESTS.AssertEqual(
            given= m.Manifest(), 
            expect= UTILS.FromYaml(yaml))
        
    
    @classmethod
    def TestGetIdentity(cls):
        m = cls.MockManifest(domain='d.com')
        TESTS.AssertEqual(m.GetIdentity()['Domain'], 'd.com')

        m = MANIFEST({})
        with TESTS.AssertValidation():
            m.GetIdentity()
    
    
    @classmethod
    def TestGetDomain(cls):
        m = cls.MockManifest('d.com')
        TESTS.AssertEqual(m.RequireDomain(), 'd.com')

        # Empty domain.
        m.GetIdentity()['Domain'] = ''
        with TESTS.AssertValidation():
            m.GetName()

        # No domain.
        m.RemoveAtt('Identity.Domain')
        with TESTS.AssertValidation():
            m.GetName()

        # Empty manifest.
        m = MANIFEST({})
        with TESTS.AssertValidation():
            m.RequireDomain()

        # Empty identity.
        m = MANIFEST({ 'Identity': {} })
        with TESTS.AssertValidation():
            m.RequireDomain()
        

    @classmethod
    def TestGetName(cls):

        m = cls.MockManifest('d.com', name='Any Domain')
        TESTS.AssertEqual(m.GetName(), 'Any Domain')

        # Default to domain.
        m.RemoveAtt('Identity.Name')
        TESTS.AssertEqual(m.GetName(), 'd.com')

        # Empty domain.
        m.GetIdentity()['Domain'] = ''
        with TESTS.AssertValidation():
            m.GetName()

        # No domain.
        m.RemoveAtt('Identity.Domain')
        with TESTS.AssertValidation():
            m.GetName()
    

    @classmethod
    def TestGetSmallIcon(cls):
        m = cls.MockManifest(smallIcon='small')
        TESTS.AssertEqual(m.GetSmallIcon(), 'small')

        m = cls.MockManifest(smallIcon='')
        TESTS.AssertEqual(m.GetSmallIcon(), '')

        m = cls.MockManifest(smallIcon=None)
        TESTS.AssertEqual(m.GetSmallIcon(), None)
    
    
    @classmethod
    def TestGetBigIcon(cls):
        m = cls.MockManifest(bigIcon='big')
        TESTS.AssertEqual(m.GetBigIcon(), 'big')

        m = cls.MockManifest(bigIcon='')
        TESTS.AssertEqual(m.GetBigIcon(), '')

        m = cls.MockManifest(bigIcon=None)
        TESTS.AssertEqual(m.GetBigIcon(), None)


    @classmethod
    def TestGetTranslations(cls):
        m = cls.MockManifest()

        m.GetIdentity()['Translations'] = [{
            "Language": "en-us",
            "Translation": "<translationOf(any-host.org)>"
        }]

        TESTS.AssertEqual(
            given= m.GetTranslations(), 
            expect= [{
                "Language": "en-us",
                "Translation": "<translationOf(any-host.org)>"
            }])
        
        # Empty list.
        m.GetIdentity()['Translations'] = []
        TESTS.AssertEqual(m.GetTranslations(), [])

        # No list at all.
        m.RemoveAtt('Identity.Translations')
        TESTS.AssertEqual(m.GetTranslations(), [])
    

    @classmethod
    def TestTranslate(cls):
        m = cls.MockManifest(name='MyName')

        m.GetIdentity()['Translations'] = [{
            "Language": "en-us",
            "Translation": "Any Domain in English"
        },{
            "Language": "pt-pt",
            "Translation": "Qualquer Domínio em Português"
        }]

        # look for the language.
        TESTS.AssertEqual(
            given= m.Translate('pt-pt'), 
            expect= "Qualquer Domínio em Português")
        
        # default to the name.
        TESTS.AssertEqual(
            given= m.Translate('any-missing-language'), 
            expect= "MyName")
    

    @classmethod
    def TestGetCodes(cls):
        from PW_DOMAIN import CODE
        
        m = cls.MockManifest()
        codes = m.GetCodes()

        TESTS.AssertEqual(len(codes), 7)
        TESTS.AssertClass(codes[0], CODE)
        TESTS.AssertEqual(codes[0].RequirePath(), '/BANK')
        
    
    @classmethod
    def TestVerifyIdentity(cls):

        m = cls.MockManifest(domain='d.com')
        m.VerifyIdentity(expectedDomain='d.com')

        with TESTS.AssertValidation():
            m.VerifyIdentity(expectedDomain='another.com')
    

    @classmethod
    def TestGrantTrusts(cls):
        m = cls.MockManifest()

        # ---------------------
        # Only accept CONSUMER,VAULT,*
        # ---------------------

        m['Trusts'] = []
        m.IsTrustable(target='d.com', role='VAULT', code='any-code')
        m.IsTrustable(target='d.com', role='CONSUMER', code='any-code')
        m.IsTrustable(target='d.com', role='*', code='any-code')
        with TESTS.AssertValidation():
            m.IsTrustable(target='d.com', role='any-thing-else', code='any-code')
        
        # ---------------------
        # test Expiration
        # ---------------------
            
        trust = { "Query": "<code>" }
        m['Trusts'] = [trust]
        
        # Accept not expired.
        trust["Expires"] = "2200-01-01T00:00:00Z"
        TESTS.AssertTrue(
            m.IsTrustable(target='d.com', code='<code>', role='VAULT', raiseException=True),
            'TestGrantTrusts: Not expired trust should have been accepted!')
        
        # Don't accept expired.
        trust["Expires"] = "2000-01-01T00:00:00Z"
        TESTS.AssertFalse(
            m.IsTrustable(target='d.com', code='<code>', role='VAULT', raiseException=True),
            'TestGrantTrusts: Expired trust should have been ignored!')
            
        # ---------------------
        # test VAULT
        # ---------------------

        m['Trusts'] = [{
            "Action": "GRANT",
            "Role": "VAULT",
            "Queries": ["<code>"],
            "Domains": ["governo.it", "gov.mt"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='gov.mt', role='VAULT', code='<code>'))
        TESTS.AssertFalse(m.IsTrustable(target='gov.mt', role='VAULT', code='<code>2'))
        TESTS.AssertFalse(m.IsTrustable(target='gov.mt2', role='VAULT', code='<code>'))
        TESTS.AssertFalse(m.IsTrustable(target='gov.mt', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test CONSUMER.
        # ---------------------

        m['Trusts'] = [{
            "Action": "GRANT",
            "Role": "CONSUMER",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))
        TESTS.AssertFalse(m.IsTrustable(target='iata.org2', role='CONSUMER', code='<code>'))
        TESTS.AssertFalse(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>2'))
        TESTS.AssertFalse(m.IsTrustable(target='airlines.any-igo.org', role='VAULT', code='<code>'))

        # ---------------------
        # Test Role:*
        # ---------------------

        m['Trusts'] = [{
            "Action": "GRANT",
            "Role": "*",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test Action missing
        # ---------------------

        m['Trusts'] = [{
            "Role": "*",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test Domain*
        # ---------------------

        m['Trusts'] = [{
            "Action": "GRANT",
            "Role": "CONSUMER",
            "Queries": ["<code>"],
            "Domains": '*'
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test Role missing
        # ---------------------

        m['Trusts'] = [{
            "Action": "GRANT",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test Action and Role missing
        # ---------------------

        m['Trusts'] = [{
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test Action, Role, and Domains missing
        # ---------------------

        m['Trusts'] = [{
            "Queries": ["<code>"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test single Query/Domain
        # ---------------------

        m['Trusts'] = [{
            "Query": "<code>",
            "Domain": "airlines.any-igo.org"
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test ignore if there's any type - i.e., unexpected property
        # ---------------------

        m['Trusts'] = [{
            "Action2": "*",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertFalse(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))

        # ---------------------
        # Test prefix codes
        # ---------------------

        m['Trusts'] = [{
            "Queries": ["europa.eu/DISA*"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='europa.eu/DISABILITY/CARD'))

        # ---------------------
        # Test multiple Role (1/3)
        # ---------------------

        m['Trusts'] = [{
            "Query": "<code>",
            "Roles": ["CONSUMER"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))
        TESTS.AssertFalse(m.IsTrustable(target='airlines.any-igo.org', role='VAULT', code='<code>'))

        # ---------------------
        # Test multiple Role (2/3)
        # ---------------------

        m['Trusts'] = [{
            "Query": "<code>",
            "Roles": ["VAULT"]
        }]
        TESTS.AssertFalse(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='VAULT', code='<code>'))

        # ---------------------
        # Test multiple Role (3/3)
        # ---------------------

        m['Trusts'] = [{
            "Query": "<code>",
            "Roles": ["CONSUMER", "VAULT"]
        }]
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='CONSUMER', code='<code>'))
        TESTS.AssertTrue(m.IsTrustable(target='airlines.any-igo.org', role='VAULT', code='<code>'))


    @classmethod
    def TestRevokeTrusts(cls):
        m = cls.MockManifest()

        # ---------------------
        # test Expiration
        # ---------------------
            
        revoke = { 
            "Action": "REVOKE",
            "Query": "<code>" 
        }
        m['Trusts'] = [
            revoke, # Revoke with expires
            { "Query": "<code>" } # Grant without expires.
        ]
        
        # Accept expired revoke.
        revoke["Expires"] = "2000-01-01T00:00:00Z"
        TESTS.AssertTrue(
            m.IsTrustable(target='d.com', code='<code>', role='VAULT', raiseException=True),
            'TestRevokeTrusts: Expired revoke should have been accepted!')
        
        # Don't accept non-expired revoke.
        revoke["Expires"] = "2200-01-01T00:00:00Z"
        TESTS.AssertFalse(
            m.IsTrustable(target='d.com', code='<code>', role='VAULT', raiseException=True),
            'TestRevokeTrusts: Non-expired revoke should have been rejected!')
            
        # ---------------------
        # test VAULT
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Role": "VAULT",
            "Queries": ["<code>"],
            "Domains": ["governo.it", "gov.mt"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='gov.mt', 
                role='VAULT', 
                code='<code>'))

        # ---------------------
        # Test CONSUMER.
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Role": "CONSUMER",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', 
                code='<code>'))

        # ---------------------
        # Test Role:*
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Role": "*",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', 
                code='<code>'))

        # ---------------------
        # Test Domain*
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Role": "CONSUMER",
            "Queries": ["<code>"],
            "Domains": '*'
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', 
                code='<code>'))

        # ---------------------
        # Test Role missing
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Queries": ["<code>"],
            "Domains": ["airlines.any-igo.org"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', 
                code='<code>'))

        # ---------------------
        # Test prefix codes
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Queries": ["europa.eu/DISA*"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', 
                code='europa.eu/DISABILITY/CARD'))

        # ---------------------
        # Test multiple Role (1/3)
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Query": "<code>",
            "Roles": ["CONSUMER"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', 
                code='<code>'))

        # ---------------------
        # Test multiple Role (2/3)
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Query": "<code>",
            "Roles": ["VAULT"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='VAULT', 
                code='<code>'))

        # ---------------------
        # Test multiple Role (3/3)
        # ---------------------

        m['Trusts'] = [{
            "Action": "REVOKE",
            "Query": "<code>",
            "Roles": ["CONSUMER", "VAULT"]
        }]
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='CONSUMER', code='<code>'))
        TESTS.AssertFalse(
            m.IsTrustable(
                target='airlines.any-igo.org', 
                role='VAULT', code='<code>'))


    @classmethod
    def TestAllManifest(cls):
        LOG.Print('MANIFEST_TESTS.TestAllManifest() ==============================')

        cls.TestManifest()
        cls.TestGetIdentity()
        cls.TestGetDomain()
        cls.TestGetName()
        cls.TestGetSmallIcon()
        cls.TestGetBigIcon()
        cls.TestGetTranslations()
        cls.TestTranslate()
        cls.TestGetCodes()
        cls.TestVerifyIdentity()
        cls.TestGrantTrusts()
        cls.TestRevokeTrusts()