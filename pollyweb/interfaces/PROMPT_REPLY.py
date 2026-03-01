from PW import PW
from PROMPT import PROMPT
from PROMPT_OPTION import PROMPT_OPTION
from ..utils import UTILS
from ..utils import STRUCT
from ..utils import LOG
     


class PROMPT_REPLY(STRUCT):
    '''
    {
        "PromptID": "<uuid>",
        "Result": "OK",
        "Answer": "1"|1|["1","2"],"[1,2]",
        "Shared": {...}       
    }
    '''

    @staticmethod
    def Reply(prompt:PROMPT, 
        result:str, answer:str=None, data:dict=None,
        dontValidate=False):
        '''👉 Creates a new PROMPT_RESPONSE based on the PROMPT_REQUEST.'''

        LOG.Print('💬 PROMPT.REPLY.Reply()', 
            f'{result=}', f'{answer=}', f'{dontValidate=}',
            f'shared= ', data)

        PROMPT.AssertClass(prompt, require=True)
        UTILS.AssertIsType(result, str, require=True)

        format = prompt.RequireFormat()
        if not dontValidate:

            if format in ['AMOUNT','QUANTITY','RATE']:
                UTILS.AssertIsType(answer, int, 
                    msg='Answer should a number')
                
            elif format in ['INT','OTP']:
                UTILS.AssertIsAnyType(answer, [int,str], 
                    msg='Answer should a number or string of numbers')
                
            elif format in ['MANY']:
                UTILS.AssertIsAnyType(answer, [str,list], 
                    msg='Answer should be a string or a list.')
                
            else:
                UTILS.AssertIsType(answer, str, 
                    msg='Answer should be a string.')
        
        item = {
            "PromptID": prompt.RequirePromptID(),
            "Result": result,
            "Answer": answer
        }
        
        if not STRUCT(data).IsMissingOrEmpty():
            item['Data'] = data
        
        reply = PROMPT_REPLY(item)
        reply.VerifyReply()

        format = prompt.RequireFormat()
        reply.VerifyPrompt(format)

        return reply


    def RequirePromptID(self) -> str:
        return self.RequireUUID('PromptID')
            
    def RequireResult(self) -> str:
        return self.RequireStr('Result')

    def GetAnswer(self, set:any=None) -> any:
        return self.GetAtt('Answer', set=set)
    
    def GetData(self) -> dict:
        return self.GetStruct('Data')
    
    def SetData(self, set:dict):
        if set != None: self.RemoveAtt('Data', safe=True)
        else: self.GetStruct('Data', set=set)
        
    def RequireAnswer(self, set:str=None) -> any:
        '''👉 Returns the answer to the prompt.'''
        return self.RequireAtt('Answer', set=set)
    
    def RequireAnswerStr(self, set:str=None) -> str:
        '''👉 Returns the string answer to the prompt.'''
        return self.RequireStr('Answer', set=set)
    

    def VerifyReply(self):
        LOG.Print('💬 PROMPT.REPLY.VerifyReply()', self)
        self.RequirePromptID()
        self.RequireResult()


    def VerifyPrompt(self, format:str):
        '''👉 Verifies if the result and answer are valid for the prompt.
        * Docs: https://quip.com/CDrjAxNKwLpI#temp:C:KSc3b3a2537dfeb48d2ad2848477'''
        
        # From here, verify the reply based on the prompt type.
        result = self.RequireResult()
        answer = self.GetAnswer()
        shared = self.GetData()
        msg = f'Verify {format=}'

        LOG.Print(
            f'💬✅ PROMPT.REPLY.VerifyPrompt()', 
            f'domain={PW.CONFIG().RequireDomain()}',
            f'{format=}', 
            f'{result=}', 
            f'{answer=}',
            f'shared= ', shared)
        
        if format == 'SHARE' and shared==None:
            LOG.RaiseException('SHARE requires share!')

        if format in ['CONFIRM']:
            # Override the result with the answer, if necessary.
            if not UTILS.IsNoneOrEmpty(answer):
                result = answer
            UTILS.AssertIsAnyValue(result, ['YES', 'NO', 'CANCEL'], msg=msg)

        if format in ['INFO']:
            UTILS.AssertIsAnyValue(result, ['OK'], msg=msg)

        if format in ['AMOUNT', 'EAN', 'INT', 'QUANTITY', 'OTP', 'RATE']:
            self.VerifyNumber(result, format=format, check=msg)
        
        elif format in ['DATE', 'TIME', 'UNTIL']:
            self.VerifyDate(result, check=msg)

        elif format in ['LOCATION', 'TRACK']:
            self.VerifyCoordinates(result, msg=msg)

        elif format in ['SELFIE']:
            self.VerifySelfie(result, msg=msg)

        elif format in ['SCAN']:
            self.VerifyScan(result, msg=msg)

        elif format in ['UPLOAD']:
            self.VerifyUpload(result, msg=msg)

        elif format in ['ONE']:
            self.VerifyOne(result, msg=msg)

        elif format in ['MANY']:
            self.VerifyMany(result, msg=msg)

        elif format in ['DOWNLOAD']:
            self.VerifyDownload(result, msg=msg)


    def VerifyNumber(self, result:str, format:str, check:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=check)
        if result != 'OK':
            return 

        answer = self.GetAnswer()

        # Convert to an int/float.
        if format == 'AMOUNT':
            value = float(answer)
            self.RequireAnswer(value)
        else:
            # Test, but use the original answer because we need numbers 
            # starting with 0, for example for UK phone numbers.
            self.RequireAnswer(answer)
            value = int(answer)

        # Barcodes muts be either 8 or 13 digits.
        if format == 'EAN':
            answer = str(answer).strip().replace(',', '').replace('.', '')
            UTILS.AssertIsAnyValue(len(answer), [8, 12])

        # OTPs must have 6 digits.
        if format == 'OTP':
            UTILS.AssertInterval(value, 0, 999999)

        # Rates can only be 1,2,3,4,5.
        if format == 'RATE':
            UTILS.AssertIsAnyValue(value, [1, 2, 3, 4, 5], 
                msg= 'Invalid rate!')


    def VerifyDate(self, result:str, check:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=check)
        if result != 'OK':
            return 
        
        answer = self.RequireAnswerStr()
    
        # Convert the answer to a date.
        if not answer.endswith('Z'):
            LOG.RaiseException('Provide a date-time in UTC, ending with Z')
        
        UTILS.ParseTimestamp(answer)


    def VerifyCoordinates(self, result:str, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['YES', 'NO', 'CANCEL'], msg=msg)
        if result != 'OK':
            return
    
        answer = self.RequireAnswerStr()

        # Convert the answer to coordinates, then to floats.
        coordinates = answer.split(',')
        UTILS.AssertLenght(coordinates, 2)
        float(coordinates[0])
        float(coordinates[1])


    def VerifySelfie(self, result:str, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=msg)
        if result != 'OK':
            return 
        
        answer = self.GetAnswer()

        # This should be a match probability (percentage).
        value = float(answer)
        UTILS.AssertInterval(value, 0, 100)


    def VerifyScan(self, result:str, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=msg)
        if result != 'OK':
            return 
        
        answer = self.RequireAnswerStr()

        # Verify if it's a QR code from the PW world.
        if not answer.startswith('🤝'):
            LOG.RaiseException('PW QR codes must start with 🤝!')


    def VerifyUpload(self, result:str, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=msg)
        if result != 'OK':
            return 
        
        answer = self.GetAnswer()

        # Verify if it's a UUID of a file uploaded.
        UTILS.AssertLenght(str(answer), 36)


    def VerifyOne(self, result:str, options:list[str]=None, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=msg)
        if result != 'OK':
            return 
        
        # Match any of the options.
        if options != None:
            option = self.GetAnswer()
            UTILS.AssertIsAnyValue(option, options, msg=msg)
        

    def VerifyMany(self, result:str, options:list[str]=None, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=msg)
        if result != 'OK':
            return 

        # Get answers
        answer = self.RequireAnswer()
        answers = PROMPT_OPTION.ParseOptions(answer)
        answerIDs = answers

        # Match any of the selections with any of the options.
        if options != None:
            for answerID in answerIDs:
                UTILS.AssertIsAnyValue(answerID, options)


    def VerifyDownload(self, result:str, options:list[str]=None, msg:str=None):
        UTILS.AssertIsAnyValue(result, ['OK', 'CANCEL'], msg=msg)
        if result != 'OK':
            return 

        # Answers are optional for downloads.
        optionID = self.GetAnswer()

        if not optionID:
            return 

        # Match any of the options.
        if options != None:
            UTILS.AssertIsAnyValue(optionID, options)