from ACM_TESTS import ACM_TESTS
from APIGW_TESTS import APIGW_TESTS
from APPCONFIG_REAL_TESTS import APPCONFIG_REAL_TESTS
from AWS_RETRY_TESTS import AWS_RETRY_TESTS
from CLOUDFRONT_TESTS import CLOUDFRONT_TESTS
from CODEBUILD_TESTS import CODEBUILD_TESTS
from CODEPIPELINE_TESTS import CODEPIPELINE_TESTS
from DYNAMO_REAL_TESTS import DYNAMO_REAL_TESTS
from ECR_TESTS import ECR_TESTS
from ECS_TESTS import ECS_TESTS
from EVENTBRIDGE_REAL_TESTS import EVENTBRIDGE_REAL_TESTS
from IAM_POLICY_TESTS import IAM_POLICY_TESTS
from LAMBDA_REAL_TESTS import LAMBDA_REAL_TESTS
from pollyweb.utils.LOG import LOG
from VPC_TESTS import VPC_TESTS
from PW_PARALLEL.PARALLEL import PARALLEL
from ROUTE53_TESTS import ROUTE53_TESTS
from S3_REAL_TESTS import S3_REAL_TESTS
from SECRETS_REAL_TESTS import SECRETS_REAL_TESTS
from SNS_TESTS import SNS_TESTS
from SQS_TESTS import SQS_TESTS
from SSM_REAL_TESTS import SSM_REAL_TESTS
from WAF_TESTS import WAF_TESTS


class AWS_REAL_TESTS():

    ICON = '🧪'


    @classmethod
    def TestAwsReal(cls, parallel:bool = True):
        #LOG.Settings().SetWriteToConsole()

        handlers = []

        handlers += ACM_TESTS.GetAllTests()
        handlers += APIGW_TESTS.GetAllTests()
        handlers += APPCONFIG_REAL_TESTS.GetAllTests()
        handlers += AWS_RETRY_TESTS.GetAllTests()
        handlers += CLOUDFRONT_TESTS.GetAllTests()
        #handlers += CODEBUILD_TESTS.GetAllTests()
        #handlers += CODEPIPELINE_TESTS.GetAllTests()
        handlers += DYNAMO_REAL_TESTS.GetAllTests()
        handlers += VPC_TESTS.GetAllTests()
        handlers += ECR_TESTS.GetAllTests()
        handlers += ECS_TESTS.GetAllTests()
        handlers += EVENTBRIDGE_REAL_TESTS.GetAllTests()
        handlers += IAM_POLICY_TESTS.GetAllTests()
        handlers += LAMBDA_REAL_TESTS.GetAllTests()
        handlers += ROUTE53_TESTS.GetAllTests()
        handlers += S3_REAL_TESTS.GetAllTests()
        handlers += SECRETS_REAL_TESTS.GetAllTests()
        handlers += SNS_TESTS.GetAllTests()
        handlers += SQS_TESTS.GetAllTests()
        handlers += SSM_REAL_TESTS.GetAllTests()
        handlers += WAF_TESTS.GetAllTests()
        

        with PARALLEL.THREAD_POOL() as pool:
            pool.RunThreadList(
                handlers= handlers, 
                parallel= parallel)

        LOG.PARALLEL().SetClassDone()