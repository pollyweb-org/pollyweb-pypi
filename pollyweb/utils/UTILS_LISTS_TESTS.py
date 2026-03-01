from .TESTS import TESTS
from .UTILS_LISTS import UTILS_LISTS
from .STRUCT import STRUCT


class UTILS_LISTS_TESTS(UTILS_LISTS):


    @classmethod
    def TestContainsAny(cls):
        TESTS.AssertTrue(cls.ContainsAny([1,2,3], [1,6]))
        TESTS.AssertTrue(cls.ContainsAny([1,2,3], [0,3]))
        TESTS.AssertFalse(cls.ContainsAny([1,2,3], [5,6]))
        
        with TESTS.AssertValidation('Empty list'):
            TESTS.AssertFalse(cls.ContainsAny([], [1]))
        with TESTS.AssertValidation('Empty list'):
            TESTS.AssertFalse(cls.ContainsAny([1], []))

    
    @classmethod
    def TestVerifyDuplicates(cls):

        cls.VerifyDuplicates(None)
        cls.VerifyDuplicates([])
        with TESTS.AssertValidation():
            cls.VerifyDuplicates({})
        with TESTS.AssertValidation():
            cls.VerifyDuplicates('A')
        
        cls.VerifyDuplicates([1,2,3])
        with TESTS.AssertValidation():
            cls.VerifyDuplicates([1,2,2])

        cls.VerifyDuplicates(['A','B'])
        with TESTS.AssertValidation():
            cls.VerifyDuplicates(['A','B','A'])

        cls.VerifyDuplicates([0,1,True,2,False])
        with TESTS.AssertValidation():
            cls.VerifyDuplicates([0,1,True,2,False,True])

        cls.VerifyDuplicates([{'A':1},{'A':2}])
        with TESTS.AssertValidation():
            cls.VerifyDuplicates([{'A':1},{'A':1}])
        
        cls.VerifyDuplicates([STRUCT({'A':1}),{'A':2}])
        with TESTS.AssertValidation():
            cls.VerifyDuplicates([STRUCT({'A':2}),{'A':2}])


    @classmethod
    def TestAppendIfMissing(cls):
        
        cls.AppendIfMissing([], 1)
        with TESTS.AssertValidation():
            cls.AppendIfMissing({}, 1)
        with TESTS.AssertValidation():
            cls.AppendIfMissing('', 1)
        with TESTS.AssertValidation():
            cls.AppendIfMissing(None, 1)

        lst = [1,2]
        cls.AppendIfMissing(lst, 3)
        TESTS.AssertEqual(lst, [1,2,3])
        cls.AppendIfMissing(lst, 3)
        TESTS.AssertEqual(lst, [1,2,3])
        cls.AppendIfMissing(lst, 4)
        TESTS.AssertEqual(lst, [1,2,3,4])


    @classmethod
    def TestRequireStrings(cls):
        cls.RequireStrings(["abc"])
        cls.RequireStrings(["abc", 'def'])

        with TESTS.AssertValidation():
            cls.RequireStrings([None])
        with TESTS.AssertValidation():
            cls.RequireStrings([123])
        with TESTS.AssertValidation():
            cls.RequireStrings([1, 2, 3])
        with TESTS.AssertValidation():
            cls.RequireStrings([1, 'a', 'asd'])
        with TESTS.AssertValidation():
            cls.RequireStrings([None, 'a', 'asd'])



    @classmethod
    def TestRequireList(cls):

        cls.RequireList([1,2,3])
        cls.RequireList([1,2,'asd'])
        cls.RequireList([None])

        with TESTS.AssertValidation():
            cls.RequireList(None)
        with TESTS.AssertValidation():
            cls.RequireList([])
        with TESTS.AssertValidation():
            cls.RequireList(123)
        with TESTS.AssertValidation():
            cls.RequireList("abc")


    @classmethod
    def TestAssertIsList(cls):

        cls.AssertIsList(None)
        cls.AssertIsList([1,2,3])
        cls.AssertIsList([1,2,3], require=True)
        cls.AssertIsList([1,2,3], itemType=int)
        cls.AssertIsList([1,2,3], require=True, itemType=int)  

        with TESTS.AssertValidation():
            cls.AssertIsList(None, require=True)
        with TESTS.AssertValidation():
            cls.AssertIsList([], require=True)
        with TESTS.AssertValidation():
            cls.AssertIsList(123)
        with TESTS.AssertValidation():
            cls.AssertIsList("abc")
        with TESTS.AssertValidation():
            cls.AssertIsList([1,2,3], itemType=str)
        with TESTS.AssertValidation():
            cls.AssertIsList([1,2,3], require=True, itemType=str)  


    @classmethod
    def TestAssertIsDict(cls):

        cls.AssertIsDict(None)
        cls.AssertIsDict({'a':1, 'b':2})
        cls.AssertIsDict(STRUCT({'a':1}))
        cls.AssertIsDict({}, require=True)
        cls.AssertIsDict({'a':1}, require=True)
        cls.AssertIsDict({'a':1}, itemType=int)

        with TESTS.AssertValidation():
            cls.AssertIsDict(None, require=True)
        with TESTS.AssertValidation():
            cls.AssertIsDict(123)
        with TESTS.AssertValidation():
            cls.AssertIsDict("abc")
        with TESTS.AssertValidation():
            cls.AssertIsDict(["a"])
        with TESTS.AssertValidation():
            cls.AssertIsDict({'a':1}, type=str)


    @classmethod
    def TestDicFromList(cls):

        # Test with a list of dictionaries.
        l = [
            {'A':'10', 'B':'20'},
            {'A':'11', 'B':'21'},
            {'A':'12', 'B':'22'},
        ]
        d = cls.DictFromList(l, key='B')
        TESTS.AssertEqual(d['20']['A'], '10')
        TESTS.AssertEqual(d['21']['A'], '11')
        TESTS.AssertEqual(d['22']['A'], '12')

        # Test with a list of STRUCTs.
        l = [
            STRUCT({'A':'10', 'B':'20'}),
            STRUCT({'A':'11', 'B':'21'}),
            STRUCT({'A':'12', 'B':'22'}),
        ]
        d = cls.DictFromList(l, key='B')
        TESTS.AssertEqual(d['20']['A'], 10)
        TESTS.AssertEqual(d['21']['A'], 11)
        TESTS.AssertEqual(d['22']['A'], 12)

        # Test with a list of mixed dictionaries and STRUCTs.
        l = [
            {'A':'10', 'B':'20'},
            STRUCT({'A':'11', 'B':'21'}),
            {'A':12, 'B':'22'},
        ]
        d = cls.DictFromList(l, key='B')
        TESTS.AssertEqual(d['20']['A'], '10')
        TESTS.AssertEqual(d['21']['A'], '11')
        TESTS.AssertEqual(d['22']['A'], '12')

        # Test with a class that implements STRUCT, using key a function.
        class CLASS(STRUCT):
            def GetKey(self):
                return self.GetAtt('B')
        l = [
            CLASS({'A':'10', 'B':'20'}),
            CLASS({'A':'11', 'B':'21'}),
        ]
        d = cls.DictFromList(l, key='GetKey')
        TESTS.AssertEqual(d['20']['A'], '10')
        TESTS.AssertEqual(d['21']['A'], '11')


    @classmethod
    def TestAssertIsAny(cls):
        TESTS.AssertEquals([
            [cls.AssertIsAnyValue(1, [1,2,3]), None],
            [cls.AssertIsAnyValue(True, [True]), None],
            [cls.AssertIsAnyValue('a', ['a']), None]
        ])

        with TESTS.AssertValidation():
            cls.AssertIsAnyValue(4, [1,2,3])
        

    @classmethod
    def TestDictFromList(cls):
        
        TESTS.AssertEqual(
            cls.DictFromList([
                {'key': 'a', 'val': 1}, 
                {'key': 'b', 'val': 2}
            ], key='key'),
            {
                'a': {'key': 'a', 'val': 1},
                'b': {'key':'b', 'val': 2}
            })
        
        TESTS.AssertEqual(
            cls.DictFromList([
                STRUCT({'key': 'a', 'val': 1}), 
                STRUCT({'key': 'b', 'val': 2})
            ], key='key'),
            {
                'a': {'key': 'a', 'val': 1},
                'b': {'key':'b', 'val': 2}
            })
        
        with TESTS.AssertValidation():
            cls.DictFromList([1,2], key='key')


    @classmethod
    def TestSortList(cls):

        # -----------------------------
        # Without key.
        # -----------------------------

        TESTS.AssertEqual(
            cls.SortList([]),
            [])
        
        TESTS.AssertEqual(
            cls.SortList([1,3,2]),
            [1,2,3])
        
        TESTS.AssertEqual(
            cls.SortList(['a','c','b']),
            ['a','b','c'])
        
        with TESTS.AssertValidation('Provide a key when using dictionaries'):
            cls.SortList([{'a': 2}, {'a': 1}])
        
        # -----------------------------
        # With key.
        # -----------------------------

        TESTS.AssertEqual(
            cls.SortList([], key='a'),
            [])
        
        TESTS.AssertEqual(
            cls.SortList([{'a': 1}], key='a'),
            [{'a': 1}])
        
        TESTS.AssertEqual(
            cls.SortList([{'a': 2}, {'a': 1}], key='a'),
            [{'a': 1}, {'a': 2}])
        
        TESTS.AssertEqual(
            cls.SortList([{'a': 2}, {'a': 1}, {'a': 4}], key='a'),
            [{'a': 1}, {'a': 2}, {'a': 4}])

        TESTS.AssertEqual(
            cls.SortList([{'a': 1}, {'a': 2}], key='a'),
            [{'a': 1}, {'a': 2}])
        
        with TESTS.AssertValidation('when providing a key, all items should have the key.'):
            cls.SortList([{'a': 1}, {'b': 2}], key='a')

        with TESTS.AssertValidation('the list should not be empty.'):
            cls.SortList(None)

        with TESTS.AssertValidation('the list should not be empty.'):
            cls.SortList(None, key='a')

        with TESTS.AssertValidation('When providing a key, the list must be a list of dictionaries.'):
            cls.SortList([1,2,3], key='a')

        # -----------------------------
        # With method key.
        # -----------------------------

        class X(STRUCT):

            def __init__(self, a):
                super().__init__(a)
            
            def getA(self):
                return self._obj
            
        TESTS.AssertEqual(
            cls.SortList([X(1), X(3), X(2)], key='getA'),
            [X(1), X(2), X(3)])


    @classmethod
    def TestAssertLenght(cls):
        TESTS.AssertEqual(cls.AssertLenght('', 0), None)
        TESTS.AssertEqual(cls.AssertLenght('a', 1), None)
        TESTS.AssertEqual(cls.AssertLenght([], 0), None)
        TESTS.AssertEqual(cls.AssertLenght([True], 1), None)

        with TESTS.AssertValidation():
            cls.AssertLenght('', 1)

        with TESTS.AssertValidation(): 
            cls.AssertLenght([], 1)
        

    @classmethod
    def TestReverseStrList(cls):
        
        TESTS.AssertEqual(cls.ReverseStrList([]), [])
        TESTS.AssertEqual(cls.ReverseStrList(['a']), ['a'])
        TESTS.AssertEqual(cls.ReverseStrList(['a','b']), ['b','a'])
        TESTS.AssertEqual(cls.ReverseStrList(['a','b','c']), ['c','b','a'])
        TESTS.AssertEqual(cls.ReverseStrList(['abc','def']), ['def','abc'])
        
        with TESTS.AssertValidation():
            cls.ReverseStrList('abc')

        with TESTS.AssertValidation():
            cls.ReverseStrList(None)


    @classmethod
    def TestRemoveEmptyStrings(cls):
        TESTS.AssertEqual(cls.RemoveEmptyStrings(None), None)
        TESTS.AssertEqual(cls.RemoveEmptyStrings([]), [])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['']), [])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['a']), ['a'])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['a','']), ['a'])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['  ','b']), ['b'])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['a','b','']), ['a','b'])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['a','    ','c']), ['a','c'])
        TESTS.AssertEqual(cls.RemoveEmptyStrings(['  ','','c']), ['c'])


    @classmethod
    def TestAllLists(cls):
                
        cls.TestContainsAny()
        cls.TestVerifyDuplicates()
        cls.TestAppendIfMissing()

        cls.TestRequireStrings()
        cls.TestRequireList()
        
        cls.TestAssertIsList()
        cls.TestAssertIsDict()
        cls.TestDicFromList()

        cls.TestAssertIsAny()
        cls.TestDictFromList()
        cls.TestSortList()

        cls.TestAssertLenght()
        cls.TestReverseStrList()
        cls.TestRemoveEmptyStrings()