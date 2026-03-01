# 📚 CODE

from .ITEM import ITEM
from .CODE import CODE
from pollyweb import UTILS
from pollyweb import LOG
from pollyweb import TESTS

class CODE_TESTS(CODE):


    @classmethod
    def TestParseDomain(cls):
        TESTS.AssertEqual(CODE.ParseAuthority('authority/A/B/C'), 'authority')
        TESTS.AssertEqual(CODE.ParseAuthority('   authority/A/B/C'), 'authority')
        TESTS.AssertEqual(CODE.ParseAuthority('authority/A'), 'authority')
        TESTS.AssertEqual(CODE.ParseAuthority('authority'), None)
        TESTS.AssertEqual(CODE.ParseAuthority('/A/B/C'), None)


    @classmethod
    def TestParsePath(cls):
        TESTS.AssertEqual(CODE.ParsePath('authority/A/B/C'), '/A/B/C')
        TESTS.AssertEqual(CODE.ParsePath('authority/A   '), '/A')
        TESTS.AssertEqual(CODE.ParsePath('authority/A'), '/A')
        TESTS.AssertEqual(CODE.ParsePath('authority'), None)
        TESTS.AssertEqual(CODE.ParsePath('/A/B/C'), None)


    @classmethod
    def TestParseRoot(cls):
        TESTS.AssertEqual(CODE.ParseRoot('authority/A/B/C'), '/A')
        TESTS.AssertEqual(CODE.ParseRoot('authority/A/*'), '/A')
        TESTS.AssertEqual(CODE.ParseRoot('authority/A'), '/A')
        TESTS.AssertEqual(CODE.ParseRoot('authority/*'), '/*')
        TESTS.AssertEqual(CODE.ParseRoot('authority/A  '), '/A')
        TESTS.AssertEqual(CODE.ParseRoot('authority'), None)
        TESTS.AssertEqual(CODE.ParseRoot('/A/B/C'), None)


    @classmethod
    def TestAllCode(cls):
        cls.TestParseDomain()
        cls.TestParsePath()
        cls.TestParseRoot()