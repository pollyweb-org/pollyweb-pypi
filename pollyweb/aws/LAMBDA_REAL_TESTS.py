from AWS import AWS
from pollyweb.utils.LOG import LOG
from pollyweb.utils.TESTS import TESTS
from pollyweb.utils.UTILS import UTILS


class LAMBDA_REAL_TESTS:


    @classmethod
    def GetAllTests(cls):
        
        return [
            cls.LambdaPolicy,
            cls.LambdaRole,
            cls.Lambda,
            cls.LambdaPermissions
        ]
    

    @classmethod
    def LambdaPolicy(cls):

        # Initialize the policy object.
        policy = AWS.IAM().POLICY('TestPolicy')
        TESTS.AssertEqual(policy.RequireName(), 'TestPolicy')
        TESTS.AssertNotEqual(policy.GetArn(), None)

        # Delete the policy if the policy exists.
        if policy.Exists():
            policy.Delete()
        TESTS.AssertFalse(policy.Exists())
        TESTS.AssertNotEqual(policy.GetArn(), None)

        # Create the policy on AWS.
        policy.EnsureExists()
        TESTS.AssertTrue(policy.Exists())

        # Create again should not fail.
        policy.EnsureExists()
        policy.Delete()


    @classmethod
    def LambdaRole(cls):
        
        # Initialize the role object.
        role = AWS.IAM().ROLE('TestRole')
        TESTS.AssertEqual(role.RequireName(), 'TestRole')

        # Delete the role if the role exists.
        if role.Exists():
            role.Delete()
        TESTS.AssertFalse(role.Exists())
        TESTS.AssertEqual(role.RequireArn(), None)

        # Create the role on AWS.
        role.CreateForLambda()
        TESTS.AssertTrue(role.Exists())
        TESTS.AssertNotEqual(role.RequireArn(), None)

        # Create again should not fail.
        role.EnsureForLambda()
        role.EnsureForLambda()
        role.Delete()



    @classmethod
    def Lambda(cls):
                
        # Initialize the lambda object.
        fn = AWS.LAMBDA('TestLambda')
        
        if fn.Exists():
            fn.Delete()
        TESTS.AssertFalse(fn.Exists(), 'function should not exist')

        fn.EnsurePythonLambda(
            code= '''print("Hello World")''', 
            tags= {'TagName': 'TestLambda'}, 
            env= {'EnvName': 'TestLambda'}, 
            permissions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ])
        
        roleArn = fn.GetRoleArn()
        TESTS.AssertTrue(fn.Exists(), 'function should exist')
        TESTS.AssertNotEqual(roleArn, None)

        role = fn.GetRole()
        TESTS.AssertTrue(role.Exists(), 'role should exist')
        TESTS.AssertNotEqual(role.RequireArn(), None)

        policy = role.EnsurePolicy()
        TESTS.AssertTrue(policy.Exists(), 'policy should exist')
        TESTS.AssertNotEqual(policy.GetArn(), None)

        fn.Delete()
        TESTS.AssertFalse(fn.Exists(), 'function should not exist')
        TESTS.AssertFalse(role.Exists(), 'role should not exist')
        TESTS.AssertFalse(policy.Exists(), 'policy should not exist')


    @classmethod
    def LambdaPermissions(cls):
                
        # Initialize the lambda object.
        fn = AWS.LAMBDA('TestLambdaPermissions')
        
        if fn.Exists():
            fn.Delete()

        fn.EnsurePythonLambda(
            code= '''
def handler(event, context):
    import boto3

    # dynamodb:ListTables
    dynamoClient = boto3.client('dynamodb')
    dynamoClient.list_tables()

    # lambda:ListLayers
    lambdaClient = boto3.client('lambda')
    lambdaClient.list_layers()

    return 'Success'
''', 
            tags= {'TagName': 'TestLambda'}, 
            env= {'EnvName': 'TestLambda'}, 
            permissions=[
                "lambda:ListLayers",
                "dynamodb:ListTables"
            ])
        

        for i in range(20):
            try:
                ret = fn.Invoke()
                UTILS.AssertEqual(ret, 'Success')
                break
            except Exception as e:
                if i < 19 and '(AccessDeniedException)' in str(e):
                    LOG.Print(f'Waiting for the permission to be granted... {i} secs')
                    UTILS.Sleep(1)
                else:
                    raise e
        
        fn.Delete()
       


    