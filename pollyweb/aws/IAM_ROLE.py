
import json
from AWS_RETRY import RetryWithBackoff
from IAM_POLICY import IAM_POLICY
from pollyweb.utils.PRINTABLE import PRINTABLE
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS
from pollyweb.utils.LOG import LOG

import boto3
iam_client = boto3.client('iam')


class IAM_ROLE(PRINTABLE):

    ICON = '🔒'


    def __init__(self, 
        name: str, 
        cached: bool= False
    ):
        super().__init__(name)
        self._name = name

        # Cache the role Arns.
        self._cached = cached
        if cached: self._cache = UTILS.CACHE()


    def RequireName(self):  
        return self._name


    def Exists(self):
        '''👉️ Checks if the IAM role exists.'''
        role_name = self._name

        try:
            response = iam_client.get_role(RoleName= role_name)
            return True

        except iam_client.exceptions.NoSuchEntityException:
            return False


    def RequireArn(self):
        arn = self.GetArn()
        if not arn:
            LOG.RaiseException(f"@: Role {self.RequireName()} does not exist.")
        return arn


    def GetArn(self):
        '''👉️ Checks if the IAM role exists.'''

        LOG.Print(f'@: {self._name=} [cached={self._cached}]')

        if hasattr(self, '_arn'):
            if self._arn:
                return self._arn

        # Check the cache for a cached ARN.
        cacheKey = f'Arn.{self._name}'
        if self._cached:
            arn = self._cache.Get(cacheKey)
            if arn: 
                self._arn = arn
                return arn

        # Check if the role exists.
        role_name = self._name
        try:
            response = iam_client.get_role(RoleName= role_name)
            LOG.Print(f"@: Role {role_name} exists.")
            #LOG.Print(f"@: Role Details: {response['Role']}")
            
            # return the ARN of the role
            arn = str(response['Role']['Arn'])

            # Cache the ARN.
            if self._cached:
                self._cache.Set(cacheKey, arn)

            self._arn = arn
            return arn

        except iam_client.exceptions.NoSuchEntityException:
            LOG.Print(f"@: Role {role_name} does not exist.")
            return None

        except Exception as e:
            LOG.RaiseException(f"@: Error checking role: {e}")


    def EnsureForLambda(self):
        '''👉️ Ensures that the IAM role exists for Lambda.'''
        if not self.Exists():
            self.CreateForLambda()
        return self.RequireArn()


    def CreateForService(self, service:str):
        '''👉️ Creates an IAM role for a service,
            and returns the ARN of the role.'''
        
        LOG.Print(f'@ {service=}')
        
        role_name:str = self._name

        # Trust policy allowing the service to assume the role
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": f"{service}.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        # Create the role
        try:
            create_role_response = iam_client.create_role(
                RoleName= role_name,
                AssumeRolePolicyDocument= json.dumps(trust_policy),
                Description= 'Service execution role created via Boto3',
                Path="/service-role/")
            
            role_arn = create_role_response['Role']['Arn']
            LOG.Print(f"@: Created role ARN: {role_arn}")

            # Wait until the role is ready
            self._WaitUntilReady(
                serviceRoles=[service])

            return str(role_arn)
        
        except iam_client.exceptions.EntityAlreadyExistsException:
            LOG.RaiseException(f"@: The role {role_name} already exists.")


    def CreateForLambda(self):
        '''👉️ Creates an IAM role for Lambda,
            and returns the ARN of the role.'''
        
        role_name:str = self._name

        # Trust policy allowing Lambda to assume the role
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }

        # Create the role
        try:
            create_role_response = iam_client.create_role(
                RoleName= role_name,
                AssumeRolePolicyDocument= json.dumps(trust_policy),
                Description= 'Lambda execution role created via Boto3')
            
            role_arn = create_role_response['Role']['Arn']
            LOG.Print(f"@: Created role ARN: {role_arn}")

            # Attach the AWSLambdaBasicExecutionRole policy
            policy_arn = 'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
            iam_client.attach_role_policy(
                RoleName= role_name,
                PolicyArn= policy_arn)
            
            LOG.Print("@: Attached policy to the role.")

            # Wait until the role is ready
            self._WaitUntilReady()
            self.EnsurePolicy()

            return str(role_arn)
        
        except iam_client.exceptions.EntityAlreadyExistsException:
            LOG.RaiseException(f"@: The role {role_name} already exists.")


    def AssertAssumesServiceRole(self, service:str):
        if not self.AssumesServiceRole(service):
            LOG.RaiseValidationException(
                f'Role {self.RequireName()} does not assume the service role {service}')


    def AssumesServiceRole(self, service:str):
        '''👉️ Checks if the IAM role assumes the service role.'''
        role_name = self.RequireName()

        role_details = iam_client.get_role(RoleName=role_name)
        role_details = STRUCT(role_details)
        
        role = role_details.RequireStruct('Role')
        #LOG.Print(f"@: Role details: {role}")

        policy_document = role.RequireStruct('AssumeRolePolicyDocument')

        if policy_document.ContainsAtt('Statement'):
            statement = policy_document.RequireList('Statement')
            #LOG.Print(f"@: Statement={statement}")

            if any(
                s['Principal'].get('Service') == f'{service}.amazonaws.com' and s['Action'] == 'sts:AssumeRole' 
                for s in statement
            ):
                LOG.Print(f"@: Assumes service role {service}")
                return True
            
        LOG.Print(f"@: Does not assume service role {service}")
        return False


    @RetryWithBackoff(codes=['NoSuchEntity'])
    def _WaitUntilReady(self, 
        serviceRoles:list[str]=[]
    ):
        '''👉️ Waits for the IAM role to be ready to be assumed by Lambda.'''

        role_name = self._name

        role_details = iam_client.get_role(RoleName=role_name)
        
        role_details = STRUCT(role_details)
        role = role_details.RequireStruct('Role')

        if len(serviceRoles) == 0:
            return
    
        policy_document = role.RequireStruct('AssumeRolePolicyDocument')

        if policy_document.ContainsAtt('Statement'):
            statement = policy_document.RequireList('Statement')
            #LOG.Print(f"@: Statement={statement}")

            for service in serviceRoles:
                if any(
                    s['Principal'].get('Service') == f'{service}.amazonaws.com' and s['Action'] == 'sts:AssumeRole' 
                    for s in statement
                ):
                    continue
                LOG.RaiseValidationException(f'Service role not ready for: {service}')

            LOG.Print(
                "@: IAM.Role and trust relationship are correctly configured.", 
                policy_document, 
                role)
            return
            
        LOG.RaiseValidationException('Role not ready')


    def EnsurePolicy(self):
        '''👉️ Ensures that the IAM policy exists for the role.'''
        LOG.Print(f'@: policy for role {self.RequireName()} [cached={self._cached}]')

        policy = self.GetPolicy()
        roleName = self.RequireName()
        
        policy.EnsureExists(roleName= roleName)
        policy.AttachToRole(roleName= roleName)
        return policy


    def DetachPolicy(self):
        '''👉️ Detaches a policy from the IAM role.'''
        policy = self.GetPolicy()
        policy_arn = policy.GetArn()
        role_name = self.RequireName()

        iam_client.detach_role_policy(
            RoleName= role_name, 
            PolicyArn= policy_arn)
        
        LOG.Print(f"@: Detached policy {policy_arn} from role {role_name}")



    def GetPolicy(self):
        '''👉️ Gets the IAM policy for the role.'''
        LOG.Print(f'@: policy for role {self.RequireName()}')

        role_name = self.RequireName()
        policy_name = f"{role_name}-policy"

        policy = IAM_POLICY(policy_name)
        return policy
        

    def SetPermissions(self, 
        permissions: list[str] | dict[str, list[str]] = [],
        statements: list[dict] = []
    ):
        '''👉️ Sets the permissions for the IAM role.'''
        
        policy = self.EnsurePolicy()
        
        policy.SetPermissions(
            permissions= permissions,
            statements= statements)
        
        policy.AttachToRole(
            roleName= self.RequireName())


    def Delete(self):
        '''👉️ Deletes the IAM role.'''
        role_name = self.RequireName()

        self.DetachAllPolicies()

        try:
            iam_client.delete_role(RoleName= role_name)
            LOG.Print(f"@: Deleted role {role_name}")

        except iam_client.exceptions.NoSuchEntityException:
            LOG.Print(f"@: Role {role_name} does not exist.")


    def GetAttachedPolicyArns(self):
        '''👉️ Gets the ARNs of the attached policies.'''
        role_name = self.RequireName()

        response = iam_client.list_attached_role_policies(RoleName= role_name)
        policy_arns = [
            str(p['PolicyArn']) 
            for p in response['AttachedPolicies']
        ]
        LOG.Print(f"@: Attached policies: {policy_arns}")
        return policy_arns


    def DetachAllPolicies(self):
        '''👉️ Detaches all policies from the IAM role.'''
        role_name = self.RequireName()

        policy_arns = self.GetAttachedPolicyArns()
        for policy_arn in policy_arns:
            iam_client.detach_role_policy(
                RoleName= role_name, 
                PolicyArn= policy_arn)
            LOG.Print(f"@: Detached policy {policy_arn} from role {role_name}")


    def AttachPolicies(self, policy_arns:list[str]):
        '''👉️ Attaches policies to the IAM role.
        
        Examples:
            * AmazonS3FullAccess
            * mazonEC2ContainerRegistryPowerUser
            * CloudWatchLogsFullAccess
            * AWSCodeBuildAdminAccess
        '''
        for policy_arn in policy_arns:
            self.AttachPolicy(policy_arn)


    def AttachPolicy(self, policy_arn:str):
        '''👉️ Attaches a policy to the IAM role.
    
        Examples:
            * AmazonS3FullAccess
            * mazonEC2ContainerRegistryPowerUser
            * CloudWatchLogsFullAccess
            * AWSCodeBuildAdminAccess'''
        
        role_name = self.RequireName()

        if not policy_arn.startswith('arn:aws:iam::aws:policy/'):
            policy_arn = f"arn:aws:iam::aws:policy/{policy_arn}"

        if policy_arn in self.GetAttachedPolicyArns():
            return

        iam_client.attach_role_policy(
            RoleName= role_name, 
            PolicyArn= policy_arn)
        
        LOG.Print(f"@: Attached policy {policy_arn} to role {role_name}")