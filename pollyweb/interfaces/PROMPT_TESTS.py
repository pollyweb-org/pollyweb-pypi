from .PROMPT_OPTION import PROMPT_OPTION
from .PROMPT import PROMPT
from pollyweb import TESTS
from ..utils import LOG
import json


class PROMPT_TESTS(PROMPT):
    


    @classmethod
    def TestParseOptions(cls):

        TESTS.AssertEqual(PROMPT_OPTION.ParseOptions(None), None)
        TESTS.AssertEqual(PROMPT_OPTION.ParseOptions("[ a , b ]"), ['a', 'b'])
        TESTS.AssertEqual(PROMPT_OPTION.ParseOptions([' a ',' b ']), ['a', 'b'])
        TESTS.AssertEqual(PROMPT_OPTION.ParseOptions([1,2]), ['1','2'])
        TESTS.AssertEqual(['1:a','2:b'], ['1:a','2:b'])

        #with TESTS.AssertValidation('Only str or lists are allowed?'):
        PROMPT_OPTION.ParseOptions({'a':'x','b':'y'})    

        with TESTS.AssertValidation('Avoid duplicates?'):
            PROMPT_OPTION.ParseOptions("[ a,a ]")   


    @classmethod
    def TestNew(cls):

        p = PROMPT.New(format= "INFO", message= "m")
        p = PROMPT.New(format= "ONE", message= "m", options='1,2')
        p = PROMPT.New(format= "ONE", message= "m", options='a,b')

        p = PROMPT.New(format= "INFO", message= "m", appendix='<uuid>')

        with TESTS.AssertValidation('Format is valid?'):
            p = PROMPT.New(format= "f", message= "m")

        with TESTS.AssertValidation('Options is empty?'):
            p = PROMPT.New(format= "INFO", message= "m", options='a,b')

        p = PROMPT.New(
            format= "ONE",
            message= "Which credit card to use?", 
            options= 'Personal, Business',
            appendix= '<uuid>',
            default= 'Personal')

        p.RemoveAtt('PromptID')
        TESTS.AssertEqual(p, {
            'Format': 'ONE', 
            'Message': 'Which credit card to use?', 
            'Options': ['Personal', 'Business'],
            'Appendix': '<uuid>',
            'Results': ['OK', 'CANCEL'],
            'Default': 'Personal'
        })
        
    
    @classmethod
    def TestRequireFormat(cls):
        p = PROMPT.New(format= "INFO", message= "m")
        TESTS.AssertEqual(p.RequireFormat(), 'INFO')
    

    @classmethod
    def TestRequireMessage(cls):
        p = PROMPT.New(format= "INFO", message= "m")
        TESTS.AssertEqual(p.RequireMessage(), 'm')
    

    @classmethod
    def TestGetAppendix(cls):

        p = PROMPT.New(format= "INFO", message= "m")

        TESTS.AssertEqual(p.GetAppendix(), None)

        with TESTS.AssertValidation():
            p.RequireAppendix()
    

    @classmethod
    def TestRequireOptions(cls):

        p = PROMPT.New(format= "ONE", message= "m", options='1:a,2:b')
        TESTS.AssertEqual(p.RequireOptions(), ['1:a','2:b'])

        p = PROMPT.New(format= "INFO", message= "m")
        with TESTS.AssertValidation():
            p.RequireOptions()


    @classmethod
    def TestRequireOptionList(cls):

        p = PROMPT.New(
            format= "ONE", 
            message= "m", 
            options='1:a,2:b')

        TESTS.AssertEqual(
            given= json.dumps(p.RequireOptionList()), 
            expect= json.dumps(['1:a','2:b']))
        
        TESTS.AssertClass(p.RequireOptionList()[0], str)    

        p = PROMPT.New(format= "INFO", message= "m")
        with TESTS.AssertValidation():
            p.RequireOptionList()


    @classmethod
    def TestSetOptions(cls):

        p = PROMPT.New(
            format= "ONE", 
            message= "m", 
            options=[3,4])
        TESTS.AssertEqual(p.RequireOptions(), ['3','4'])

        p.SetOptions('1:a,2:b', override=True)
        TESTS.AssertEqual(p.RequireOptions(), ['1:a','2:b'])

        with TESTS.AssertValidation('Avoid duplicates?'):
            TESTS.AssertEqual(p.RequireOptions(), ['a','a'])

        with TESTS.AssertValidation('Need to explicitly override?'):
            p.SetOptions('1:a,2:b')

        with TESTS.AssertValidation('Empty list of options only allowed for Download'):
            p = PROMPT.New(
                format= "ONE", 
                message= "m", 
                options=[])

        p = PROMPT.New(
            format= "DOWNLOAD", 
            message= "m", options=[], 
            appendix= '<uuid>')
        

    @classmethod
    def TestVerifyPrompt(cls):

        with TESTS.AssertValidation('Unknown format.'): 
            PROMPT.New(format= "f", message= "m").VerifyPrompt()

        # Assert required message.
        PROMPT.New(format= "INFO", message= "m").VerifyPrompt()
        with TESTS.AssertValidation('Missing message'):
            PROMPT.New(format= "INFO", message= '').VerifyPrompt()
        with TESTS.AssertValidation('Missing message'):
            PROMPT.New(format= "INFO", message= None).VerifyPrompt()

        # Assert required options for ONE.
        PROMPT.New(format= "ONE", message= 'm', options=[1]).VerifyPrompt()
        with TESTS.AssertValidation('ONE has options?'):
            PROMPT.New(format= "ONE", message= 'm').VerifyPrompt()
        with TESTS.AssertValidation('ONE has at list one option?'):
            PROMPT.New(format= "ONE", message= 'm', options=[]).VerifyPrompt()

        # Assert CONFIRM.
        PROMPT.New(format= "CONFIRM", message= "m").VerifyPrompt()

        # Assert AMOUNT.
        PROMPT.New(format= "AMOUNT", message= "m").VerifyPrompt()
        
        # Assert SELFIE.
        PROMPT.New(format= "SELFIE", message= "m", locator='asd').VerifyPrompt()
        with TESTS.AssertValidation():
            PROMPT.New(format= "SELFIE", message= "m").VerifyPrompt()
        with TESTS.AssertValidation():
            PROMPT.New(format= "SELFIE", message= "m", locator='').VerifyPrompt()

        # Assert Download.
        PROMPT.New(format= "DOWNLOAD", message= "m", appendix='<uuid>').VerifyPrompt()
        PROMPT.New(format= "DOWNLOAD", message= "m", appendix='<uuid>', options=[]).VerifyPrompt()
        PROMPT.New(format= "DOWNLOAD", message= "m", appendix='<uuid>', options=[1,2]).VerifyPrompt()
        with TESTS.AssertValidation('Missing appendix'):
            PROMPT.New(format= "DOWNLOAD", message= "m", options=[1,2]).VerifyPrompt()
        with TESTS.AssertValidation('Missing appendix'):
            PROMPT.New(format= "DOWNLOAD", message= "m").VerifyPrompt()

        # Assert default value for lists.
        PROMPT.New(format= "ONE", message= "m", options= ['x','y'], default='x').VerifyPrompt()
        PROMPT.New(format= "MANY", message= "m", options= ['x','y'], default='x').VerifyPrompt()
        with TESTS.AssertValidation('Default not in options of ONE!'):
            PROMPT.New(format= "ONE", message= "m", options= ['x','y'], default='z').VerifyPrompt()
        with TESTS.AssertValidation('Default not in options of MANY!'):
            PROMPT.New(format= "MANY", message= "m", options= ['x','y'], default='z').VerifyPrompt()
        
        # Assert default value for INT.
        PROMPT.New(format= 'INT', message='m', default= '123')
        with TESTS.AssertValidation('INT default a float?!'):
            PROMPT.New(format= 'INT', message='m', default= '123.45').VerifyPrompt()
        with TESTS.AssertValidation('INT default a string?!'):
            PROMPT.New(format= 'INT', message='m', default= 'x').VerifyPrompt()
            
        # Assert default value for QUANTITY.
        PROMPT.New(format= 'QUANTITY', message='m', default= '123')
        with TESTS.AssertValidation('QUANTITY default a float?!'):
            PROMPT.New(format= 'QUANTITY', message='m', default= '123.45').VerifyPrompt()
        with TESTS.AssertValidation('QUANTITY default a string?!'):
            PROMPT.New(format= 'QUANTITY', message='m', default= 'x').VerifyPrompt()

        # Assert default value for AMOUNT.
        PROMPT.New(format= 'AMOUNT', message='m', default= '123')
        PROMPT.New(format= 'AMOUNT', message='m', default= '123.45').VerifyPrompt()
        with TESTS.AssertValidation('AMOUNT default a string?!'):
            PROMPT.New(format= 'AMOUNT', message='m', default= 'x').VerifyPrompt()
        
        # Assert default value for others.
        with TESTS.AssertValidation('EAN default?!'):
            PROMPT.New(format= 'EAN', message='m', default= '1').VerifyPrompt()
        with TESTS.AssertValidation('OTP default?!'):
            PROMPT.New(format= 'OTP', message='m', default= '1').VerifyPrompt()
        with TESTS.AssertValidation('RATE default?!'):
            PROMPT.New(format= 'RATE', message='m', default= '1').VerifyPrompt()
        

    @classmethod
    def TestDefaultInOptions(cls):
        with TESTS.AssertValidation('Invalid default'):
            PROMPT.New(
                format= "ONE",
                message= "Which credit card to use?", 
                options= 'Personal, Business',
                default= 'SomethingElse')
                    

    @classmethod
    def TestAllPrompt(cls):
        LOG.Print('PROMPT_TESTS.TestAllPrompt() ==============================')

        cls.TestParseOptions()
        cls.TestNew()
        cls.TestRequireFormat()
        cls.TestRequireMessage()
        cls.TestGetAppendix()
        cls.TestRequireOptions()
        cls.TestRequireOptionList()
        cls.TestSetOptions()
        cls.TestVerifyPrompt()
        cls.TestDefaultInOptions()