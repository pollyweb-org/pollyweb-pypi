# 🔆 QR

from typing import Union
from pollyweb import STRUCT
from pollyweb import LOG
   

class QR(STRUCT):
    ''' 🔆 QR Code.
    * Docs: https://quip.com/zE0MAiuuPMaE/-NFC-QR 
    * Example: 🤝pollyweb.org/QR,1,any-hairdresser.com,7V8KD3G
    '''


    def __init__(self, data:Union[str,STRUCT]=None):
        LOG.Print(f'🔆 QR.__init__()', data)
        
        obj= data
        
        # Convert string structs into plain strings.
        if isinstance(data, STRUCT) \
        and isinstance(data.Obj(), str):
            data = data.Obj()

        # Detect json.loads() from a string.
        if isinstance(data, str) \
        and '\\ud83e\\udd1d' in data:
            LOG.RaiseException(
                'There was a json.loads() from a string, was it not?')

        # Parse strings.
        if isinstance(data, str):
            obj = self.Parse(data)

        # Do any other stuff in the base class.
        super().__init__(obj)


    def __str__(self):
        if isinstance(self._obj, str):
            return self._obj
        else:
            return self.GetAtt('QR')


    def Parse(self, string:str):
        '''👉 Parses the QR string.

        Example: 🤝pollyweb.org/QR,1,any-printer.com,7V8KD3G 
        '''
        LOG.Print(f'🔆 QR.Parse()', f'{string=}')

        if not string.startswith('🤝'):
            LOG.RaiseValidationException(
                'Invalid QR, missing handshake!')
        
        parts = string.split(',')
        ret = {
            'QR': string,
            'Code': parts[0].replace('🤝', ''),
            'Version': parts[1],
            'Domain': parts[2],
            'Locator': parts[3]
        }

        return ret



    def RequireDomain(self):
        '''👉 Returns the target domain name that owns the Resource.
        * Example: pollyweb.org'''
        return self.RequireStr('Domain')
        

    def RequireLocator(self):
        '''👉 Returns the resource locator in the target domain.'''
        return self.RequireStr('Locator')
    

    def RequireCode(self):
        '''👉 Returns the code that defines the structure of the resource.
        * Example: pollyweb.org/HOST'''
        return self.RequireStr('Code')    
    

    def IsHostCode(self) -> bool:
        '''👉 Indicates if the resource is used to checkin into a host.'''
        return self.RequireCode() == 'pollyweb.org/HOST'
    

    def RequireQR(self):
        return self.RequireStr('QR')
    

    @classmethod
    def ComposeHost(cls, host:str,locator:str):
        return f'🤝pollyweb.org/HOST,1.0,{host},{locator}'
    
    
    @classmethod
    def ComposeEphemeral(cls, host:str, locator:str, pin:str):
        return f'🤝pollyweb.org/HOST,1.0,{host},{locator},{pin}'
    

