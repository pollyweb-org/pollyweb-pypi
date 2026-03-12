# 📚 LAMBDA
 
import boto3
lambdaClient = boto3.client('lambda')
lambda_client = lambdaClient

from AWS_RETRY import RetryWithBackoff
from LAMBDA_DEPLOY_LAYERS import LAMBDA_DEPLOY_LAYERS
from LAMBDA_BASE import LAMBDA_BASE

class LAMBDA_REAL(
    LAMBDA_DEPLOY_LAYERS,
    LAMBDA_BASE
):
    ''' 👉 Looks up the `alias` in `os.environ`
        * if not found, considers the `alias` as the function name.'''


    @classmethod
    def Layers(cls):
        from LAMBDA_LAYERS import LAMBDA_LAYERS as proxy
        return proxy()
