from SELLER import SELLER
from PW_AWS.AWS_TEST import AWS_TEST
from SESSION import SESSION
from pollyweb import LOG
   

class SELLER_TESTS(SELLER, AWS_TEST):
        

    @classmethod
    def TestCharge(cls):

        seller = 'any-seller.org'
        broker = 'any-broker.org'
        collector = 'any-collector.org'

        cls.ResetAWS()

        # -------------------------
        # SET UP
        # -------------------------

        # Set up comms.
        cls.MOCKS().BROKER().MockBroker(broker)
        cls.MOCKS().MESSENGER().MockMessenger(seller)

        cls.MOCKS().DYNAMO().MockTable(
            domain= seller,
            table= 'COLLECTORS',
            items= [{
                'ID': collector,
                'IsActive': True
            }])

        # -------------------------
        # EXEC
        # -------------------------

        cls.SetDomain(seller)

        cls.Charge(
            source= 'SELLER_TEST',
            session= SESSION.New(
                host= seller,
                locator= 'any-locator',
                broker= broker,
                sessionID= '<session-uuid@seller>'
            ),
            message= '<reason-for-charge>',
            amount= 10.34,
            currency= 'USD')
        

    @classmethod
    def TestPaid(cls):

        broker = 'any-broker.org'
        seller = 'any-seller.org'
        collector = 'any-collector.org' 

        # -------------------
        # SET UP
        # -------------------

        cls.ResetAWS()
        cls.MOCKS().SELLER().MockSeller()

        # -------------------
        # EXEC
        # -------------------

        charge = {
            "ChargeID": "<charge-uuid>",
            "Operation": "DEBIT",
            "Amount": 10.54,
            "Currency": "USD",
            "Collectors": [collector]
        }

        session = {
            "Host": seller,
            "Broker": broker,
            "Locator": "<any-locator>",
            "SessionID": "<session-uuid>"
        }
        
        cls.SetDomain(seller)

        cls.HandlePaid({
            "Header": {
                "From": collector,
                "To": seller,
            },
            "Body": {
                "Session": session,
                "Charge": charge,
                "Transaction": {}
            }
        })

        # -------------------
        # VERIFY
        # -------------------
    

    @classmethod
    def TestAllSeller(cls):
        LOG.Print('SELLER_TESTS.TestAllSeller() ==============================')

        cls.TestCharge()
        cls.TestPaid()
        