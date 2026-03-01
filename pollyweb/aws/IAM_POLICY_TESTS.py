
from IAM_POLICY import IAM_POLICY
from pollyweb.utils.TESTS import TESTS


class IAM_POLICY_TESTS(IAM_POLICY):

    
    @classmethod
    def TestMergeStatements(cls):

        given = [
            {
                "Sid": "77ebfeb2ddeb49708f2eae74d7de8e7e",
                "Effect": "Allow",
                "Resource": "*",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream"
                ]
            },
            {
                "Sid": "26ffec851fac497db5070a881205d7c8",
                "Effect": "Allow",
                "Resource": "arn:aws:secretsmanager:us-west-2:997532394226:secret:/NLWEB/PrivateKey-D5ssHY",
                "Action": [
                    "secretsmanager:GetSecretValue",
                    "kms:Encrypt"
                ]
            },
            {
                "Sid": "xpto",
                "Effect": "Allow",
                "Resource": "arn:aws:secretsmanager:us-west-2:997532394226:secret:/NLWEB/PublicKey-D5ssHY",
                "Action": [
                    "secretsmanager:GetSecretValue",
                    "kms:Encrypt"
                ]
            },
            {
                "Sid": "b9fae7f4bdaf4cc88b3cc4e28ad58c5d",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]

        expected = [
            {
                "Sid": "77ebfeb2ddeb49708f2eae74d7de8e7e",
                "Effect": "Allow",
                "Resource": "*",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ]
            },
            {
                "Sid": "26ffec851fac497db5070a881205d7c8",
                "Effect": "Allow",
                "Resource": "arn:aws:secretsmanager:us-west-2:997532394226:secret:/NLWEB/PrivateKey-D5ssHY",
                "Action": [
                    "secretsmanager:GetSecretValue",
                    "kms:Encrypt"
                ]
            }, {
                "Sid": "xpto",
                "Effect": "Allow",
                "Resource": "arn:aws:secretsmanager:us-west-2:997532394226:secret:/NLWEB/PublicKey-D5ssHY",
                "Action": [
                    "secretsmanager:GetSecretValue",
                    "kms:Encrypt"
                ]
            }
        ]

        TESTS.AssertEqual(
            cls.MergeStatements(given), 
            expected)


    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.TestMergeStatements
        ]
        

    @classmethod
    def RunAllTests(cls):
        for test in cls.GetAllTests():
            test()

        