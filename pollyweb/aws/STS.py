# 📚 STS

from PW_UTILS.LOG import LOG
from PW_UTILS.STRUCT import STRUCT

import boto3

from PW_UTILS.UTILS import UTILS
sts = None
def get_sts():
    '''👉️ Returns the STS client.'''
    global sts
    if not sts:
        try: 
            sts = boto3.client('sts')
        except Exception as e:
            LOG.RaiseException(
                f'Consider "isengard assume nlweb": {e}')
    return sts

class STS():

    
    @classmethod
    def RequireAccount(cls, number:str, name:str=None):
        from PW_UTILS.TESTS import TESTS
        current_account = cls.GetAccountNumber()
        
        TESTS.AssertEqual(
            given= current_account,
            expect= number,
            msg= f'Log in into the [{name}] account. Consider: isengardcli assume {name} --region eu-west-1 --nocache')
        
        LOG.Print(f'✅ Current Account: {current_account}')


    @classmethod
    def EnsureAlias(cls, alias:str):
        from PW_UTILS.TESTS import TESTS
        current_account = cls.GetAccountAlias()
        
        TESTS.AssertEqual(
            given= current_account,
            expect= alias,
            msg= f'Log in into the [{alias}] account. Consider: isengardcli assume {alias} --region eu-west-1 --nocache')
        
        print(f'✅ Current Account: {current_account}')


    @classmethod
    def GetAccountNumber(cls) -> str|None:

        # Get the caller identity
        try:
            sts = get_sts()
        except Exception as e:
            return None
        
        caller_identity = sts.get_caller_identity()
        caller_identity = STRUCT(caller_identity)

        # Extract the account number from the response
        account_number = caller_identity.RequireStr('Account')

        LOG.Print('@: return', account_number)
        return account_number
    

    @classmethod
    def GetAccountAlias(cls):
        '''👉️ Returns the account Alias.'''
        LOG.Print('@')
       
        # Use STS to get the account ID
        number = cls.GetAccountNumber()
        if not number:
            return None

        # Create a session using the credentials and 
        # configuration (such as region) from the environment
        session = boto3.session.Session()

        # Use IAM to list account aliases
        iam_client = session.client('iam')
        aliases = iam_client.list_account_aliases()['AccountAliases']
        
        # Return the first account alias if any exist, otherwise return the account ID
        if aliases:
            ret = aliases[0]
            return ret
        
        # Not found!
        # Try to get the account alias from the account ID on Isengard
        from PW_UTILS.UTILS import UTILS
        details = UTILS.OS().Execute(['isengardcli', 'cat', number])
        struct = UTILS.FromYamlStruct(details)
        alias = struct.RequireStr('Email').replace('@amazon.com', '')
        return alias

        # No alias found.
        LOG.RaiseException(f"No alias found for account ID {number}")
    

    @classmethod
    def GetRegion(cls):
        # Create a session using the default configuration (could specify credentials here)
        session = boto3.session.Session()        
        return session.region_name


    @classmethod
    def GetCliProfile(cls):
        # Check if AWS_PROFILE environment variable is set
        import os
        aws_profile = os.environ.get('AWS_PROFILE')
        
        if aws_profile:
            return aws_profile
        else:
            LOG.RaiseException(f"AWS_PROFILE environment variable not set")
            return 'default'  # AWS CLI defaults to the 'default' profile if AWS_PROFILE is not set


    @classmethod
    def InAccountNumber(cls, number:str):
        '''👉️ Returns true if the code is running in the specified AWS account.'''
        current = cls.GetAccountNumber()
        return str(current) == str(number) 
    

    @classmethod
    def InAccountAlias(cls, alias:str):
        '''👉️ Returns true if the code is running in the specified AWS account.'''
        current = cls.GetAccountAlias()
        #print(f'GetAccountAlias.current: {current}')
        return str(current) == str(alias) 
    

    @classmethod
    def IsengardLogin(cls, alias:str, region:str):
        print(f' STS.IsengardLogin()')
        cmd = '/opt/homebrew/bin/isengardcli'
        cmds = [cmd, 'assume', alias, '--region', region, '--nocache']
        from PW_UTILS.UTILS import UTILS
        str = UTILS.OS().ExecuteShellLess(cmds)
        print(' STS.IsengardLogin', str)
        

    @classmethod
    def EnsureIsengardAccount(cls, number:str, alias:str, region:str):
        '''👉️ Ensure that the code is running in the specified AWS account
        * if not in the account, log in using the Isengard CLI.
        
        Arguments:
            * `number` {str} -- The account number.
            * `alias` {str} -- The account alias.
            * `region` {str} -- The region to use.  

        Example:
            AWS.STS().EnsureIsengardAccount(
                number= '123456789012', 
                alias= 'nlweb', 
                region= 'eu-west-1')
        '''
        print(f'🤖 Verifying if in the account [{alias}]...')

        # Check if in the account.
        if not cls.InAccountNumber(number):

            # Login into the right account.
            cls.IsengardLogin(
                alias= alias, 
                region= region)
            
        # Block if the command was not sucessful.
        cls.RequireAccount(
            number= number, 
            name= alias)
        

    @classmethod
    def EnsureIsengardAlias(cls, alias:str, region:str):
        ''' 👉️ Ensure that the code is running in the specified AWS account
        * if not in the account, log in using the Isengard CLI.
        
        Arguments:
            * `alias` {str} -- The account alias.
            * `region` {str} -- The region to use.  

        Example:
            AWS.STS().EnsureIsengardAlias(
                alias= 'nlweb', 
                region= 'eu-west-1')
        '''
        print(f'🤖 Verifying if in the account [{alias}]...')

        # Check if in the account.
        if not cls.InAccountAlias(alias):

            # Login into the right account.
            cls.IsengardLogin(
                alias= alias, 
                region= region)
            
        # Block if the command was not sucessful.
        if not cls.InAccountAlias(alias):
            LOG.RaiseException(f'Not in the account [{alias}]')

        print(f'✅ Current Account: {alias}')

