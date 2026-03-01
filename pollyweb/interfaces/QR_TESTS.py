from .QR import QR
from pollyweb import TESTS
from ..utils import LOG
   

class QR_TESTS(QR):
   
   
    @classmethod
    def Test__str__(cls):
        s = '🤝pollyweb.org/QR,1,any-printer.com,7V8KD3G'
        q = QR(s)
        TESTS.AssertEqual(f'{q}', s)


    @classmethod
    def Test_parse(cls):
        q = QR('🤝pollyweb.org/QR,1,any-printer.com,7V8KD3G')

        with TESTS.AssertValidation('Missing icon'):
            QR('pollyweb.org/QR,1,any-printer.com,7V8KD3G')

        TESTS.AssertEqual(q.Obj(), {
            'QR': '🤝pollyweb.org/QR,1,any-printer.com,7V8KD3G', 
            'Code': 'pollyweb.org/QR', 
            'Version': '1', 
            'Domain': 'any-printer.com', 
            'Locator': '7V8KD3G'
        })
            

    @classmethod
    def TestIsHostCode(cls):

        q = QR('🤝pollyweb.org/QR,1,any-printer.com,7V8KD3G')
        TESTS.AssertFalse(q.IsHostCode())

        q = QR('🤝pollyweb.org/HOST,1,any-printer.com,7V8KD3G')
        TESTS.AssertTrue(q.IsHostCode())
    

    @classmethod
    def TestAllQR(cls):
        LOG.Print('QR_TESTS.TestAllQR() ==============================')

        cls.Test__str__()
        cls.Test_parse()
        cls.TestIsHostCode()
    