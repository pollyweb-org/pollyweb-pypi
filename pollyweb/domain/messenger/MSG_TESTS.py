# 📚 MSG

from pollyweb import TESTS
from pollyweb import STRUCT
from MSG import MSG
from WEB_MOCK import WEB_MOCK
from pollyweb import LOG


class MSG_TESTS(MSG):
    ''' 👉 Structure of a message: { Header, Body, Hash, Signature }.
    * https://quip.com/NiUhAQKbj7zi

    Usage:
    * MSG({}) -> ${}
    * MSG(${}) -> ${}

    Example:
    { 
        "Header": {
            "Code": "pollyweb.org/msg",
            "Version": "1",
            "From": "any-sender.com",
            "To": "any-receiver.com",
            "Subject": "AnyMethod",
            "Correlation": "125a5c75-cb72-43d2-9695-37026dfcaa48", 
            "SentAt": "2018-12-10T13:45:00.000Z"
        },
        "Body": {}
        "Hash": "..."
        "Signature": <{ Header, Body } signed>
    }
    '''
        

    @classmethod
    def TestEnvelope(cls):

        TESTS.AssertEqual(
            given= MSG({'Header':{}, 'Body':{}}).Envelope(), 
            expect= {'Header':{}, 'Body':{}}
        )
        
        TESTS.AssertEqual(
            given= MSG({'Header':{}}).Envelope(), 
            expect= {'Header':{}, 'Body':{}}
        )
        

    @classmethod
    def TestHeader(cls):

        TESTS.AssertEqual( MSG({}).RequireHeader(), {} )

        TESTS.AssertEqual( 
            given= MSG({'Header':{'A':1}, 'Body':{}}).RequireHeader(), 
            expect= STRUCT({'A':1}) 
        )
        
        TESTS.AssertEqual( 
            given= MSG({'Header':{'A':1}}).RequireHeader(), 
            expect= STRUCT({'A':1})
        )
        
        m= MSG({})
        m.RequireHeader({'A':1})
        TESTS.AssertEqual(
            given= m.Envelope(),
            expect= STRUCT({'Header':{'A':1}, 'Body':{}})
        )

        m= MSG({})
        m.RequireHeader(STRUCT({'A':1}))
        TESTS.AssertEqual(
            given= m.Envelope(),
            expect= STRUCT({'Header':{'A':1}, 'Body':{}})
        )
                

    @classmethod
    def TestSubject(cls):
        
        MSG({}).RequireSubject('x')

        TESTS.AssertEqual(
            given= MSG({'Header':{'Subject':'x'}}).RequireSubject(),
            expect= 'x')
        
        m= MSG({'Header':{}})
        m.RequireSubject('x')
        TESTS.AssertEqual(
            m.Envelope(), 
            {'Header':{'Subject':'x'},'Body':{}})
        

    @classmethod
    def TestFrom(cls):

        MSG({}).RequireFrom('x')

        TESTS.AssertEqual(
            given= MSG({'Header':{'From':'x'}}).RequireFrom(),
            expect= 'x')
        
        m= MSG({'Header':{}})
        m.RequireFrom('x')
        TESTS.AssertEqual(m.Envelope(), {'Header':{'From':'x'},'Body':{}})
        
    
    @classmethod
    def TestTo(cls):
        
        MSG({}).RequireTo('x')
        
        TESTS.AssertEqual(
            given= MSG({'Header':{'To':'x'}}).RequireTo(),
            expect= 'x' 
        )
        
        m= MSG({'Header':{}})
        m.RequireTo('x')
        TESTS.AssertEqual(m.Envelope(), {'Header':{'To':'x'},'Body':{}})
        
    
    @classmethod
    def TestSentAt(cls):

        with TESTS.AssertValidation():
            MSG({}).GetTimestamp('x') # Invalid date.

        MSG({}).GetTimestamp('2023-04-01T05:00:30.001000Z')
        
        TESTS.AssertEqual(
            given= MSG({
                'Header':{
                    'SentAt':'2023-04-01T05:00:30.001000Z'
                }
            }).GetTimestamp(),
            expect= '2023-04-01T05:00:30.001000Z'
        )
        
        m= MSG({'Header':{}})
        m.GetTimestamp('2023-04-01T05:00:30.001000Z')
        TESTS.AssertEqual(
            m.Envelope(), 
            {'Header':{'SentAt':'2023-04-01T05:00:30.001000Z'},'Body':{}})
        
    
    @classmethod
    def TestCorrelation(cls):
        
        MSG({}).RequireCorrelation("8e8cb55b-55a8-49a5-9f80-439138e340a2")
        MSG({}).RequireCorrelation("<uuid>")

        with TESTS.AssertValidation('Not a UUID'):
            MSG({}).RequireCorrelation("x")

        TESTS.AssertEqual(
            given= MSG({'Header':{'Correlation':'<uuid>'}}).RequireCorrelation(),
            expect= '<uuid>')
        
        m= MSG({'Header':{}})
        m.RequireCorrelation('<uuid>')
        TESTS.AssertEqual(m.Envelope(), {'Header':{'Correlation':'<uuid>'},'Body':{}})
                

    @classmethod
    def TestSignature(cls):
        
        TESTS.AssertEqual(
            given= MSG({'Signature':'x'}).RequireSignature(),
            expect= 'x')
        
        m= MSG({'Header':{}})
        m.RequireSignature('x')
        TESTS.AssertEqual(
            m.Envelope(), 
            {'Header':{},'Body':{}, 'Signature':'x'})

        MSG({}).RequireSignature('x')


    @classmethod
    def TestHash(cls):
        
        TESTS.AssertEqual(
            given= MSG({'Hash':'x'}).RequireHash(),
            expect= 'x')
        
        m= MSG({'Header':{}})
        m.RequireHash('x')
        TESTS.AssertEqual(
            m.Envelope(), 
            {'Header':{},'Body':{}, 'Hash':'x'})

        MSG({}).RequireHash('x')
        

    @classmethod
    def TestBody(cls):
        
        # Getter =============================

        # ${Body:x}.Body() -> $x 
        TESTS.AssertEqual( MSG({'Body':{'A':1}}).Body().Obj(), {'A':1} ) 
        
        # ${}.Body() -> ${} (safe gatter)
        TESTS.AssertEqual( MSG({}).Body().Obj(), {} )

        #m=${Body:{x:1}}; a=m.Body(); a.Att(x,2); b=m.Body(); f'{a.Att(x)},{b.Att(x)}' -> '2,1' 
        m= MSG({'Body':{'x':1}})
        
        a= m.Body()
        a.GetAtt('x', set=2)
        TESTS.AssertEqual(a.GetAtt('x'), 2)

        b= m.Body()
        TESTS.AssertEqual(b.GetAtt('x'), 1)

        # Setter =============================
        
        # m=${}; m.Body(1); m.Envelope() -> {Body:1} (safe setter)
        m = MSG({})
        m.Body({'A':1})
        TESTS.AssertEqual(m.Envelope(), {'Header':{},'Body':{'A':1}})

        # m=${Body:1}; m.Body(2); m.Envelope() -> {Body:2} (replace)
        m = MSG({'Body':{'A':1}})
        m.Body({'A':2})
        TESTS.AssertEqual(m.Envelope(), {'Header':{},'Body':{'A':2}})

        # m=${Body:1}; m.Body($2); m.Envelope() -> {Body:2} (unboxing)
        m = MSG({'Body':{'A':1}})
        m.Body(STRUCT({'A':2}))
        TESTS.AssertEqual(
            m.Envelope(), 
            {'Header':{},'Body':{'A':2}})
        

    @classmethod
    def TestMatchMsg(cls):
        m1 = MSG({'Header':{'Subject':1}, 'Body':{}, 'Hash':'', 'Signature':''})
        m2 = MSG({'Header':{'Subject':2}, 'Body':{}, 'Hash':'', 'Signature':''})
        m1.MatchMsg(m1)
        with TESTS.AssertValidation():
            m1.MatchMsg(m2)
        

    @classmethod
    def TestWrap(cls):
        
        # Wrap(to, subject, body) -> ${Header: {To, Subject, SentAt, Correlation}, Body}
        m = MSG.Wrap(to='to', subject='subject', body={'A':1})
        TESTS.AssertEqual(m.RequireTo(), 'to')
        TESTS.AssertEqual(m.RequireSubject(), 'subject')
        TESTS.AssertEqual(m.Body(), {'A':1})
        TESTS.AssertNotEqual(m.GetTimestamp(), None)
        TESTS.AssertNotEqual(m.RequireCorrelation(), None)


    @classmethod
    def TestStamp(cls):

        # ${Header:*}.Stamp() -> ${Header:{*, SentAt, Correlation}}
        m = MSG({'Header':{}})
        m.Stamp()
        TESTS.AssertNotEqual(m.GetTimestamp(), None)
        TESTS.AssertNotEqual(m.RequireCorrelation(), None)
    
    
    @classmethod
    def TestCanonicalize(cls):
        
        # {Header:*, Body:*, Signature, Hash}.Canonicalize() -> '{Header:*,Body:*}'
        m = MSG({'Header':1, 'Body':2, 'Signature':3, 'Hash':4})
        TESTS.AssertEqual(
            given= m.Canonicalize(),
            expect= '{"Header":1,"Body":2}')
        

    @classmethod
    def TestVerifyHeader(cls):

        # ${Header:{From,To,Subject,SentAt,Correlation, *}, *} -> OK
        m = MSG({
            'Header': {
                'From': 'f', 
                'To': 't', 
                'Subject': 's', 
                'SentAt': '2023-04-01T05:00:30.001000Z', 
                'Correlation': '<uuid>', 
                'x': 5
            }, 
            'y': 6
        })
        m.VerifyHeader()
        
        # ${Header:{From,To,Subject,SentAt,Correlation}, Body, *} -> OK
        m = MSG({
            'Header': {
                'From': 'f', 
                'To': 't', 
                'Subject': 's', 
                'SentAt': '2023-04-01T05:00:30.001000Z', 
                'Correlation': '<uuid>', 
                'x': 5
            }, 
            'Body': 6
        })
        m.VerifyHeader()

        # anything else -> Exception!
        with TESTS.AssertValidation():
            MSG({
                'Header': {
                    'To': 't', 
                    'Subject': 's', 
                    'SentAt': '2023-04-01T05:00:30.001000Z', 
                    'Correlation': 'c', 
                    'x': 5
                }, 
                'Body': 6
            }).VerifyHeader()

        with TESTS.AssertValidation():
            m = MSG({
                'Header': {
                    'From': '<same>', 
                    'To': '<same>', 
                    'Subject': 's', 
                    'SentAt': '2023-04-01T05:00:30.001000Z', 
                    'Correlation': 'c'
                }, 
                'Body': 6
            }).VerifyHeader()
        

    @classmethod
    def TestSign(cls):

        with TESTS.AssertValidation():
            MSG({}).Sign(hash=1, signature=1)
        
        MSG({}).Sign(hash='<hash>', signature='<signature>')


    @classmethod
    def TestVerifySignature(cls):
        # self.VerifySignature(publicKey) -> offline validation.
        m = MSG.Wrap(to='t', subject='s', body='b')
        m.RequireFrom('f')
        #TODO: m.VerifySignature()

        #TODO: self.VerifySignature() -> online validation, gets the remote DKIM.
    

    @classmethod
    def TestSend(cls):

        WEB_MOCK.ResetWebMock()
        WEB_MOCK.MockUrl('https://pollyweb.t/inbox', domain='t')

        m = MSG.Wrap(to='t', subject='s', body='b')
        m.RequireFrom('f')
        m.Sign(hash='<hash>', signature='<signature>')
        m.Send()


    @classmethod
    def TestRequire(cls):

        TESTS.AssertEqual(MSG({"A": 1}).RequireAtt('A'), 1)
        TESTS.AssertEqual(MSG({'Host': 1}).RequireAtt('Host'), 1)

        TESTS.AssertEqual(MSG({'Body': {}}).GetAtt('A', default=1), 1)

        #OLD:TESTS.AssertEqual(MSG({'Body': {'A':None}}).Att('A', default=1), None)
        TESTS.AssertEqual(MSG({'Body': {'A':None}}).GetAtt('A', default=1), 1)

        TESTS.AssertEqual(MSG({'Body': {'A':''}}).GetAtt('A', default=1), '')
        TESTS.AssertEqual(MSG({'Body': {}}).GetAtt('A', default=1), 1)

        with TESTS.AssertValidation('A=None fails on required, even with default'):
            TESTS.AssertEqual(MSG({'Body': {'A':None}}).RequireAtt('A', default=1), None)


    @classmethod
    def TestAllMsg(cls):
        LOG.Print('MSG_TESTS.TestAllMsg() ==============================')

        cls.TestEnvelope()
        cls.TestHeader()
        cls.TestSubject()
        cls.TestFrom()
        cls.TestTo()
        cls.TestSentAt()
        cls.TestCorrelation()
        cls.TestSignature()
        cls.TestHash()
        cls.TestBody()
        cls.TestMatchMsg()
        cls.TestWrap()
        cls.TestStamp()
        cls.TestCanonicalize()
        cls.TestVerifyHeader()
        cls.TestSign()
        #cls.TestVerifySignature()
        cls.TestSend()
        cls.TestRequire()
        