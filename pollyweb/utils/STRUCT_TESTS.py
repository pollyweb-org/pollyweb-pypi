# 📚 STRUCT TESTS

from __future__ import annotations

from .TESTS import TESTS
from .UTILS import UTILS
from .STRUCT import STRUCT
from .LOG import LOG


# ✅ DONE
class TestCastStructsClass(STRUCT):
    pass


# ✅ DONE 
class STRUCT_TESTS(STRUCT):


    @classmethod
    def TestInit(cls):
        TESTS.AssertEquals([
            [STRUCT({}).Obj(), {}],
            [STRUCT(STRUCT({})).Obj(), {}],
            [STRUCT({'a':1}).Obj(), {'a':1}],
            [STRUCT(None).Obj(), None]
        ])

    
    @classmethod
    def TestMapAtt(cls):
        TESTS.AssertEqual(
            STRUCT({'a':1}).GetAtt('b'), 
            None)
        
        TESTS.AssertEqual(
            STRUCT({'a':1}).MapAtt(alias='b',att='a').GetAtt('b'), 
            1)
        
        TESTS.AssertEqual(
            STRUCT({
                'a':{'x':2}
            }).MapAtt(
                alias='b', att='a.x'
            ).RequireAtt('b', noHierarchy=False), 
            2)


    @classmethod
    def TestUnstruct(cls):
        TESTS.AssertEquals([
            [cls.Unstruct(1), 1],
            [cls.Unstruct(STRUCT(1)), 1],
            [cls.Unstruct({'a':1}), {'a':1}],
            [cls.Unstruct(STRUCT({'a':1})), {'a':1}]
        ])
        

    @classmethod
    def TestObj(cls):
        TESTS.AssertEquals([
            [STRUCT({'a':1}).Obj(), {'a':1}],
            [STRUCT(None).Obj(), None],
            [STRUCT({}).Obj(), {}],
            [STRUCT({}).Obj({'a':1}), {'a':1}],
            [STRUCT({}).Obj(STRUCT({'a':1})), {'a':1}],
            [STRUCT({}).Obj(None), {}]
        ])


    @classmethod 
    def TestStr(cls):

        TESTS.AssertEqual(
            given= str(STRUCT({'a':1})), 
            expect= '{\n  "a": 1\n}')
        
        TESTS.AssertEqual(
            given= str(STRUCT(None)), 
            expect= 'None')


    @classmethod
    def TestEquals(cls):

        TESTS.AssertTrue(UTILS.IsType({}, dict))
        TESTS.AssertFalse(UTILS.IsType(STRUCT({}), dict))

        TESTS.AssertEquals([
            [STRUCT({'a':1}), {'a':1}],
            [STRUCT('a'), 'a'],
            [STRUCT(True), True]
        ])


    @classmethod
    def TestSetAttRoot(cls):
        
        TESTS.AssertEqual( STRUCT({'a':1,'b':{'y':2}}).SetAttRoot('b').GetAtt('y'),  2)
        # Looks at the top, if not found on the root.
        TESTS.AssertEqual( STRUCT({'a':1,'b':{'y':2}}).SetAttRoot('b').GetAtt('a'), 1)
        TESTS.AssertEqual( STRUCT({'a':{'x:':1},'b':{'y':2}}).SetAttRoot('b').GetAtt('x'), None)

        TESTS.AssertEqual( STRUCT({'a':1,'b':{'x':3,'c':{'y':2}}}).SetAttRoot('b.c', noHierarchy=False).GetAtt('y', noHierarchy=False), 2)
        TESTS.AssertEqual( STRUCT({'a':1,'b':{'x':3,'c':{'y':2}}}).SetAttRoot('b.c', noHierarchy=False).GetAtt('a', noHierarchy=False), 1)
        TESTS.AssertEqual( STRUCT({'a':1,'b':{'x':3,'c':{'y':2}}}).SetAttRoot('b.c', noHierarchy=False).GetAtt('x', noHierarchy=False), None)

        TESTS.AssertEqual( STRUCT({'a':{}}).SetAttRoot('a').SetAtt('b', 1), {'a':{},'b':1})

        with TESTS.AssertValidation():
            STRUCT({}).SetAttRoot('x') 

        with TESTS.AssertValidation():
            STRUCT({'x':1}).SetAttRoot(None)
        

    @classmethod
    def TestSetAtt(cls):
        TESTS.AssertEqual(STRUCT({'a':1}).SetAtt('a', 2).Obj(), {'a':2})
        TESTS.AssertEqual(STRUCT({'a':1}).SetAtt('a', None).Obj(), {'a':None})
        

    @classmethod
    def TestAtt(cls):
        TESTS.AssertEquals([
            [STRUCT({'a':1}).GetAtt('a'), 1],
            [STRUCT({'a':{'b':2}}).GetAtt('a'), {'b':2}],
            [STRUCT({'a':{'b':2}}).GetAtt('a.b', noHierarchy=False), 2],
            [STRUCT({}).GetAtt('a'), None],
            [STRUCT({}).GetAtt('a', default=1), 1],
            [STRUCT({}).GetAtt('a', set=1), 1]
        ])
        
        s = STRUCT({})
        s.GetAtt('a', default='x')
        TESTS.AssertEqual(s.Obj(), {})
        
        s.GetAtt('a', set=1)
        TESTS.AssertEqual(s.Obj(), {'a':1})

        s = STRUCT({})
        s.GetAtt('b', set=STRUCT(2))
        TESTS.AssertEqual(s.Obj(), {'b':2})

        # Test setting an empty object.
        s = STRUCT()
        s.Obj({'A': 1})
        TESTS.AssertEqual(s.Obj()['A'], 1)
        TESTS.AssertEqual(s.GetAtt('A'), 1)

        # Test accesing an empty object.
        s = STRUCT()
        with TESTS.AssertValidation():        
            s.GetAtt('A')
    

    @classmethod
    def TestRequireBool(cls):

        TESTS.AssertEquals([
            [STRUCT({'a':True}).RequireBool('a'), True],
            [STRUCT({'a':False}).RequireBool('a'), False],
            [STRUCT({'a':{'b':False}}).RequireBool('a.b', noHierarchy=False), False]
        ])
        
        s = STRUCT({})
        TESTS.AssertEquals([
            [s.RequireBool('a', True), True],
            [s, {'a':True}]
        ])

        s = STRUCT({'a':False})
        TESTS.AssertEquals([
            [s.RequireBool('a', True), True],
            [s, {'a':True}]
        ])

        s = STRUCT({'a':False})
        TESTS.AssertEquals([
            [s.RequireBool('a', None), False],
            [s, {'a':False}]
        ])

        with TESTS.AssertValidation():
            STRUCT({}).RequireBool(att=None)

        with TESTS.AssertValidation():
            STRUCT({'a':'x'}).RequireBool('a')

        with TESTS.AssertValidation():
            STRUCT({}).RequireBool('a')

        with TESTS.AssertValidation():
            STRUCT({'a':None}).RequireBool('a')
        

    @classmethod
    def TestRequireStr(cls):

        TESTS.AssertEqual(
            STRUCT({'a':'1'}).RequireStr('a'), 
            '1')
        
        TESTS.AssertEqual(
            STRUCT({'a':{'b':'2'}}).RequireDeepStr('a.b'), 
            '2')
        
        s=STRUCT({})
        s.RequireStr('a', '1'); 
        TESTS.AssertEqual(s.Obj(), {'a':'1'})

        s=STRUCT({'a':'1'})
        s.RequireStr('a', 'y') 
        TESTS.AssertEqual(s.Obj(), {'a':'y'})

        with TESTS.AssertValidation():
            STRUCT({}).RequireStr(att=None) #attribute name is required

        with TESTS.AssertValidation():
            STRUCT({}).RequireStr('a')  #should exist

        with TESTS.AssertValidation():
            STRUCT({'a':True}).RequireStr('a') #should be a string

        with TESTS.AssertValidation():
            STRUCT({'a':'  '}).RequireStr('a') #should not be empty

        with TESTS.AssertValidation():
            STRUCT({'a':'x'}).RequireStr('a', True) #setter should be a string
        
        with TESTS.AssertValidation():
            STRUCT({'a':{}}).RequireDeepStr('a.b', '1')


        STRUCT({
            "Function": "bindable-codes",
            "Session": {
                "Host": "amazon.com",
                "Locator": "website",
                "Broker": "any-broker.org",
                "SessionID": "aa78e74c-9a31-4434-95d2-db8957a99c5c"
            },
            "Prompts": [
                {
                    "StepID": "TOP",
                    "Message": "TOP",
                    "Result": "OK",
                    "Answer": "Bind",
                    "SentAt": "2023-08-26T21:24:02.652816+00:00Z"
                }
            ],
            "Result": None
        }).RequireDeepStr('Session.Host')


    @classmethod
    def TestRequireTimestamp(cls):
        
        TESTS.AssertEqual(
            STRUCT({'a':'2023-04-01T05:00:30.001000Z'}).RequireTimestamp('a'), 
            '2023-04-01T05:00:30.001000Z'
        )

        with TESTS.AssertValidation():
            STRUCT({'a':'2023-04-01T05:00:30.001000'}).RequireTimestamp('a')

        with TESTS.AssertValidation():
            STRUCT({'a':'x'}).RequireTimestamp('a')

        with TESTS.AssertValidation():
            STRUCT({}).RequireTimestamp(att=None)
        

    @classmethod
    def TestRequire(cls):

        TESTS.AssertEquals([
            [STRUCT(1).Require(), 1],
            [STRUCT(False).Require(), False],
            [STRUCT({'a':1}).RequireAtt('a'), 1],
            [STRUCT({'a':{}}).RequireAtt('a'), {}],
            [STRUCT({'a':False}).RequireAtt('a'), False],
            [STRUCT({}).RequireAtt('a', set=1), 1],
            [STRUCT({'a':{'b':1}}).RequireAtt('a.b', noHierarchy=False), 1],
            [STRUCT({}).RequireAtt('a', set={}), {}]
        ])

        TESTS.AssertEqual(
            given= STRUCT({"Host": "any-host.org", "Header": {}, "Body": {}}).RequireAtt('Host'),
            expect= "any-host.org"
        )
        
        with TESTS.AssertValidation():
            STRUCT({}).Require()

        with TESTS.AssertValidation():
            STRUCT(None).Require()

        with TESTS.AssertValidation():
            STRUCT({'a':None}).RequireAtt('a')

        with TESTS.AssertValidation():
            STRUCT({'a':''}).RequireAtt('a')


    @classmethod
    def TestMatch(cls):

        STRUCT({'a':1}).Match('a', 1)

        with TESTS.AssertValidation():
            STRUCT({'a':1}).Match('a', 2)

        with TESTS.AssertValidation():
            STRUCT({}).Match('a', {})

        with TESTS.AssertValidation():
            STRUCT(None).Match('a', None)

        with TESTS.AssertValidation():
            STRUCT({'a':1}).Match(None, 1)
        

    @classmethod
    def TestGetDict(cls):
        TESTS.AssertEqual(STRUCT({'a':1}).GetDict(), {'a':1})
        TESTS.AssertEqual(STRUCT(None).GetDict(), None)
        TESTS.AssertEqual(STRUCT({'a':None}).GetDict('a'), None)
        TESTS.AssertEqual(STRUCT({}).GetDict(), {})
        TESTS.AssertEqual(STRUCT({'a':{}}).GetDict('a'), {})
        TESTS.AssertEqual(STRUCT({'a':{'b':1}}).GetDict('a'), {'b':1})
        TESTS.AssertEqual(STRUCT({'a':1}).GetDict('b'), None)
        
        with TESTS.AssertValidation():
            STRUCT({'a':1}).GetDict('a')


    @classmethod
    def TestRequireDict(cls):
        
        TESTS.AssertEqual(
            STRUCT({'a':{}}).RequireDict('a'),
            {})

        TESTS.AssertEqual(
            STRUCT({'a':{'x':1},'b':2}).RequireDict('a'), 
            {'x':1})

        with TESTS.AssertValidation():
            STRUCT({'a':1}).RequireDict('a')

        with TESTS.AssertValidation():
            STRUCT({'a':None}).RequireDict('a')

        with TESTS.AssertValidation():
            STRUCT({'a':' '}).RequireDict('a')

        with TESTS.AssertValidation():
            STRUCT({}).RequireDict('a')

        with TESTS.AssertValidation():
            STRUCT({}).RequireDict(None)



    @classmethod
    def TestRequireStruct(cls):

        s = STRUCT({})
        s.RequireStruct('a', set={})

        TESTS.AssertEqual(
            STRUCT({'a':{'x':1},'b':2}).RequireStruct('a'), 
            STRUCT({'x':1}))
        TESTS.AssertClass(
            STRUCT({'a':{'x':1},'b':2}).RequireStruct('a'), 
            STRUCT)
        TESTS.AssertEqual(
            STRUCT({'a':{'b':{'y':2}}}).RequireStruct('a.b', noHierarchy=False), 
            STRUCT({'y':2}))
        TESTS.AssertClass(
            STRUCT({'a':{'b':{'y':2}}}).RequireStruct('a.b', noHierarchy=False), 
            STRUCT)
        TESTS.AssertEqual(
            STRUCT({'a':{}}).RequireStruct('a'), 
            STRUCT({}))

        with TESTS.AssertValidation():
            STRUCT({'a':[]}).RequireStruct('a') # should be a dictionary

        with TESTS.AssertValidation():
            STRUCT({'b':1}).RequireStruct('a') # att must exist

        with TESTS.AssertValidation():
            STRUCT({'a':None}).RequireStruct('a') # att cannot be null

        with TESTS.AssertValidation():
            STRUCT({'a':' '}).RequireStruct('a') # att cannot be an empty string

        with TESTS.AssertValidation():
            STRUCT({}).RequireStruct('a') # the struct cannot be empty

        with TESTS.AssertValidation():
            STRUCT({}).RequireStruct(None) # the att name must be provided
        

    @classmethod
    def TestStruct(cls):

        a = STRUCT({'a':{'x':1},'b':2}).GetStruct('a')
        TESTS.AssertEqual(a, STRUCT({'x':1}))
        TESTS.AssertClass(a, STRUCT)

        a = STRUCT({'a':{'x':{}},'b':2}).GetStruct('a.x', noHierarchy=False)
        TESTS.AssertEqual(a, STRUCT({})) # reads children
        TESTS.AssertClass(a, STRUCT)

        a = STRUCT({}).GetStruct('a')
        TESTS.AssertEqual(a, STRUCT(None)) # safe missing
        TESTS.AssertClass(a, STRUCT)

        with TESTS.AssertValidation():
            a = STRUCT(None).GetStruct('a')
        #TESTS.AssertEqual(a, STRUCT(None)) 
        #TESTS.AssertClass(a, STRUCT)

        a = STRUCT({'a':1}).GetStruct('b')
        TESTS.AssertEqual(a, STRUCT(None)) # safe missing
        TESTS.AssertClass(a, STRUCT)
        
        with TESTS.AssertValidation():
            STRUCT({'a':1}).GetStruct(None) # the att name must be provided


    @classmethod
    def TestListStr(cls):
        TESTS.AssertEqual(STRUCT([1,'x']).ListStr(), ['1','x'])
        TESTS.AssertEqual(STRUCT({'a':[1,'x']}).ListStr(att='b'), [])
        TESTS.AssertEqual(STRUCT({'a':[1,'x']}).ListStr(att='a'), ['1','x'])

        with TESTS.AssertValidation():
            STRUCT({'a':[1,'x']}).ListStr()
        

    @classmethod
    def TestGetList(cls):
        
        TESTS.AssertEquals([ # Without att:
            [STRUCT(None).GetList(), []], # (safe missing)
            [STRUCT([]).GetList(), []], # reads root
            [STRUCT([1,2,3]).GetList(), [1,2,3]], # reads root
            [STRUCT([{},{}]).GetList(), [{},{}]] #reads root
        ])
        
        TESTS.AssertEquals([ # With att:
            [STRUCT({'a':[1,2,3]}).GetList('a'), [1,2,3]], # (reads attributes)
            [STRUCT({'a':[{},{}]}).GetList('a'), [{},{}]], # (reads attributes)
            [STRUCT({'a':[{},{}]}).GetList('b'), []] # (safe missing)
        ])

        TESTS.AssertEquals([ # With part:
            [STRUCT({'a':[{'x':1,'y':5},{'x':2,'y':6}]}).GetList('a', part='x'), [1,2]] # (reads atts of elements)    
        ])

        with TESTS.AssertValidation():
            STRUCT({'a':1}).GetList(att='a') # Att not a list.

        with TESTS.AssertValidation():
            STRUCT({}).GetList() # Not a list.

        STRUCT([]).GetList(itemType=int) 
        with TESTS.AssertValidation('Invalid type None'):
            STRUCT([None]).GetList(itemType=int) 

        STRUCT([1,2,3]).GetList(itemType=int) 
        with TESTS.AssertValidation('Invalid type int'):
            STRUCT([1,2,3]).GetList(type=str) 

        STRUCT([{'a':1}]).GetList(itemType=dict) 
        with TESTS.AssertValidation('Invalid type dict'):
            STRUCT([{'a':1}]).GetList(type=int) 
    

    @classmethod
    def TestSize(cls):
        TESTS.AssertEquals([
            [STRUCT([]).Size(), 0],
            [STRUCT([1,2,3]).Size(), 3],
            [STRUCT([{},{},{}]).Size(), 3],
            [STRUCT({'a':[]}).Size('a'), 0],
            [STRUCT({'a':[{},{},{}]}).Size('a'), 3]
        ])
        '''
        * ${...}.Size() -> Untested behaviour!
        * ${a:{...}}.Size(a) -> Untested behaviour!
        '''
        

    @classmethod
    def TestRemoveFirst(cls):

        # Without filter.
        s = STRUCT([{'a':1}, {'a':2}, {'a':3}]).RemoveFirst()
        TESTS.AssertEqual(s, STRUCT([{'a':2}, {'a':3}]))
        TESTS.AssertClass(s, STRUCT)

        # By name.
        s = STRUCT([{'a':1}, {'a':2}, {'a':3}]).RemoveFirst('a', equals=2)
        TESTS.AssertEqual(s, STRUCT([{'a':1}, {'a':3}]))
        TESTS.AssertClass(s, STRUCT)
        
        # Empty list.
        s = STRUCT([]).RemoveFirst('a', equals=2) 
        TESTS.AssertEqual(s, STRUCT([]))
        TESTS.AssertClass(s, STRUCT)
         
        # Missing attribute.
        with TESTS.AssertValidation():
            STRUCT({'a':1}).RemoveFirst('a', equals=1)
        
        
    @classmethod
    def TestFirst(cls):

        TESTS.AssertEquals([
            [STRUCT([{'a':1}, {'b':1}]).First(), STRUCT({'a':1})],
            [STRUCT(None).First(), STRUCT({})],
            [STRUCT([{'a':7}]).First('a', equals=8), STRUCT({})],
            [STRUCT(None).First('a', equals=8), STRUCT({})]
        ])
        
        TESTS.AssertEqual( 
            STRUCT([{'a':7,'b':1}, {'a':8,'b':2}, {'a':9,'b':3}]).First('a', equals=8), 
            STRUCT({'a':8,'b':2})
        )
        
    
    @classmethod
    def TestWhere(cls):
        with TESTS.AssertValidation():
            STRUCT([]).Where('a', equals=0)

        return
        
        given= STRUCT([{'a':0,'b':1}, {'a':0,'b':2}, {'a':9,'b':3}]).Where('a', equals=0),
        expected= [STRUCT({'a':0,'b':1}), STRUCT({'a':0,'b':2})]
        print(type(given))
        print(type(expected))
        TESTS.AssertEqual(
            given= [x.Obj() for x in given],
            expect= [x.Obj() for x in expected]
        )

        TESTS.AssertEqual(
            given= STRUCT([{'a':7,'b':1}, {'a':8,'b':2}, {'a':8,'b':3}]).Where('a', equals=8, part='b'),
            expect= [STRUCT(2), STRUCT(3)]
        )
        TESTS.AssertEquals([
            [STRUCT([{'a':0}]).Where('a', equals=1), []],
            [STRUCT(None).Where('a', equals=1), []]
        ])
        

    @classmethod
    def TestPop(cls):
        
        s = STRUCT({'a':[1,2,3]})
        TESTS.AssertEqual(s.Pop('a'), STRUCT(3))
        TESTS.AssertEqual(s, STRUCT({'a':[1,2]}))
        
        # Empty lists return None.
        TESTS.AssertEqual(STRUCT({'a':[]}).Pop('a'), None)
        

    @classmethod
    def TestStructs(cls):
        TESTS.AssertJson(STRUCT([1,2]).Structs(), [STRUCT(1),STRUCT(2)])
        TESTS.AssertJson(STRUCT(None).Structs(), [])
        TESTS.AssertJson(STRUCT({'a':[1,2]}).Structs('a'), [STRUCT(1),STRUCT(2)])
        TESTS.AssertJson(STRUCT({}).Structs('a'), [])
        TESTS.AssertJson(STRUCT({'a':None}).Structs('a'), [])
        TESTS.AssertJson(STRUCT({'a':[]}).Structs('a'), [])


    @classmethod
    def TestRequireStructs(cls):
        
        expected= [STRUCT(1), STRUCT(2)]
        TESTS.AssertEqual(UTILS.ToJson(expected), '[1, 2]')
        given= STRUCT([1,2]).RequireStructs()
        TESTS.AssertEqual(UTILS.ToJson(given), '[1, 2]')
        TESTS.AssertEqual(len(given), 2)
        TESTS.AssertClass(given, list)
        TESTS.AssertEqual(UTILS.ToJson(given), UTILS.ToJson(expected))
            
        expected= [STRUCT(1), STRUCT(2)]
        TESTS.AssertEqual(UTILS.ToJson(expected), '[1, 2]')
        given= STRUCT({'a':[1,2]}).RequireStructs('a')
        TESTS.AssertEqual(UTILS.ToJson(given), '[1, 2]')
        TESTS.AssertEqual(len(given), 2)
        TESTS.AssertClass(given, list)
        TESTS.AssertEqual(UTILS.ToJson(given), UTILS.ToJson(expected))

        TESTS.AssertEqual(
            given= STRUCT({'a':[]}).Structs('a'),
            expect= []
        )

        with TESTS.AssertValidation():
            STRUCT(None).RequireStructs()
            
        with TESTS.AssertValidation():
            STRUCT({}).RequireStructs('a')

        with TESTS.AssertValidation():
            STRUCT({'a':None}).RequireStructs('a')

        with TESTS.AssertValidation():
            STRUCT({'a':{}}).RequireStructs('a')
        

    @classmethod
    def TestCopy(cls):

        a = STRUCT({'x':1})
        b = a.Copy().SetAtt('x', 2)
        TESTS.AssertEquals([
            [ a, STRUCT({'x':1}) ],
            [ b, STRUCT({'x':2}) ]
        ])

        c = a
        c.SetAtt('x', 3)
        TESTS.AssertEquals([
            [ a, STRUCT({'x':3}) ],
            [ c, STRUCT({'x':3}) ]
        ])
        

    @classmethod
    def TestMerge(cls):
        TESTS.AssertEquals([
            [ STRUCT({'a':1}).Merge({'b':2}), STRUCT({'a':1,'b':2}) ],
            [ STRUCT({'a':1}).Merge(STRUCT({'b':2})), STRUCT({'a':1,'b':2}) ],
            [ STRUCT({'a':1}).Merge({'b':2, 'a':3}), STRUCT({'a':3, 'b':2}) ] 
        ])
        

    @classmethod
    def TestIsMissingOrEmpty(cls):

        TESTS.AssertTrue(STRUCT({}).IsMissingOrEmpty())
        TESTS.AssertTrue(STRUCT(None).IsMissingOrEmpty())
        TESTS.AssertTrue(STRUCT({'a':None}).IsMissingOrEmpty('a'))

        s = STRUCT({'a':{}})
        TESTS.AssertTrue(s.IsMissingOrEmpty('a'))

        TESTS.AssertTrue(STRUCT({'a':''}).IsMissingOrEmpty('a'))
        TESTS.AssertTrue(STRUCT({'a':'  '}).IsMissingOrEmpty('a'))
        
        TESTS.AssertFalse([
            STRUCT({False}).IsMissingOrEmpty(),
            STRUCT({'a':None}).IsMissingOrEmpty(),
            STRUCT({'a':False}).IsMissingOrEmpty('a'),
            STRUCT({'a':1}).IsMissingOrEmpty('a'),
            STRUCT({'a':'y'}).IsMissingOrEmpty('a'),
            STRUCT({'a':{'b':2}}).IsMissingOrEmpty('a')
        ])
        

    @classmethod
    def TestDefault(cls):
        TESTS.AssertEqual(STRUCT({'a':1}).Default('a',2).Obj(), {'a':1})
        TESTS.AssertEqual(STRUCT({'a':1}).Default('b',2).Obj(), {'a':1,'b':2})
        #TESTS.AssertEqual(STRUCT({'a':{'b':2}}).Default('a.c',3).Obj(), {'a':{'b':2,'c':3}})
        #* s=${}.Default(a.c,3); s.Obj() -> Untested behaviour!

        TESTS.AssertEqual(STRUCT({'A':''}).GetAtt('A', default=1), '')
        TESTS.AssertEqual(STRUCT({}).GetAtt('A', default=1), 1)

        #OLD: TESTS.AssertEqual(STRUCT({'A':None}).Att('A', default=1), None)
        TESTS.AssertEqual(STRUCT({'A':None}).GetAtt('A', default=1), 1)
        

    @classmethod
    def TestDefaultTimestamp(cls):
        
        TESTS.AssertFalse(STRUCT({}).DefaultTimestamp('a').IsMissingOrEmpty('a'))
        
        TESTS.AssertNotEqual(
            given= STRUCT({'a':None}).DefaultTimestamp('a').GetAtt('a'), 
            expect= None)

        TESTS.AssertEqual(
            given= STRUCT({'a':'2023-04-01T05:00:30.001000Z'}).DefaultTimestamp('a').GetAtt('a'), 
            expect= '2023-04-01T05:00:30.001000Z')
        

    @classmethod
    def TestDefaultGuid(cls):
        TESTS.AssertFalse(STRUCT({}).DefaultGuid('a').IsMissingOrEmpty('a'))
        TESTS.AssertEqual(STRUCT({'a':1}).DefaultGuid('a').GetAtt('a'), 1)
        TESTS.AssertNotEqual(STRUCT({'a':None}).DefaultGuid('a').GetAtt('a'), None)
        TESTS.AssertNotEqual(STRUCT({'a':{}}).DefaultGuid('a').GetAtt('a'), {})
        TESTS.AssertEqual(STRUCT({}).GetAtt('a'), None)
        TESTS.AssertNotEqual(STRUCT({}).DefaultGuid('a').GetAtt('a'), None)
    

    @classmethod
    def TestRemoveAtt(cls):

        TESTS.AssertEqual(
            given= STRUCT({'a':1, 'b':2}).RemoveAtt('a'),
            expect= STRUCT({'b':2})
        )

        # With child path.
        TESTS.AssertEqual(
            given= STRUCT({'a':{'x':1, 'y':3}, 'b':2}).RemoveAtt('a.x'),
            expect= STRUCT({'a':{'y':3}, 'b':2})
        )

        # Missing attribute.
        with TESTS.AssertValidation():
            STRUCT({}).RemoveAtt('a')
        

    @classmethod
    def TestCanonicalize(cls):
        TESTS.AssertEqual(
            given= STRUCT({ 'a': 1, 'b': 2 }).Canonicalize(),
            expect= '{"a":1,"b":2}'
        )
        
    
    @classmethod
    def TestToJson(cls):     
        TESTS.AssertEqual(
            given= STRUCT({ 'a': 1, 'b': 2 }).ToJson(),
            expect= '{"a": 1, "b": 2}'
        )
        
    
    @classmethod
    def TestToYaml(cls):
        obj = {'products':['item 1', 'item 2']}
        yaml = "products:\n  - item 1\n  - item 2"
        TESTS.AssertEqual(
            given= STRUCT(obj).ToYaml(), 
            expect= yaml)

        obj = {'A':1, 'B':2}
        yaml = "A: 1\nB: 2"
        TESTS.AssertEqual(
            given= STRUCT(obj).ToYaml(), 
            expect= yaml)

        obj = {'A':1, 'B':{'C':3,'D':4}}
        yaml = "A: 1\nB:\n  C: 3\n  D: 4"
        TESTS.AssertEqual(
            given= STRUCT(obj).ToYaml(), 
            expect= yaml)
        
        # Accept None in indent.
        STRUCT({}).ToYaml(indent=None) 
       

    @classmethod
    def TestAny(cls):
        
        TESTS.AssertTrue(STRUCT([1,{}]).Any())
        TESTS.AssertTrue(STRUCT([{'x':1},{'x':2}]).Any('x', equals=2))
        TESTS.AssertTrue(STRUCT([{'x':1},{'x':2}]).Any({'x':1}))

        TESTS.AssertFalse([
            STRUCT([]).Any(),
            STRUCT([]).Any('y', equals=1),
            STRUCT([{'x':1},{'x':2}]).Any('x', equals=3),
            STRUCT([{'x':1},{'x':2}]).Any('y', equals=1),
            STRUCT([{'x':1},{'x':2}]).Any({'x':3}),
            STRUCT([{'x':1},{'x':2}]).Any({'y':1})
        ])
                
        #* ${}.Any() -> Untested behaviour!
        #* ${}.Any(x, equals=y) -> Untested behaviour!
        

    @classmethod
    def TestAppend(cls):

        TESTS.AssertEquals([
            [ STRUCT(None).Append(1), STRUCT([1]) ],
            [ STRUCT([]).Append(1), STRUCT([1]) ],
            [ STRUCT([1]).Append(1), STRUCT([1,1]) ]
        ])
        
        with TESTS.AssertValidation():
            STRUCT({}).Append(1)
        

    @classmethod
    def TestAppendToAtt(cls):

        TESTS.AssertEquals([
            [ STRUCT({}).AppendToAtt('a', [1]), STRUCT({'a':[1]}) ],
            [ STRUCT({'a':[]}).AppendToAtt('a', [2]), STRUCT({'a':[2]}) ],
            [ STRUCT({'a':[]}).AppendToAtt('a', 2), STRUCT({'a':[2]}) ],
            [ STRUCT({'a':[]}).AppendToAtt('a', [{'x':1}]), STRUCT({'a':[{'x':1}]}) ],
            [ STRUCT({'a':[1]}).AppendToAtt('a', [2]), STRUCT({'a':[1,2]}) ],
            [ STRUCT({'a':[1,2]}).AppendToAtt('a', [2]), STRUCT({'a':[1,2]}) ],
            [ STRUCT({'a':[1,2]}).AppendToAtt('a', [2,3,4]), STRUCT({'a':[1,2,3,4]}) ]
        ])
        

    @classmethod
    def TestLast(cls):

        TESTS.AssertEquals([
            [ STRUCT([1,2,3]).Last(), 3 ],
            [ STRUCT([1]).Last(), 1 ]
        ])

        with TESTS.AssertValidation():
            STRUCT([]).Last()

        with TESTS.AssertValidation():
            STRUCT({}).Last()

        with TESTS.AssertValidation():
            STRUCT({}).Last()
        

    @classmethod
    def TestLoadYamlFile(cls):
        pass
        
    
    @classmethod
    def TestAttributes(cls):
        TESTS.AssertEqual(
            given= STRUCT({'a':1, 'b':2}).Attributes(),
            expect= ['a','b']
        )
        

    @classmethod
    def TestContainsAtt(cls):

        TESTS.AssertTrue(STRUCT({'a':1}).ContainsAtt('a'))
        TESTS.AssertFalse(STRUCT({'a':1}).ContainsAtt('b'))
        TESTS.AssertFalse(STRUCT({}).ContainsAtt('b'))
        TESTS.AssertFalse(STRUCT({}).ContainsAtt('a.b'))
        

    @classmethod
    def TestFromStructs(cls):
        s = [STRUCT(10),STRUCT(20)]
        t = TestCastStructsClass.FromStructs(s)

        TESTS.AssertEqual(len(t), 2)
        TESTS.AssertClass(t[0], TestCastStructsClass)
        TESTS.AssertClass(t[1], TestCastStructsClass)
        TESTS.AssertEqual(t[0], STRUCT(10))
        TESTS.AssertEqual(t[1], STRUCT(20))
    

    @classmethod
    def TestMoveAtt(cls):
        
        # ${A:1,B:2}.MoveAtt(B,0) -> {B:2,A1}
        TESTS.AssertEqual( STRUCT({'A':1, 'B':2}).MoveAtt('B', 0).Obj(), {'B':2, 'A':1} )

        s = STRUCT({'A':1, 'B':2})
        s.MoveAtt('B', 0)
        TESTS.AssertEqual(s.Obj(), {'B':2, 'A':1})


    @classmethod
    def Test__getitem__(cls):
        s = STRUCT({'A':1, 'C':3, 'D':4})
        
        TESTS.AssertTrue('A' in s)
        TESTS.AssertTrue('B' not in s)

        TESTS.AssertEqual(s.GetAtt('C'), 3)
        TESTS.AssertEqual(s.__getitem__('C'), 3)
        TESTS.AssertEqual(s['C'], 3)

        # __getitem__ ignores the hierarchy, unlike Att.
        s = STRUCT({'A.B':1, 'A':{'B':2}})
        TESTS.AssertEqual(s['A.B'], 1)
        TESTS.AssertEqual(s.GetAtt('A.B', noHierarchy=False), 2)

        # Requires the key to exist.
        with TESTS.AssertValidation():
            s['B']
        

    @classmethod
    def TestRaw(cls):

        # Raw() returns the converted clean dictionary.
        TESTS.AssertEqual(
            STRUCT({'A':STRUCT(1)}).Raw(), 
            {'A':1})
        
        # Obj() returns the structure, not a converted dictionary.
        UTILS.AssertIsType(
            STRUCT({'A':STRUCT(1)}).Obj()['A'],
            STRUCT)
    
        # Raw() returns the converted clean dictionary, not the original STRUCT.
        UTILS.AssertIsType(
            STRUCT({'A':STRUCT(1)}).Raw()['A'],
            int)
            

    @classmethod
    def TestMatchClass(cls):

        s0 = None
        s1 = STRUCT_TESTS_CHILD(1)
        s2 = STRUCT(1) 
        
        STRUCT().AssertClass(s0)
        STRUCT().AssertClass(s1)
        STRUCT().AssertClass(s2)

        STRUCT_TESTS_CHILD().AssertClass(s0)
        STRUCT_TESTS_CHILD().AssertClass(s1)
        with TESTS.AssertValidation('STRUCT not a CHILD?'):
            STRUCT_TESTS_CHILD().AssertClass(s2)


    @classmethod
    def TestRequireInt(cls):
        STRUCT({'A':1}).RequireInt('A')

        with TESTS.AssertValidation('Not float'):
            STRUCT({'A':1.23}).RequireInt('A')
        with TESTS.AssertValidation('Not str(int)'):
            STRUCT({'A':'1'}).RequireInt('A')
        with TESTS.AssertValidation('Not str'):
            STRUCT({'A':'z'}).RequireInt('A')
        with TESTS.AssertValidation('Not dict'):
            STRUCT({'A':{}}).RequireInt('A')
        with TESTS.AssertValidation('Not array'):
            STRUCT({'A':[]}).RequireInt('A')
        with TESTS.AssertValidation('Not bool'):
            STRUCT({'A':True}).RequireInt('A')


    @classmethod
    def TestRequireFloat(cls):
        STRUCT({'A':1.23}).RequireFloat('A')

        with TESTS.AssertValidation('Not int'):
            STRUCT({'A':1}).RequireFloat('A')
        with TESTS.AssertValidation('Not str(int)'):
            STRUCT({'A':'1'}).RequireInt('A')
        with TESTS.AssertValidation('Not str'):
            STRUCT({'A':'z'}).RequireInt('A')
        with TESTS.AssertValidation('Not dict'):
            STRUCT({'A':{}}).RequireInt('A')
        with TESTS.AssertValidation('Not array'):
            STRUCT({'A':[]}).RequireInt('A')
        with TESTS.AssertValidation('Not bool'):
            STRUCT({'A':True}).RequireInt('A')


    @classmethod
    def TestIterate(cls):
        '''Iterate over the keys of a STRUCT.'''
        lst = []
        for key in STRUCT({'A':1, 'B':2}):
            lst.append(key)
        TESTS.AssertEqual(lst, ['A', 'B'])


    @classmethod
    def TestParse(cls):

        # Test with a class that implements STRUCT.
        class CLASS(STRUCT):
            pass
        parsed = CLASS.Parse(1)
        TESTS.AssertEqual(parsed.Obj(), 1)
        CLASS.AssertClass(parsed)

        # Test a struct inside a struct.
        parsed = CLASS.Parse(STRUCT(1))
        TESTS.AssertEqual(parsed.Obj(), 1)
        CLASS.AssertClass(parsed)



    @classmethod
    def TestParseList(cls):
        class CLASS(STRUCT):
            pass
        lst = [1,2,3]
        parsed = CLASS.ParseList(lst)
        UTILS.AssertIsList(parsed, itemType=CLASS, require=True)


    @classmethod
    def TestKeys(cls):  
        TESTS.AssertEqual(STRUCT({'A':1, 'B':2}).Keys(), ['A', 'B'])
        TESTS.AssertEqual(STRUCT({}).Keys(), [])
        TESTS.AssertEqual(STRUCT(None).Keys(), [])
        TESTS.AssertEqual(STRUCT(1).Keys(), [])
        TESTS.AssertEqual(STRUCT('x').Keys(), [])
        TESTS.AssertEqual(STRUCT([]).Keys(), [])


    @classmethod
    def TestLength(cls):
        LOG.Print(type(STRUCT('asd').Obj()).__name__)
        TESTS.AssertEqual(STRUCT('asd').Length(), 3)
        TESTS.AssertEqual(STRUCT(134).Length(), 0)
        TESTS.AssertEqual(STRUCT([1,1,1]).Length(), 3)
        TESTS.AssertEqual(STRUCT([]).Length(), 0)
        TESTS.AssertEqual(STRUCT(None).Length(), 0)
        TESTS.AssertEqual(STRUCT({'a':1}).Length(), 1)
        TESTS.AssertEqual(STRUCT({'a':None}).Length(), 1)
        TESTS.AssertEqual(STRUCT({'a':{}}).Length(), 1)
        TESTS.AssertEqual(STRUCT({'a':[]}).Length(), 1)
        TESTS.AssertEqual(STRUCT({'a':[1,2]}).Length(), 1)
        TESTS.AssertEqual(STRUCT({'a':[1,2,3]}).Length(), 1)



    @classmethod
    def TestAssertOnlyKeys(cls):
        STRUCT({}).AssertOnlyKeys([])
        STRUCT({'a':1,'b':2}).AssertOnlyKeys(['a','b'])
        
        with TESTS.AssertValidation():
            STRUCT({'a':1,'b':2}).AssertOnlyKeys(['a'])

        with TESTS.AssertValidation():
            STRUCT({'a':1,'b':2}).AssertOnlyKeys(['a', 'c'])


    @classmethod
    def TestAllStruct(cls):
        LOG.Print('STRUCT_TESTS.TestAllStruct() ==============================')
        
        cls.TestInit()
        cls.TestMapAtt()
        cls.TestUnstruct()
        cls.TestObj()
        cls.TestStr()
        cls.TestEquals()
        cls.TestSetAttRoot()
        cls.TestSetAtt()
        cls.TestAtt()
        cls.TestRequireBool()
        cls.TestRequireStr()
        cls.TestRequireTimestamp()
        cls.TestRequire()
        cls.TestMatch()
        cls.TestStruct()
        cls.TestRequireStruct()
        cls.TestListStr()
        cls.TestGetList()
        cls.TestSize()
        cls.TestRemoveFirst()
        cls.TestFirst()
        cls.TestWhere()
        cls.TestPop()
        cls.TestRequireStructs()
        cls.TestStructs()
        cls.TestCopy()
        cls.TestMerge()
        cls.TestIsMissingOrEmpty()
        cls.TestDefault()
        cls.TestDefaultTimestamp()
        cls.TestDefaultGuid()
        cls.TestRemoveAtt()
        cls.TestCanonicalize()
        cls.TestToJson()
        cls.TestToYaml()
        cls.TestAny()
        cls.TestAppend()
        cls.TestAppendToAtt()
        cls.TestLast()
        cls.TestLoadYamlFile()
        cls.TestAttributes()
        cls.TestContainsAtt()
        cls.TestFromStructs()
        cls.TestMoveAtt()        
        cls.Test__getitem__()
        cls.TestRaw()
        cls.TestMatchClass()
        cls.TestRequireInt()
        cls.TestRequireFloat()
        cls.TestIterate()
        cls.TestParse()
        cls.TestParseList()
        cls.TestKeys()
        cls.TestLength()
        cls.TestRequireDict()
        cls.TestGetDict()
        cls.TestAssertOnlyKeys()


class STRUCT_TESTS_CHILD(STRUCT):
    pass