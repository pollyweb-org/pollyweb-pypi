from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from SQS_QUEUE import SQS_QUEUE


class SQS_TESTS(AWS_RESOURCE_TESTER[SQS_QUEUE]):
    

    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.Queue,
        ]
    

    @classmethod
    def Queue(cls):
        cls.BasicTest(
            pool= AWS.SQS(),
            name= 'NLWEB-Test-SQS')