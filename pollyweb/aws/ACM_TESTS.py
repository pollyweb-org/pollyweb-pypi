from ACM_CERTIFICATE import ACM_CERTIFICATE
from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from LOG import LOG


class ACM_TESTS(AWS_RESOURCE_TESTER[ACM_CERTIFICATE]):
    
    
    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.AcmForApiGW,
            cls.AcmForCloudfront,
        ]
    

    @classmethod
    def AcmForApiGW(cls):
        cls.Certificate(central= False)


    @classmethod
    def AcmForCloudfront(cls):
        cls.Certificate(central= True)


    @classmethod
    def Certificate(cls, central: bool):
        LOG.Print('@', central)

        domainName= 'acm.test.dev.nlweb.org'

        acm = AWS.ACM()
        client= acm.GetClient(central= central)

        with acm.Test(
            client= client,
            name= domainName
        ) as certificate:
            certificate.WaitUntilIssued()