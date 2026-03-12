from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from LOG import LOG

class WAF_TESTS(AWS_RESOURCE_TESTER):


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.WafForApiGW,
            cls.WafForCloudfront,
        ]
    

    @classmethod
    def WafForApiGW(cls):
        cls.WebAcl(
            name= 'nlweb-test-regional', 
            central= False)
        

    @classmethod
    def WafForCloudfront(cls):
        cls.WebAcl(
            name= 'nlweb-test-central', 
            central= True)
        

    @classmethod
    def WebAcl(cls, name:str, central: bool):
        LOG.Print('@', central)

        waf = AWS.WAF()
        client= waf.GetClient(central= central)
        
        cls.BasicTest(
            pool= waf,
            name= name,
            client= client)
