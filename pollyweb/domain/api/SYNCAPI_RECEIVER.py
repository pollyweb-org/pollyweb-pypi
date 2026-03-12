# 📚 RECEIVER (part of SYNCAPI)

import json


from pollyweb import UTILS
from NLWEB import NLWEB
from DOMAIN import DOMAIN
from PW_AWS.AWS import AWS
from MSG import MSG
from WEB import WEB
from SYNCAPI_RECEIVER_MAP import SYNCAPI_RECEIVER_MAP
from pollyweb import LOG


class ApiException(Exception):
    pass


class AnotherException(Exception):
    pass


class SYNCAPI_RECEIVER:


    @classmethod
    def MAP(cls):
        return SYNCAPI_RECEIVER_MAP()


    def __init__(self):
        self._timer = UTILS.Timer()


    def _elapsed(self):
        return self._timer.Elapsed()
            


    # REQUEST { hostname }
    # RESPONSE: str
    def _invokeDkimReader(self, envelope, checks:list[str]):
        LOG.Print(
            f'🚀👉 SYNCAPI.RECEIVER._invokeDkimReader():', 
            f'Invoke dns.google...',
            f'checks={checks}',
            f'envelope=', envelope)

        msg = MSG(envelope)
        domain = msg.RequireFrom()
        hostname = f'pollyweb._domainkey.{domain}'
        checks.append(f'Valid domain?: {hostname}')
        
        d = DOMAIN(domain)
        d.GoogleDns()
        ##LOG.Print(f'{self._elapsed()} Validate dns.google...')

        isDnsSec = d.IsDnsSec()
        checks.append(f'IsDnsSec?: {isDnsSec}')
        if not isDnsSec:
            raise ApiException(f"Sender is not DNSSEC protected.")

        isDkimSetUp = d.IsDkimSetUp()
        checks.append(f'DKIM set?: {isDkimSetUp}')
        if not isDkimSetUp:
            raise ApiException(f"Sender DKIM not found for pollyweb.")
        
        hasPublicKey = d.HasPublicKey()
        checks.append(f'Public Key set?: {hasPublicKey}')
        if not hasPublicKey:
            raise ApiException(f"Public key not found on sender DKIM.")
        
        return d.GetPublicKey()
        

    def _validateTo(self, msg: MSG, checks:list[str]):
        to = msg.RequireTo().lower()
        me = NLWEB.CONFIG().RequireDomain().lower()

        if to != me:
            raise ApiException(f'Wrong domain. Expected [{me}], but received [{to}]!')
        checks.append(f'For me?: {True}')
    

    def _validateHashAndSignature(self, msg: MSG, checks:list[str], speed):
        ##LOG.Print(f'API.RECEIVER: {self._elapsed()} Validating signature...')
        
        started = self._timer.StartWatch()
        publicKey = self._invokeDkimReader(msg.Envelope(), checks)
        speed['Get DKIM over DNSSEC'] = self._timer.StopWatch(started)

        started = self._timer.StartWatch()
        msg.VerifySignature(publicKey)
        checks.append(f'Hash and Signature match?: {True}')
        speed['Verify signature'] = self._timer.StopWatch(started)


    def _validate(self, msg:MSG, speed:dict[str,any]) -> dict[str,any]:
        ##LOG.Print(f'SYNCAPI_RECEIVER._Validate(...): {self._elapsed()} Validating...')
        
        error = None
        checks:list[str] = []
        
        try:
            msg.VerifyHeader()
            self._validateTo(msg, checks)

            map = SYNCAPI_RECEIVER_MAP.RequireMap(msg.RequireSubject())
            ##LOG.Print(f'  SYNCAPI_RECEIVER._validate(): {map.Raw()=}')
            if map.IsMissingOrEmpty() or not map.IgnoreValidation():
                ##LOG.Print(f'  SYNCAPI_RECEIVER._validate(): {map.IsMissingOrEmpty()=}')
                ##LOG.Print(f'  SYNCAPI_RECEIVER._validate(): {map.IgnoreValidation()=}')
                self._validateHashAndSignature(msg, checks, speed)

        except AnotherException as e:
            if hasattr(e, 'message'):
                error = f'{e.message}'
            else:
                error = f'{e}'
        
        ret = {
            'Error': error,
            'Checks': checks
        }

        ##LOG.Print(f'{ret=}')
        return ret


    def _execute(self, validation:dict[str,any], envelope:dict[str,any], speed:dict[str,str]) -> dict[str,any]:
        '''👉 Executes the handler.
        
        Params:
        * validation: errors found.
        * envelope: content received.
        * speed: logs the speed of each step.
        '''

        ##LOG.Print(f'{self._elapsed()} Executing...')
        started = self._timer.StartWatch()

        if validation['Error']:
            ret = { 
                'Result': 'Ignored, invalid envelope!'
            }
            ##LOG.Print(f'{ret=}')
            return ret

        msg = MSG(envelope)
        subject = msg.RequireSubject()
        target = SYNCAPI_RECEIVER_MAP.RequireMap(subject)
        
        answer = None 
        functionName = None
        
        if not target.IsMissingOrEmpty():
            functionName = target.Handler()
            LOG.Print('🚀🧠 SYNCAPI.RECEIVER._execute:','found a target:',functionName)
            answer = AWS.LAMBDA(functionName).Invoke(envelope).Obj()

        else:
            LOG.Print('🚀🧠 SYNCAPI.RECEIVER._execute:','no target found.')
            pass

        ret = {
            'Result': 'Executed',
            'Target': functionName,
            'Answer': answer
        }    
        LOG.Print(f'🚀🧠 SYNCAPI.RECEIVER._execute:','ret=', ret)

        speed['Execute method'] = self._timer.StopWatch(started)
        return ret


    def _output(self, envelope, validation, execution, speed):
        ##LOG.Print(f'{self._elapsed()} Building the output...')

        output = {}
        if execution != None:
            if 'Answer' in execution:
                if execution['Answer'] != None:
                    output = execution['Answer']

        if UTILS.IsType(output, dict):
            output['Insights'] = {
                'Speed': speed,
                'Execution': json.loads(json.dumps(execution)),
                'Validation': validation,
                'Received': envelope
            }
        
        LOG.Print(f'🚀🧠 SYNCAPI.RECEIVER._execute:','Returning...')
        if validation['Error']:
            return WEB().HttpResponse(status=400, body=output)
        return WEB().HttpResponse(status=200, body=output)


    def _parse(self, event:dict[str:any]) -> dict[str:any]:
        UTILS.Require(event)

        envelope = {}
        if 'httpMethod' not in event:
            envelope = event
        elif 'body' in event and event['body'] != None:
            envelope = json.loads(event['body'])
        elif event['httpMethod'] == 'GET':
            envelope = {}

        return envelope 


    def Handle(self, event):
        '''
        {
            "Header":{
                "Correlation":"bb37d258-015c-497e-8a67-50bf244a9299",
                "SentAt":"2023-06-24T23:08:24.550719Z",
                "To":"105b4478-eaa5-4b73-b2a5-4da2c3c2dac0.dev.pollyweb.org",
                "Subject":"AnyMethod",
                "Code":"pollyweb.org/msg",
                "Version":"1",
                "From":"105b4478-eaa5-4b73-b2a5-4da2c3c2dac0.dev.pollyweb.org"
            },
            "Body":{
            },
            "Signature": "Lw7sQp6zkOGyJ+OzGn+B1R4rCN/qcYJCtijflQu1Ayqpgxph10yS3KwA4yRhjXgUovskK7LSH+ZqhXm1bcLeMS81l1GKDVaZk3qXpNtrwRmnWrjfD1MekZrO1sRWPNBRH157INAkPWFH/Wb2LLPCAJZYwIv02BF3zKz/Zgm8z7BqOJ3ZrAOC80kTef1zhXNXUMQ/HBrspUTx0NFiMi+dXZMJ69ylxGaAjALMLmcMwFqH2D5cWqX5+eMx0zv2tMh73e8xQqxOr+YLUkO7JjK56KbCUk0HYGUbL5co9eyQMYCGyDtn0G2FqSK9h8BJ1YW3LQmWWTGa/kWDxPjHR3iNyg==", 
            "Hash": "ee6ca2a43ec05d0bd855803407b9350e6c84dd1b981274e51ce0a0a8be16e4a1"
        }
        '''        
        LOG.Print(f'🚀👉 SYNCAPI.RECEIVER.Handle():', event)
        
        UTILS.Require(event)
        envelope = self._parse(event)
        LOG.Print(f'🚀👉 SYNCAPI.RECEIVER.Handle:', 'envelope=', envelope)
        
        if envelope == {}:
            return WEB().HttpResponse(
                status= 200, 
                body= { 'Result': 'Inbox is working :)' })

        speed:dict[str,str] = {}
        started = self._timer.StartWatch()
        msg = MSG(envelope)

        validation = self._validate(msg, speed)
        execution = self._execute(validation, envelope, speed)
        speed['Total handling'] = self._timer.StopWatch(started)

        return self._output(envelope, validation, execution, speed)
