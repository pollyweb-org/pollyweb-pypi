# 📚 HANDLER

from typing import Union

from .DEPLOYER_TASK import DEPLOYER_TASK
from .STRUCT import STRUCT
from .AWS import AWS
from .LOG import LOG


# ✅ DONE
class HANDLER: 
    ''' 👉 Registers and triggers code events. 

    Tables:
    * Handlers: list of registered handlers.
    '''

    _events:dict[str,list[object]] = {}

    @classmethod
    def _Events(cls, event:str=None, handlers:list=None) -> Union[ 
        None,
        list[object], 
        dict[str,list[object]] 
        ]:

        ##LOG.Print(f'HANDLER._Memory(key={event}, value={handlers}')

        if event == None:
            return HANDLER._events
        
        elif handlers == None:
            if event not in HANDLER._events:
                HANDLER._events[event] = []
            return HANDLER._events[event]
        
        else:
            HANDLER._events[event] = handlers
        

    # ✅ DONE
    @classmethod
    def OnPython(cls, event:str, handler:object):
        ''' 👉 Registers a handler for a python event.

        Source:
        * https://stackoverflow.com/questions/307494/function-pointers-in-python \n
        * https://d-hanshew.medium.com/cleaner-code-using-function-pointers-in-python-75c49f04b6f2 

        Usage:
        * Listener: On('Event@Component', myPythonFunction)
        * Producer: result = Trigger('Event@Component', arg1, ..., argN)
        '''

        # Get the list.
        lst = cls._Events(event)
        if lst == None:
            cls._Events(event, handlers=[])
        
        # Ignore if is already registered.
        for e in HANDLER._events:
            for h in HANDLER._events[e]:
                if e==event and h==handler:
                    return

        # Register.
        cls._Events(event).append(handler)
        

    # ✅ DONE
    @classmethod
    def TriggerPython(cls, event:str, *args):
        ''' 👉 Runs all triggers registered for the event. 
        * Source: https://stackoverflow.com/questions/13783211/how-to-pass-an-argument-to-a-function-pointer-parameter 
        
        Usage:
        * Listener: On('Event@Component', myPythonFunction)
        * Producer: result = Trigger('Event@Component', arg1, ..., argN)
        '''
        LOG.Print(
            f'🌀 HANDLER.TriggerPython()', 
            f'{event=}')

        # Read from memory and execute the python function.
        ret = None # function returm/
        index = 0 # print helper.
        executed = [] # dedup helper.

        if event in cls._Events():
            handlers = cls._Events(event)

            for handler in handlers:
                LOG.Print(f'🌀 HANDLER.TriggerPython:', f'{handler=}')

                # Get the handler's name.
                hs = f'{handler}'
                if '<bound method ' in hs:
                    hs = hs.split('<bound method ')[1]
                    hs = hs.split(' of')[0]

                LOG.Print(f'🌀 HANDLER.TriggerPython: ', 
                          f'loop index= {index}', f'handler= {hs}', f'{executed=}',
                          f'{event=}')
                
                index = index + 1

                # Skip if already executed in the same loop.
                if hs in executed:
                    continue
                executed.append(hs)

                # Execute the handler with args.
                ret = handler(*args)    
        return ret


    @classmethod
    def TriggerLambdas(cls, event:str, payload:any, required:bool=False) -> STRUCT:
        ''' 👉 Read from Dynamo and invoke the lambda function.'''

        from .POLLYWEB import POLLYWEB
        domain = POLLYWEB.CONFIG().RequireDomain()
        LOG.Print(
            f'🌀 HANDLER.TriggerLambdas()', 
            f'domain= {domain}',
            f'event= {event}')

        ret = STRUCT(payload)
        item = AWS.DYNAMO('TRIGGERS').Require(event)
        handlers = item.GetList('Lambdas')

        if required == True and len(handlers) == 0:
            LOG.RaiseException(
                f'Missing handler for event=({event})!', f'{domain=}')

        LOG.Print(f'🌀 HANDLER.TriggerLambdas:',
            'handlers list:', handlers)
        
        iHandler = 0
        for handler in handlers:
            iHandler = iHandler + 1
            LOG.Print(
                f'🌀 HANDLER.TriggerLambdas:',
                f'invoking handler {iHandler}/{len(handlers)}...', 
                f'{domain=}', f'{event=}', f'{handler=}')

            ret = AWS.LAMBDA(handler).Invoke(ret)
    
        # return the value of the last invocation.
        return ret
    

    # ✅ DONE
    @classmethod
    def Trigger(cls, event:str, args:any={}):
        ''' 👉 Runs all triggers registered for the event. \n
        * Source: https://stackoverflow.com/questions/13783211/how-to-pass-an-argument-to-a-function-pointer-parameter 
        
        Usage:
        * Listener: On('Event@Component', myPythonFunction)
        * Producer: result = Trigger('Event@Component', arg1, ..., argN)
        '''
        LOG.Print(f'🌀 HANDLER.Trigger()', f'{event=}')
        ##AWS.DYNAMO('TRIGGERS').DumpIDs()

        cls.TriggerPython(event, args)

        return cls.TriggerLambdas(event, args)
  

    @classmethod
    def HandleRaisesEvent(cls, task:DEPLOYER_TASK):
        ''' 👉 Registers an event to be handled by HANDLER.Trigger. '''
        LOG.Print(f'🌀 HANDLER.HandleRaisesEvent()', f'{task=}')

        stack = task.RequireStackName()
        asset = task.RequireAsset()
        eventName = f'Handle{asset}@{stack}'
        
        AWS.DYNAMO('TRIGGERS').Insert({
            'ID': eventName,
            'Lambdas': []
        })


    @classmethod
    def HandleHandlesEvent(cls, task:DEPLOYER_TASK):
        ''' 👉 Registers an event to be handled by HANDLER.Trigger'''
        LOG.Print(f'🌀 HANDLER.HandleHandlesEvent()', f'{task=}')
                  
        LOG.RaiseException(f'Not implemented yet!')