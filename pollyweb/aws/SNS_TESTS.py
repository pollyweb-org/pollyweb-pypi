from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from SNS_TOPIC import SNS_TOPIC


class SNS_TESTS(AWS_RESOURCE_TESTER[SNS_TOPIC]):


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.CreateTopic,
        ]
    

    @classmethod
    def CreateTopic(cls):
        cls.BasicTest(
            pool= AWS.SNS(),
            name= 'NLWEB-Test-SNS')