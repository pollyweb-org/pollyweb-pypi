from AWS import AWS
from PW_UTILS.LOG import LOG
from PW_UTILS.UTILS import UTILS


class ECS_TESTS:
    
    ICON = '🧪'


    @classmethod
    def RunAllTests(cls):
        for test in cls.GetAllTests():
            test()


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.Cluster,
        ]
    

    @classmethod
    def Cluster(cls):
        LOG.Print('@')
        
        # Clusters are inactivated, not deleted.
        NAME = 'NLWEB-Test-ECS'
        NAME2 = NAME + '-' + UTILS.TIME().SecondsStr()
        
        with AWS.ECR().Ensure(NAME) as ecr:
            ecr.Retain = True

            if not ecr.HasImage():
                with UTILS.PYTHON().HellowWorldStreamlit() as app:
                    ecr.BuildStreamlit(app)

            with AWS.VPC().Ensure(NAME) as vpc:
                vpc.Retain = True
                    
                with AWS.ECS().Ensure(
                    name= NAME,
                    ecr= ecr,
                    vpc= vpc
                ) as cluster:
                    cluster.Retain = True
                    
                    pass
    