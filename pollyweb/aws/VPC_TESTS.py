from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from LOG import LOG


class VPC_TESTS(AWS_RESOURCE_TESTER):


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.VPC,
        ]
    

    @classmethod
    def VPC(cls):
        LOG.Print('@')
        NAME = 'NLWEB-Test-VPC'

        cls.BasicTest(
            pool= AWS.VPC(),
            name= NAME,
            prefix= '10.76')