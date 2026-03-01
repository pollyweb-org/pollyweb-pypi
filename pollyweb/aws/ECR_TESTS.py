from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from pollyweb.utils.UTILS import UTILS


class ECR_TESTS(AWS_RESOURCE_TESTER):
    

    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.EcrRepo,            
        ]
    
    
    @classmethod
    def EcrRepo(cls):
        name = 'NLWEB-Test-ECR-Repo-' + UTILS.TIME().SecondsStr()
        name = name.lower()

        cls.BasicTest(
            pool= AWS.ECR(),
            name= name)
        