from HOST import HOST
from PW_AWS.AWS_TEST import AWS_TEST
from pollyweb import LOG
from pollyweb import UTILS



class HOST_MOCKS(HOST, AWS_TEST):

    @classmethod
    def MockHostSetup(cls, host, clean:bool):
        LOG.Print(' HOST.MOCKS.MockHostSetup()', f'{host=}')

        if cls.IsDomainMocked(domain=host, component=cls):
            return 
        
        cls.MOCKS().SYNCAPI().MockHandlers(
            domain= host,
            ignoreValidation=False, 
            pairs= {
                'CheckIn@Host': cls.HandleCheckIn
            })
        
        # SYNCAPI handlers.
        cls.MOCKS().SYNCAPI().MockHandlers(
            domain= host,
            ignoreValidation=True, 
            pairs= {
                'Prompted@Host': cls.HandlePrompted,
                'Download@Host': cls.HandleDownload,
                'Upload@Host': cls.HandleUpload
            })
        
        # MESSENGER handlers.
        cls.MOCKS().MESSENGER().MockHandlers(
            domain= host,
            pairs= {
                'Abandoned@Host': cls.HandleAbandoned,
                'CheckOut@Host': cls.HandleCheckOut,
                'Talker@Host': cls.HandleTalker,
                'Reply@Host': cls.HandleReply
            })
        
        # HANDLER handlers.
        cls.MOCKS().HANDLER().RegisterLambdaHandlers(
            events=[
                'OnCheckOut@Host',
                'OnEvaluate@Talker',
                'OnFound@Host'
            ])
        
        # TALKER HANDLERS
        cls.MOCKS().TALKER().MockTalker(domain=host, clean=clean)
        

    @classmethod
    def MockHostLocator(cls, host:str, locator:str, talker:str, script:str):

        UTILS.AssertIsType(script, str)
        UTILS.AssertIsType(talker, str)

        # LOCATORS table.
        cls.MOCKS().DYNAMO().MockTable(
            domain= host,
            table= 'LOCATORS',
            items=[{
                "ID": f"pollyweb.org/HOST,{locator}",
                "Talker": talker
            }])

        # TALKERS
        cls.MOCKS().DYNAMO().MockTable(
            domain= host,
            table= 'TALKERS',
            items=[{
                'ID': talker,
                'Script': script
            }])


    @classmethod
    def MockHostConfigs(cls, host:str, clean:bool, graph:str=None):

        # GRAPH
        cls.MOCKS().SSM().MockGraphSetting(
            domain= host,
            graph= graph)

        script = '\n'.join([
            '# Order workflow.',
            '💬|Order:',
            '- SHARE|pollyweb.org/PROFILE/NAME/FRIENDLY',
            '- RUN|Items',
            '- CHARGE|{amount}',
            '- INFO|Wait...',
            '',
            'Items:',
            '- INT|Product code?',
            '- CONFIRM|{confirm}',
            '- REPEAT|Anything else?'
        ])

        if not clean:
            cls.MockHostLocator(
                host= host, 
                locator= '<locator>',
                talker= "<talker>",
                script= script
            )            
       


    @classmethod
    def MockHostSession(cls, 
                         host:str, 
                         clean:bool,
                         broker:str= 'any-broker.org',
                         sessionID:str = '<session-uuid>'):

        # TALKS table.
        if not clean:
            cls.MOCKS().DYNAMO().MockTable(
                domain= host,
                table= 'TALKS',
                items=[{
                    "ID": "<talk>",
                    "Session": {
                        "Host": host,
                        "Broker": broker,
                        "SessionID": sessionID,
                        "Locator": "any-locator"
                    },
                    "Groups": [
                        {
                            "ID": "0",
                            "Title": "Order",
                            "Type": "TOP"
                        }
                    ]
                }])
        
        # SESSIONS table.
        if not clean:
            cls.AddSession(
                host= host,
                broker = broker,
                sessionID= sessionID)


    @classmethod
    def AddSession(cls, host:str, broker:str, sessionID:str):
        UTILS.AssertIsUUID(sessionID)

        # SESSIONS table.
        cls.MOCKS().DYNAMO().MockTable(
            domain= host,
            table= 'SESSIONS',
            items=[{
                "ID": f"{broker}/{sessionID}",
                "Locator": "<locator>",
                "Broker": broker,
                "SessionID": sessionID,
                "Talk": "<talk>",
                "Queries": ["any-authority.org/<code>"],
                "Tokens": [{
                    'Code': 'airlines.any-igo.org/SSR/WCH', 
                    'Version': '1.0.0', 
                    'Issuer': 'example.com', 
                    'ID': '7bcf138b-db79-4a42-9d36-2655f8ff1f7c', 
                    'QR': '...'
                }]
            }])
        
        # FILES table.
        cls.MOCKS().DYNAMO().MockTable(
            domain= host,
            table= 'FILES', 
            items= [{ 
                'ID': 'bc3d5f49-5d30-467a-9e0e-0cb5fd80f3cc',
                'Broker': broker,
                'SessionID': sessionID,
                'Name': 'any-file.pdf',
                'Serialized': '<serialized>'
            }])


    @classmethod
    def MockHost(cls, host:str='any-host.org', clean:bool= False):
        cls.SetDomain(host)
        
        if cls.MOCKS().WEB().IsDomainMocked(domain= host):
            return
        
        cls.MockHostSetup(host= host, clean=clean)
        cls.MockHostConfigs(host= host, clean=clean)
        if clean != True:
            cls.MockHostSession(host= host, clean=clean)

        cls.SetDomain(host)
        
        