from .AWS_TEST import AWS_TEST
from .LOG import LOG


class HANDLER_MOCKS(AWS_TEST):
    

    @classmethod
    def MockLambdaHandlers(
        cls, domain:str, map:dict):

        for key in map:
            cls.MockLambdaHandler(
                domain= domain,
                event= key,
                handler= map[key])

    INDEX = 0

    @classmethod
    def MockLambdaHandler(
        cls, domain:str, event:str, 
        alias:str=None, 
        handler:object=AWS_TEST._echo, 
        single:bool = False, 
        optional:bool= False):
        '''👉 Adds a Lambda handler to an event.'''

        LOG.Print(
            '🌀🐦 HANDLER.MOCKS.MockLambdaHandler()',
            f'{domain=}', f'{event=}', f'{alias=}', f'{single=}', f'{handler=}')

        # Get the trigger from the database.
        item = cls.MOCKS(domain).DYNAMO('TRIGGERS').GetItem(event)
        
        # Check if it hasn't yet been defined.
        if item.IsMissingOrEmpty():
            if optional == True:
                LOG.Print(
                    '🌀🐦 HANDLER.MOCKS.MockLambdaHandler:', 
                    'Not yet defined, we will wait for the next iteration.')
                return
            else:
                LOG.RaiseException(
                    '🌀🐦 HANDLER.MOCKS.MockLambdaHandler:', 
                    'Required trigger hander missing for event!', event)

        # Check if already has a handler.
        if False and item.Struct('Lambdas').Any(equals=alias):
            LOG.Print(
                '🌀🐦 HANDLER.MOCKS.MockLambdaHandler:', 
                'Already has a handler.')
            return

        # Set up the lambda.
        if alias == None:
            alias = f'Fy-{cls.INDEX}-{event}'
            cls.INDEX = cls.INDEX+1
            
        cls.MOCKS(domain).LAMBDA().MockInvoke(
            alias= alias,
            handler= handler,
            domain= domain)
        
        # Register the event handler.
        item.AppendToAtt('Lambdas', alias)
        item.UpdateItem()


    @classmethod
    def RegisterLambdaHandlers(cls, events:list[str]):
        
        for event in events:
            cls.AWS().DYNAMO('TRIGGERS').Insert({
                'ID':event, 
                'Lambdas': []
            })