from PW import PW
from SELLER import SELLER
from PW_AWS.AWS_TEST import AWS_TEST


class SELLER_MOCKS(SELLER, AWS_TEST):
        

    @classmethod
    def MockSetupSeller(cls, seller:str):

        cls.MOCKS().MESSENGER().MockHandlers(
            domain= seller, 
            ignoreValidation= False, 
            pairs= {
                'Paid@Seller': cls.HandlePaid
            })
        
        cls.MOCKS().SYNCAPI().MockHandlers(
            domain= seller,
            ignoreValidation= False,
            pairs= {
                'IsCharged@Seller': cls.HandleIsCharged
            })
        

    @classmethod
    def MockConfigSeller(cls, seller, collectors:list[str]):

        cls.MOCKS().HANDLER().RegisterLambdaHandlers(
            events= [
                'OnPaid@Seller'
            ])
        
        for collector in collectors:
            PW.ROLES().SELLER().COLLECTORS().Insert(collector)


    @classmethod
    def MockCharges(cls, seller):

        cls.MOCKS().DYNAMO().MockTable(
            domain= seller,
            table= 'CHARGES',
            items= [{
                'ID': '<charge-uuid>',
                'Amount': 10.54,
                'Currency': 'USD',
                'Operation': 'DEBIT',
                'Paid': False,
                'Collectors': ['any-collector.org']
            }]
        )


    @classmethod
    def MockSeller(cls, 
                   seller:str= 'any-seller.org',
                   collectors=['any-collector.org'],
                   graph:str='any-graph.com',
                   broker:str='any-broker.org',
                   clean:bool= False
                   ) -> str:

        cls.SetDomain(seller)

        cls.MOCKS().CONSUMER().MockConsumer(
            consumer=seller, 
            broker= broker,
            graph= graph,
            clean=clean)

        cls.MockSetupSeller(seller= seller)
        cls.MockConfigSeller(seller= seller, collectors= collectors)

        if clean != True:
            cls.MockCharges(seller= seller)

        cls.SetDomain(seller)
        return seller