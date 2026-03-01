from AWS import AWS
from IAM_POLICY_VERSION import IAM_POLICY_VERSION
from PW_UTILS.LOG import LOG
from PW_UTILS.PRINTABLE import PRINTABLE
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS

# Initialize IAM client
import json
import boto3
iam_client = boto3.client('iam')


class IAM_POLICY(PRINTABLE):

    ICON = '🔒'


    def __init__(self, 
        name:str, 
        cached:bool= False
    ) -> None:
        
        self._name = name

        self._cached = cached
        if cached: self._cache = UTILS.CACHE()

        PRINTABLE.__init__(self=self, toJson=name)



    def RequireName(self):
        return self._name
    

    def GetArn(self):
        # Check if self._policy_arn is set
        if not hasattr(self, '_policy_arn'):
            self._account_id = AWS.STS().GetAccountNumber()
            self._policy_arn = f"arn:aws:iam::{self._account_id}:policy/{self._name}"
        return self._policy_arn


    def Delete(self):
        '''👉️ Deletes the policy.'''

        policy_arn = self.GetArn()

        # Delete all non-default policy versions
        for version in self.GetVersions():
            if not version['IsDefaultVersion']:
                iam_client.delete_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=version['VersionId'])

        try:
            iam_client.delete_policy(PolicyArn= policy_arn)
            LOG.Print(f"🔒 IAM.POLICY.Delete: Deleted policy {self._name}.")

        except iam_client.exceptions.NoSuchEntityException:
            LOG.Print(f"🔒 IAM.POLICY.Delete: Policy {self._name} does not exist.")


    def Exists(self):
        '''👉️ Checks if the policy exists.'''
        try:
            iam_client.get_policy(PolicyArn= self.GetArn())
            return True

        except iam_client.exceptions.NoSuchEntityException:
            return False


    def EnsureExists(self, roleName:str=None):
        '''👉️ Ensures that the policy exists.'''

        self._policy_name = self.RequireName()

        # Check if a specific policy exists and create it if it doesn't
        self._account_id = AWS.STS().GetAccountNumber()
        self._policy_arn = f"arn:aws:iam::{self._account_id}:policy/{self._policy_name}"

        try:
            # Try to retrieve the policy
            policy = iam_client.get_policy(PolicyArn= self._policy_arn)

            self._policy_version = iam_client.get_policy_version(
                PolicyArn= policy['Policy']['Arn'],
                VersionId= policy['Policy']['DefaultVersionId'])
            
            self._policy_document = self._policy_version['PolicyVersion']['Document']

        except iam_client.exceptions.NoSuchEntityException:
            
            # Policy does not exist, create a new one
            self._policy_document = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents"
                        ],
                        "Resource": "*"
                    }
                ]
            }

            create_response = iam_client.create_policy(
                PolicyName= self._policy_name,
                PolicyDocument= json.dumps(self._policy_document),
                Description= "Policy for ...")
            
            self._policy_arn = create_response['Policy']['Arn']
            LOG.Print(f"Created new policy: {self._policy_name}")

            # Attach the policy to the role
            if roleName:
                self.AttachToRole(roleName)


    def AttachToRole(self, roleName:str):
        '''👉️ Attaches the policy to the role.'''
        iam_client.attach_role_policy(
            RoleName= roleName,
            PolicyArn= self.GetArn())
        
        LOG.Print(self.AttachToRole, 
            f"Attached policy {self._name} to role {roleName}.")
            

    @classmethod
    def MergeStatements(self, statements:list):
        # Merge the statements for the same resource.
        resources = {}

        for statement in statements:
            resource = statement['Resource']

            if resource not in resources:
                resources[resource] = {
                    'Sid': f'NLWEB{len(resources)+1}',
                    'Action': []
                }

            for action in statement['Action']:
                if action not in resources[resource]['Action']:
                    resources[resource]['Action'].append(action)
        
        return [{
            "Sid": resources[resource]['Sid'],
            "Effect": "Allow",
            "Resource": resource,
            "Action": resources[resource]['Action']
        } for resource in resources]
    
        
    def SetPermissions(self, 
        permissions: list[str] | dict[str, list[str]] = [],
        statements: list[dict] = []
    ):
        '''👉️ Sets the permissions in the policy document.'''

        LOG.Print(self.SetPermissions,
            f"{self._name=}, {permissions=}")
        
        UTILS.AssertIsAnyType(permissions, options=[list, dict], require=True)

        # Delete all policy versions.
        defaultVersion = None
        for version in self.GetVersions():
            '''
            version:
                VersionId: v1
                IsDefaultVersion: true
                CreateDate: '2024-04-18 23:22:30+00:00'
            '''
            if version.IsDefaultVersion:
                defaultVersion = version
            else:
                version.Delete()

        # Ignore if there are no permissions to set.
        if type(permissions) == list and len(permissions) == 0:
            return  
        
        # Convert permissions to a dictionary if it's a list
        if type(permissions) == list:
            permissionDict = { '*' : permissions }
        else:
            permissionDict = permissions
        
        # Set the permissions in the policy document
        statements = []
        for resource, permissions in permissionDict.items():
            
            if not resource:
                resource = "*"

            statements.append({
                "Sid": UTILS.UUID().replace('-', ''),
                "Effect": "Allow",
                "Resource": resource,
                "Action": permissions
            })

        # Add the default permissions for logging.
        statements.append({
            "Sid": UTILS.UUID().replace('-', ''),
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        })

        # Merge the statements for the same resource.
        mergedStatements = self.MergeStatements(statements)
        mergedStatements += statements
        
        # Update the policy document.
        self._policy_document['Statement'] = mergedStatements

        # Check if the policy already has the permissions
        if defaultVersion:
            if defaultVersion.GetStatement() == mergedStatements:
                LOG.Print(f"@: Policy {self._name} already has the permissions.")
                return

        # Create a new version of the policy with the updated permissions
        try:
            LOG.Print(
                f"@: Creating version policy={self._policy_name}.", 
                self._policy_document)
            
            iam_client.create_policy_version(
                PolicyArn= self._policy_arn,
                PolicyDocument= json.dumps(self._policy_document),
                SetAsDefault= True)
            
            '''
            result:
                PolicyVersion:
                    VersionId: v2
                    IsDefaultVersion: true
                    CreateDate: '2024-04-18 23:24:35+00:00'
                ResponseMetadata:
                    RequestId: 9e6fb7c3-7ea4-4c62-8849-2161c0b39e08
                    HTTPStatusCode: 200
                    HTTPHeaders:
                    date: Thu, 18 Apr 2024 23:24:35 GMT
                    x-amzn-requestid: 9e6fb7c3-7ea4-4c62-8849-2161c0b39e08
                    content-type: text/xml
                    content-length: '452'
                    RetryAttempts: 0
            '''
            
        except Exception as e:
            LOG.Print(
                f"@: Error updating policy {self._policy_name}: {e}", 
                self._policy_document['Statement'])
            raise

        LOG.Print(f'@: Updated policy {self._policy_name} to include {permissions}.')


    def GetVersions(self):
        '''👉️ Returns the ARNs of all versions of the policy.'''
        versions = iam_client.list_policy_versions(PolicyArn= self.GetArn())
        versions = STRUCT(versions)
        
        ret = [
            IAM_POLICY_VERSION(
                meta= meta, 
                client= iam_client, 
                policy= self)
            for meta in versions.GetList('Versions')
        ]

        LOG.Print(self.GetVersions, f"{ret=}")
        return ret
    