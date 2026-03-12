from pollyweb import LOG
from PW_PARALLEL.PARALLEL import PARALLEL


class PW_TESTS:
    '''👉️ Tests for the PW framework.'''

    ICON = '🧪'


    @classmethod
    def TestEvents(cls):
        LOG.Print(cls.TestEvents)
        
        # -----------------------------
        # Events.
        # -----------------------------

        from PW_UTILS.HANDLER_TESTS import HANDLER_TESTS
        HANDLER_TESTS.TestAllHandler()


    @classmethod
    def TestMsg(cls):
        LOG.Print(cls.TestMsg)

        # -----------------------------
        # MSG communication.
        # -----------------------------

        from MSG_TESTS import MSG_TESTS
        MSG_TESTS.TestAllMsg()
        
        from SYNCAPI_TESTS import SYNCAPI_TESTS
        SYNCAPI_TESTS.TestAllSyncAPI()
        
        from MESSENGER_TESTS import MESSENGER_TESTS
        MESSENGER_TESTS.TestAllMessenger()


    @classmethod
    def TestPubSub(cls):
        LOG.Print(cls.TestPubSub)

        # -----------------------------
        # Pub/Sub for Listeners/Graphs.
        # -----------------------------

        from SUBSCRIBER_TESTS import SUBSCRIBER_TESTS
        SUBSCRIBER_TESTS.TestAllSubscriber()
        
        from PUBLISHER_TESTS import PUBLISHER_TESTS
        PUBLISHER_TESTS.TestAllPublisher()


    @classmethod
    def TestManifests(cls):
        LOG.Print(cls.TestManifests)

        # -----------------------------
        # Manifests.
        # -----------------------------

        from CODE_TESTS import CODE_TESTS
        CODE_TESTS.TestAllCode()
        
        from MANIFEST_TESTS import MANIFEST_TESTS
        MANIFEST_TESTS.TestAllManifest()
        
        from GRAPH_TESTS import GRAPH_TESTS
        GRAPH_TESTS.TestAllGraph()
        
        from LISTENER_TESTS import LISTENER_TESTS
        LISTENER_TESTS.TestAllListener()
        
        from MANIFESTER_TESTS import MANIFESTER_TESTS
        MANIFESTER_TESTS.TestAllManifester()


    @classmethod
    def TestTalker(cls):
        LOG.Print(cls.TestTalker)

        # -----------------------------
        # Talker.
        # -----------------------------

        from PROMPT_TESTS import PROMPT_TESTS
        PROMPT_TESTS.TestAllPrompt()
        
        from TALKER_GROUP_TESTS import TALKER_GROUP_TESTS
        TALKER_GROUP_TESTS.TestAllTalkGroup()

        from TALK_TESTS import TALK_TESTS
        TALK_TESTS.TestAllTalkerTalk()
        
        from TALKER_TESTS import TALKER_TESTS
        TALKER_TESTS.TestAllTalker()


    @classmethod
    def TestActors(cls):
        LOG.Print(cls.TestActors)

        # -----------------------------
        # Actors.
        # -----------------------------

        from HOST_TESTS import HOST_TESTS
        HOST_TESTS.TestAllHost()
        
        from VAULT_TESTS import VAULT_TESTS 
        VAULT_TESTS.TestAllVault()
        
        from CONSUMER_TESTS import CONSUMER_TESTS
        CONSUMER_TESTS.TestAllConsumer()
        
        from ISSUER_TESTS import ISSUER_TESTS
        ISSUER_TESTS.TestAllIssuer()
        

    @classmethod
    def TestPayments(cls):
        LOG.Print(cls.TestPayments)

        # -----------------------------
        # Payments.
        # -----------------------------

        from COLLECTOR_TESTS import COLLECTOR_TESTS
        COLLECTOR_TESTS.TestAllCollector()
        
        from PAYER_TESTS import PAYER_TESTS
        PAYER_TESTS.TestAllPayer()
        
        from SELLER_TESTS import SELLER_TESTS
        SELLER_TESTS.TestAllSeller()


    @classmethod
    def TestAllQR(cls):
        '''👉️ Run all the tests in parallel.'''
        LOG.Print(cls.TestAllQR)

        from QR_TESTS import QR_TESTS
        QR_TESTS.TestAllQR()


    @classmethod
    def TestBroker(cls):
        LOG.Print(cls.TestBroker)

        from BROKER_TESTS import BROKER_TESTS
        BROKER_TESTS.TestAllBroker()
                    
    
    @classmethod
    def TestNotifier(cls):
        LOG.Print(cls.TestNotifier)

        from NOTIFIER_TESTS import NOTIFIER_TESTS
        NOTIFIER_TESTS.TestAllNotifier()


    @classmethod
    def TestWallet(cls):
        LOG.Print(cls.TestWallet)

        from WALLET_TESTS import WALLET_TESTS
        WALLET_TESTS.TestAllWallet()


    @classmethod
    def TestAllDtft(cls, parallel: bool):
        '''👉️ Run all the tests in parallel.'''
        LOG.Print(cls.TestAllDtft)

        with PARALLEL.PROCESS_POOL(
            seconds= 60 * 10) as pool2:

            pool2.StartProcessList([
                cls.TestEvents,
                cls.TestMsg,
                cls.TestPubSub,
                cls.TestManifests,
                cls.TestTalker,
                cls.TestActors,
                cls.TestPayments,
                cls.TestNotifier,
                cls.TestBroker,
                cls.TestWallet
                
            ], parallel=parallel)

        LOG.PARALLEL().SetClassDone()