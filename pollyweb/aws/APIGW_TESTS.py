from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from LOG import LOG
from PW_UTILS.TESTS import TESTS


class APIGW_TESTS(AWS_RESOURCE_TESTER):
    

    @classmethod
    def GetAllTests(cls):
        return [
            cls.RestApiWafClean,
            cls.RestApiWafDirty,
            cls.RestApiDomain,
            cls.RestApi,
        ]


    @classmethod
    def RestApiWafClean(cls):
        cls.RestApiWaf(
            cleanUp= True,
            suffix= 'Clean')


    @classmethod
    def RestApiWafDirty(cls):
        cls.RestApiWaf(
            cleanUp= False,
            suffix= 'Dirty')


    @classmethod
    def RestApiWaf(cls, cleanUp:bool, suffix:str):
        NAME = 'NLWEB-Test-ApiGW-WAF-{}'.format(suffix)
        
        # (re)Create a WAF and attach it to the API.
        with AWS.WAF().Ensure(
            name= NAME
        ) as wacl:
        
            with AWS.APIGW().Ensure(
                name= NAME
            ) as api:
                    
                # Add a resource to the API to create the DEV stage.
                # A stege is necessary to attach the WAF.
                api.MockMethod()
                
                try:
                    # Attach the WAF to the API.
                    api.AttachWebAcl(wacl)

                    # Attaching again should not fail.
                    api.AttachWebAcl(wacl)

                    # Verify the WAF is attached to the stages.
                    api2 = AWS.APIGW().GetByID(id= api.ID)
                    for stage in api2.Stages:
                        assert stage.WebAclArn == wacl.Arn

                except Exception as e:
                    # Ignore WAFUnavailableEntityException
                    if 'WAFUnavailableEntityException' not in str(e):
                        raise e


    @classmethod
    def RestApi(cls):
        LOG.Print('@')

        with AWS.APIGW().Test(
            name= 'NLWEB-Test-ApiGW'
        ) as api:
                        
            # Positive GetApiByID
            api2 = AWS.APIGW().GetByID(id= api.ID)
            assert api2.Name == api.Name
        

    @classmethod
    def RestApiDomain(cls):

        DOMAIN_NAME = 'dtwf-test.com'

        with AWS.APIGW().Ensure(
            name= 'NLWEB-Test-ApiGW-Domain'
        ) as api:    

            # (re)Create a certificate and attach it to the API.
            with AWS.ACM().Ensure(
                name= DOMAIN_NAME,
                central= False
            ) as certificate:
                assert certificate

                # Attach the certificate to the API.
                with api.SetCustomDomain(
                    domainName= DOMAIN_NAME,
                    certificate= certificate
                ):
                        
                    # Verify the domain is attached to the stages.
                    TESTS.AssertEqual(
                        api.GetDomainName(), 
                        DOMAIN_NAME)
                    
                    # Attaching again should not fail.
                    api.SetCustomDomain(
                        domainName= DOMAIN_NAME,
                        certificate= certificate)

                    # Positive GetApiByDomain
                    api2 = AWS.APIGW().GetByDomain(domain= DOMAIN_NAME)
                    assert api2 != None, 'API not found by domain.'
                    assert api2.ID == api.ID
        