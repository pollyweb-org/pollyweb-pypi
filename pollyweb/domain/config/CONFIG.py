# 🤝 PW

from PW_AWS.AWS import AWS
from pollyweb import UTILS
from pollyweb import LOG


class CONFIG:
    ''' 👉 PW Settings in SSM. '''


    def __init__(self) -> None:
        self._ssm = AWS.SSM()


    def _setting(self, 
        name:str, 
        value:str=None, 
        optional:bool=False
    ) -> str:
        '''👉️ Gets or sets a parameter on the parameter store.'''
        UTILS.RequireArgs([name])

        if '/' in name.upper():
            LOG.RaiseException('🛠️ CONFIG._setting() -> name cannot contain /')

        setting = '/PW/Config/'+name

        if value != None:
            self._ssm.Set(
                name=setting, 
                value=value)

        item = self._ssm.Get(setting, optional=optional)

        if not optional and UTILS.IsNoneOrEmpty(item):
            LOG.RaiseException('Missing setting on SSM: ' + setting)  
        
        return item
        

    def RequireGraph(self) -> str:
        ''' 👉 Domain name of the preferred Graph to send updates to. '''
        return self._setting('Graph')
    
    def SetGraph(self, graph:str) -> None:
        '''👉 Sets the Graph to send updates to.'''
        self._setting(name='Graph', value=graph)


    def RequireListener(self) -> str:
        ''' 👉 Domain name of the preferred Listener to send manifest updates to. 
        Only relevant to Manifesters in a Domain. '''
        return self._setting('Listener')

    def SetListener(self, listener:str) -> None:
        '''👉 Sets the Listener to send manifest updates to.'''
        self._setting(name='Listener', value=listener)


    def RequireBroker(self) -> str:
        ''' 👉 Domain name of the preferred Broker to register Wallets.
        Only relevant to Notifiers. '''
        return self._setting('Broker')
    

    def RequireSelfie(self) -> str:
        ''' 👉 Domain name of the preferred Selfie to verify user faces.
        Only relevant to Talkers. '''
        return self._setting(
            name= 'Selfie')
    

    def RequireTranscriber(self) -> str:
        ''' 👉 Domain name of the preferred Transcribe to record user messages.
        Only relevant to Talkers. '''
        return self._setting(
            name= 'Transcriber')
    

    def RequireDomain(self, optional:bool=False) -> str:
        ''' 👉 Domain name.'''
        ret = self._setting(
            name= 'DomainName', 
            optional= optional)
        
        LOG.Print(f'🛠️ CONFIG.RequireDomain() -> {ret}')
        return ret


    def RequirePublicKey(self) -> str:
        return AWS.SECRETS().Get('/PW/PublicKey').GetValue()