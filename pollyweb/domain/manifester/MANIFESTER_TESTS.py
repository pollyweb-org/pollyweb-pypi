from PW_AWS.AWS import AWS
from MANIFEST import MANIFEST
from MANIFESTER import MANIFESTER
from PW_AWS.AWS_TEST import AWS_TEST
from pollyweb import LOG
from pollyweb import TESTS
from pollyweb import UTILS


class MANIFESTER_TESTS(MANIFESTER, AWS_TEST):
        

    @classmethod
    def TestAlerter(cls):
        LOG.Print('MANIFESTER_TESTS.TestAlerter() ==============================')
        
        cls.ResetAWS()
        cls.MOCKS().ACTOR().MockActor()
        
        ret = cls.HandleAlerter({
            "Type": "OnDeploymentComplete"
        })
        cls.AssertTrue(ret)

        ret = cls.HandleAlerter({
            "InvocationId": "9rqvead",
            "Parameters": {
                "queueArn": "arn:aws:sqs:eu-west-1:688145780298:Manifester-AlerterQueue"
            },
            "Type": "OnDeploymentStart",
            "Application": {
                "Id": "c1nsa31"
            },
            "Environment": {
                "Id": "79gj97t"
            },
            "ConfigurationProfile": {
                "Id": "5qbzd9i",
                "Name": "Manifester-Manifest-Profile"
            },
            "DeploymentNumber": 1,
            "ConfigurationVersion": "1"
        })
        cls.AssertFalse(ret)

        # Comming from SQS: OnDeploymentStart
        ret = cls.HandleAlerter({
            "Records": [
                {
                    "messageId": "8df61367-a722-4063-bf0e-c0484f62da13",
                    "receiptHandle": "AQEB2l1P/GkVqjP38QDlVgX0+Qvo/nikgPrKiBT/orRdQgVVmJZFesjNkIlylGkJ/pmrIuJ+8Ss+Hv0m0t1G3FbeVBWLYSPBptNcWmyEXUuhVxTAmc1MFnWUon7VywjytGKzkb+7KtlOSfaBn1J78S+SM9JH/FIXRG6yUfZW2PA73hZcNe5B8dViFKl8DyBIk0I4LCDnBiLVGIllV+wKZ8mqa/FV526VbbmLz+gIyhDYnCo/kiycQCNzejSgNLUkGPEJj4djEwPPVo6WWNnOv72MnFFk2htxKo6/zzi3y3hoDvUXfhiWaoOtMpIU/6MFOBOB9TqjzcIpqtJ7P2DfAoQNzczjmELKmtnP2QpVzq/Dj0SFpZokK218eFXSxCF59sqMl18BgpLe8uFXi/whY1QLoA==",
                    "body": "{\"InvocationId\":\"8m6gn0j\",\"Parameters\":{\"queueArn\":\"arn:aws:sqs:eu-west-1:688145780298:Manifester-AlerterQueue\"},\"Type\":\"OnDeploymentStart\",\"Application\":{\"Id\":\"c1nsa31\"},\"Environment\":{\"Id\":\"79gj97t\"},\"ConfigurationProfile\":{\"Id\":\"5qbzd9i\",\"Name\":\"Manifester-Manifest-Profile\"},\"DeploymentNumber\":3,\"Description\":\"Deploying my configuration\",\"ConfigurationVersion\":\"2\"}",
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1712015946806",
                        "SenderId": "AROATAHGZVIRHAJ4NGMLL:AppConfigExtensionsInvocation",
                        "ApproximateFirstReceiveTimestamp": "1712015946813"
                    },
                    "messageAttributes": {
                        "MessageType": {
                            "stringValue": "OnDeploymentStart",
                            "stringListValues": [],
                            "binaryListValues": [],
                            "dataType": "String"
                        }
                    },
                    "md5OfMessageAttributes": "89e8e2a4a2b4b6b78d0227390a660d72",
                    "md5OfBody": "e4cc6ba60991565f4683631695c54197",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:eu-west-1:688145780298:Manifester-AlerterQueue",
                    "awsRegion": "eu-west-1"
                }
            ]
        })
        cls.AssertFalse(ret)

        # Comming from SQS: OnDeploymentComplete
        ret = cls.HandleAlerter({
            "Records": [
                {
                    "messageId": "ea1015b6-8b50-4432-87b9-3bb8391e1aef",
                    "receiptHandle": "AQEBNs3805N/laRlV1LPqwYdUTqpm0uXWZrAzvMZtLqWiE7AUESAlRJPCOfssIqLJr3drAcOOL3iapWGSLalGtY5WTJPHxHFGTZafUGJ6NN0bievSGxATo8TchCI24wUzEV5bbfLgM4iY5/iZt+juQnF3xTDpXqaEauaIVTmu8cXjJyzvyiSuixo5FKTOR4yy2OuO0is21capgRLx8Sw5TYv9WCHXOTjeF/Lw7poB28I4LVmcrvlcw5w06XnPKKtbJEuXdOoYvpJehTVBHIqanURX3BQbhuvvr8HNEWXa+tw3v5X0NhZUKbezpEBD4GgZA+Xk9eqC4A4uFdlSUJKuaEVwYVu1qXeIOlde87OuA5cfVuINfUzpxqlEVusi7SMh4xs2wu9MFYbZl0HAvyWErrBGA==",
                    "body": "{\"InvocationId\":\"t1vo5zh\",\"Parameters\":{\"queueArn\":\"arn:aws:sqs:eu-west-1:688145780298:Manifester-AlerterQueue\"},\"Type\":\"OnDeploymentComplete\",\"Application\":{\"Id\":\"c1nsa31\"},\"Environment\":{\"Id\":\"79gj97t\"},\"ConfigurationProfile\":{\"Id\":\"5qbzd9i\",\"Name\":\"Manifester-Manifest-Profile\"},\"DeploymentNumber\":3,\"Description\":\"Deploying my configuration\",\"ConfigurationVersion\":\"2\"}",
                    "attributes": {
                        "ApproximateReceiveCount": "1",
                        "SentTimestamp": "1712015946841",
                        "SenderId": "AROATAHGZVIRHAJ4NGMLL:AppConfigExtensionsInvocation",
                        "ApproximateFirstReceiveTimestamp": "1712015946844"
                    },
                    "messageAttributes": {
                        "MessageType": {
                            "stringValue": "OnDeploymentComplete",
                            "stringListValues": [],
                            "binaryListValues": [],
                            "dataType": "String"
                        }
                    },
                    "md5OfMessageAttributes": "11e41f3c9ccba0c409f764d7fa5d2a8d",
                    "md5OfBody": "b2e63687ac8d7c803224b9ecf7509999",
                    "eventSource": "aws:sqs",
                    "eventSourceARN": "arn:aws:sqs:eu-west-1:688145780298:Manifester-AlerterQueue",
                    "awsRegion": "eu-west-1"
                }
            ]
        })
        cls.AssertTrue(ret)


    @classmethod
    def TestYamlViewer(cls):
        LOG.Print('MANIFESTER_TESTS.TestYamlViewer() ==============================')

        cls.ResetAWS()
        cls.MOCKS().ACTOR().MockActor()

        resp = cls.HandleYamlViewer()

        cls.AssertEqual(
            resp['body'], 
            cls.MOCKS().MANIFESTER().Manifest.ToYaml())
        

    @classmethod
    def TestJsonViewer(cls):
        LOG.Print('MANIFESTER_TESTS.TestJsonViewer() ==============================')

        cls.ResetAWS()
        cls.MOCKS().ACTOR().MockActor()

        resp = cls.HandleJsonViewer()

        cls.AssertEqual(
            resp['body'], 
            cls.MOCKS().MANIFESTER().Manifest.ToJson())
        

    @classmethod
    def TestDefaultViewer(cls):
        LOG.Print('MANIFESTER_TESTS.TestDefaultViewer() ==============================')

        cls.ResetAWS()
        cls.MOCKS().ACTOR().MockActor()

        resp = cls.HandleDefaultViewer()

        cls.AssertEqual(
            resp['body'], 
            cls.MOCKS().MANIFESTER().Manifest.Obj())
        

    @classmethod
    def TestEndToEnd(cls):
        LOG.Print('MANIFESTER_TESTS.TestEndToEnd() ==============================')

        authority = 'any-authority.org'
        listener = 'any-listener.com'
        graph = 'any-graph.com'
        
        # SETUP
        cls.ResetAWS()

        cls.MOCKS().ACTOR().MockActor(
            domain= authority,
            listener= listener,
            graph= graph)

        cls.MOCKS().GRAPH().MockGraph(graph)
        cls.MOCKS(graph).DYNAMO('DOMAINS').MatchCount(0, 'Initial state')
        cls.MOCKS(graph).DYNAMO('DEDUPS').MatchCount(0)
        cls.MOCKS(graph).DYNAMO('CODES').MatchCount(0)

        cls.MOCKS().LISTENER().MockListener(listener, subscribers=[graph])
        cls.MOCKS(listener).DYNAMO('UPDATES').MatchCount(0)
        cls.MOCKS(listener).DYNAMO('SUBSCRIBERS').MatchCount(1, 'Graph addded as subscriber?')

        # EXECUTE
        cls.SetDomain(authority)
        cls.NLWEB().BEHAVIORS().MANIFESTER().InvokeAlerter()

        # VERIFY
        cls.MOCKS(listener).DYNAMO('UPDATES').MatchCount(1, 'Listener received the update?')
        cls.MOCKS(graph).DYNAMO('DEDUPS').MatchCount(1, 'Graph received the update?')
        cls.MOCKS(graph).DYNAMO('DOMAINS').MatchCount(1, 'Graph downloaded the manifest?')
        cls.MOCKS(graph).DYNAMO('CODES').MatchCount(7, 'Codes were parsed?')


    @classmethod
    def TestMultipleListeners(cls):
        LOG.Print('MANIFESTER_TESTS.TestMultipleListeners() ==============================')

        authority = 'any-authority.org'
        listener1 = 'l1.com'
        listener2 = 'l2.com'
        graph1 = 'g1.com'
        graph2 = 'g2.com'
        
        # SETUP
        cls.ResetAWS()

        cls.MOCKS().ACTOR().MockActor(
            domain= authority,
            listener= listener1,
            graph= graph1)

        # GRAPH 1
        cls.MOCKS().GRAPH().MockGraph(graph1)
        cls.MOCKS(graph1).DYNAMO('DOMAINS').MatchCount(0, 'Initial state 1')
        
        # GRAPH 2
        cls.MOCKS().GRAPH().MockGraph(graph2)
        cls.MOCKS(graph2).DYNAMO('DOMAINS').MatchCount(0, 'Initial state 2')

        # LISTENER 1
        cls.MOCKS().LISTENER().MockListener(listener1, subscribers=[listener2, graph1, graph2])
        cls.MOCKS(listener1).DYNAMO('SUBSCRIBERS').MatchCount(3, 'G1+G2+L2 addded as subscribers of L1?')

        # LISTENER 2
        cls.MOCKS().LISTENER().MockListener(listener2, subscribers=[listener1, graph1, graph2])
        cls.MOCKS(listener2).DYNAMO('SUBSCRIBERS').MatchCount(3, 'G1+G2+L1 addded as subscriber to L2?')
        
        # EXECUTE
        cls.SetDomain(authority)
        cls.NLWEB().BEHAVIORS().MANIFESTER().InvokeAlerter()

        # VERIFY
        cls.MOCKS(listener1).DYNAMO('UPDATES').MatchCount(1, 'L1 received the update?')
        cls.MOCKS(listener2).DYNAMO('UPDATES').MatchCount(1, 'L2 also received the update?')
        cls.MOCKS(graph1).DYNAMO('DEDUPS').MatchCount(1, 'G1 received the update?')
        cls.MOCKS(graph2).DYNAMO('DEDUPS').MatchCount(1, 'G2 also received the update?')
        cls.MOCKS(graph2).DYNAMO('DOMAINS').MatchCount(1, 'G2 downloaded the manifest?')


    @classmethod
    def TestMockManifester(cls):
        LOG.Print('MANIFESTER_TESTS.TestMockManifester() ==============================')
        
        # Clean up
        cls.ResetAWS()
        
        # Set a general manifest.
        m = cls.MOCKS().MANIFEST().MockManifest()
        cls.MOCKS().MANIFESTER().MockManifester(manifest= m)

        # Compare if equal
        resp = cls.WEB().HttpGet('https://pollyweb.any-domain.com/manifest')
        cls.AssertEqual(m.ToYaml(), resp, 'General OK?')

        # Clean up again
        cls.ResetAWS()
        
        # Set a customised manifest.
        
        custom = MANIFEST({'Identity':{'Domain':'d.com'}})
        cls.MOCKS().MANIFESTER().MockManifester(manifest= custom)

        resp = cls.WEB().HttpGet('https://pollyweb.any-domain.com/manifest')
        cls.AssertEqual(resp, custom.ToYaml(), 'Changed to customized?')


    @classmethod
    def TestValidator(cls):
        LOG.Print('@')

        # Template envelope.
        envelope = {
            "content": "",
            "uri": "hosted",
            "applicationId": "cn7jl97",
            "configurationProfileId": "klxooqp",
            "configurationVersion": "3"
        }

        # Bad format, just random stuff.
        envelope['content'] = "PGVtcHR5PgogYXNkIAogIGFzZA=="
        with cls.AssertValidation():
            MANIFESTER.HandleValidator(envelope)

        # Invalid Valid format, missing domain.
        with cls.AssertValidation():
            envelope['content'] = UTILS.EncodeTextBase64('''
Identity:
  Domain2: any-domain.long
  Name: Any text
        ''')
            MANIFESTER.HandleValidator(envelope)

        # Valid format.
        envelope['content'] = UTILS.EncodeTextBase64('''
Identity:
  Domain: any-domain.long
  Name: Any text
        ''')
        MANIFESTER.HandleValidator(envelope)


    @classmethod
    def TestAllManifester(cls):
        LOG.Print('MANIFESTER_TESTS.TestAllManifester() ==============================')

        cls.TestAlerter()
        cls.TestYamlViewer()
        cls.TestJsonViewer()
        cls.TestDefaultViewer()
        cls.TestEndToEnd()
        cls.TestMultipleListeners()
        cls.TestMockManifester()
        cls.TestValidator()