from ACTOR import ACTOR
from PW_AWS.AWS_TEST import AWS_TEST
from MANIFEST import MANIFEST

# ✅ DONE
class ACTOR_MOCKS(ACTOR, AWS_TEST):
    

    @classmethod
    def MockActor(cls, 
        domain:str='any-domain.com', 
        graph:str='any-graph.com', 
        listener:str='any-listener.com',
        selfie:str=None,
        transcriber:str=None,
        manifest:MANIFEST=None,
        clean:bool=False):
        
        # --------------------
        # DEPENDENCIES
        # --------------------
            
        # GRAPH
        cls.MOCKS().SSM().MockGraphSetting(domain= domain, graph= graph)
        if clean != True:
            cls.MOCKS().GRAPH().MockGraph(graph)

        # LISTENER
        cls.MOCKS().SSM().MockListenerSetting(domain= domain, listener= listener)
        if clean != True:
            cls.MOCKS().LISTENER().MockListener(listener, subscribers=[graph])

        # --------------------
        # BEHAVIOURS
        # --------------------

        # Endpoint
        cls.MOCKS().WEB().MockDomain(domain= domain)

        # SYNC API
        cls.MOCKS().SYNCAPI().MockSyncApi(domain= domain)

        # MESSENGER
        cls.MOCKS().MESSENGER().MockMessenger(domain= domain)

        # MANIFESTER
        cls.MOCKS().MANIFESTER().MockManifester(
            domain= domain, 
            manifest=manifest)
        
        # TRANSFER
        cls.MOCKS().TRANSFER().MockTransfer(domain= domain)

        # TALKER.SELFIE
        if selfie != None:
            cls.MOCKS().SSM().MockSelfieSetting(
                domain= domain,
                selfie= selfie)
            
        # TALKER.TRANCRIBER
        if transcriber != None:
            cls.MOCKS().SSM().MockTranscriberSetting(
                domain= domain,
                transcriber= transcriber)

        # Set the universal active domain to this one.
        cls.SetDomain(domain= domain)