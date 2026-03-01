from aws.APPCONFIG_REAL_DEPLOY import APPCONFIG_REAL_DEPLOY
from DEPLOYER_EXEC_TASK import DEPLOYER_EXEC_TASK
from aws.LAMBDA_FUNCTION import LAMBDA_FUNCTION
from aws.LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from LOG import LOG
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.UTILS import UTILS

class DEPLOYER_EXEC_APPCONFIG(DEPLOYER_EXEC_TASK):
    

    def OnValidate(self):
        '''👉 Validates if the AppConfig definitions are OK.'''

        LOG.Print('@', self)
        
        self.VerifyAlienParameters([
            'Validators',
            'Format',
            'Content'
        ])

        self.VerifyMissingParameters([
            'Format',
            'Content'
        ])

        validators = self.task.GetListParam(
            key= 'Validators', 
            itemType= str)
                
        # Add the stack to the validator, if necessary.
        stack = self.task.RequireStackName()

        self.Validators: list[str] = []
        for name in validators:

            if '-' not in name:
                reference = f'{stack}-{name}'
            else:
                reference = name

            # Test the full name from the reference.
            self.taskDict[reference].RequireFullName()

            self.Validators.append(reference)

        # Parse the format.
        self.Format = self.task.RequireStringParam('Format')
        UTILS.AssertIsAnyValue(self.Format, ['TXT', 'JSON', 'YAML'])

        # Parse the content.
        if self.Format == 'TXT':
            self.Content = self.task.RequireStringParam('Content')
        elif self.Format == 'YAML':
            self.Content = self.task.RequireDictParam('Content')
            self.Content = UTILS.ToYaml(self.Content)
        elif self.Format == 'JSON':
            self.Content = self.task.RequireDictParam('Content')
            self.Content = UTILS.ToJson(self.Content)


    def OnExecute(self):
        '''👉 Deploys AppConfig.'''

        LOG.Print('@', 
            'validators=', self.Validators, self)

        validators: list[LAMBDA_FUNCTION_REAL] = []
        for reference in self.Validators:

            LOG.Print(f'@ Validator: {reference}')

            # Get the full name from the reference.
            result = self.taskDict[reference].RequireResult()
            result = STRUCT(result)
            arn = result['Arn']
            name = result['Name']
            fn = LAMBDA_FUNCTION_REAL(name)
            
            # Add to the validators.
            validators.append(fn)

        # Create the app.
        app = APPCONFIG_REAL_DEPLOY().CreateApp(
            name= self.task.RequireFullName(),
            validators= validators)

        # Set a value.
        app.SetValue(
            content= self.Content,
            format= self.Format)
