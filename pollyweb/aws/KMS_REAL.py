import boto3
import json

from PW_UTILS.UTILS import UTILS
kms_client = boto3.client('kms')

from AWS import AWS

class KMS_REAL():


    @classmethod
    def CreateForDnsSec(cls, tags:dict):
        '''👉️ Creates a KMS key for DNSSEC'''

        # Ensure the parameters
        UTILS.AssertIsDict(tags, require=True, itemType=str)

        # Convert the tags to the required format
        tags = [
            {
                'TagKey': key,
                'TagValue': value
            }
            for key, value in tags.items()
        ]
        
        # Create the KMS key with the specified key usage and key spec
        key_details = kms_client.create_key(
            CustomerMasterKeySpec='ECC_NIST_P256',
            KeyUsage='SIGN_VERIFY',
            Description='Key for signing and verifying',
            Tags=tags)

        # Get the key ID
        account_id = AWS.STS().GetAccountNumber()

        # Define the policy statement
        policy_statement = {
            "Version": "2012-10-17",
            "Id": "key-default-1",
            "Statement": [
                {
                    "Sid": "Allow dnssec-route53.amazonaws.com",
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "dnssec-route53.amazonaws.com"
                    },
                    "Action": [
                        "kms:DescribeKey",
                        "kms:GetPublicKey",
                        "kms:Sign"
                    ],
                    "Resource": "*",
                    "Condition": {
                        "StringEquals": {
                            "aws:SourceAccount": account_id
                        }
                    }
                },
                {
                    "Sid": "Enable IAM User Permissions",
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{account_id}:root"
                    },
                    "Action": "kms:*",
                    "Resource": "*"
                }
            ]
        }

        # Convert the policy statement to a JSON string
        policy = json.dumps(policy_statement)

        # Get the key ID
        key_id = key_details['KeyMetadata']['KeyId']

        # Apply the policy to the key
        kms_client.put_key_policy(
            KeyId= key_id,
            PolicyName='default',
            Policy=policy)

        # Output the key ID and ARN
        return {
            'ID': key_details['KeyMetadata']['KeyId'],
            'Arn': key_details['KeyMetadata']['Arn']
        }