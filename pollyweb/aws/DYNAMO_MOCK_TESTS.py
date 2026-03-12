from ITEM import ITEM
from PW_UTILS.STRUCT import STRUCT
from PW_UTILS.TESTS import TESTS
from DYNAMO_MOCK import DYNAMO_MOCK
from LOG import LOG


class DYNAMO_MOCK_TESTS(DYNAMO_MOCK):


    @classmethod
    def _GetTable(cls, keys:list[str]=None, items:list[dict[str,any]]=[]) -> DYNAMO_MOCK:
        '''👉 Resets the mockup and returns a mocked table.'''

        ##LOG.Print(f'\nDYNAMO.MOCK.TEST._GetTable(keys={keys}, items={items})')

        DYNAMO_MOCK.ResetMock()

        DYNAMO_MOCK.MockTable(
            domain= 't.com', 
            table= 'T', 
            items= items
        )

        DYNAMO_MOCK.SetMockDomain('t.com')

        ret = DYNAMO_MOCK(alias='T', keys= keys)
        ##LOG.Print()
        return ret


    @classmethod
    def TestTable(cls):

        # Happy Path
        t = cls._GetTable()
        t.Table()

        # missing alias.
        t = cls._GetTable()
        t._alias = ''
        with TESTS.AssertValidation():
            t.Table() 

        # missing domain.
        DYNAMO_MOCK.ResetMock()
        t = cls._GetTable()
        DYNAMO_MOCK._activeDomain = ''
        with TESTS.AssertValidation():
            t.Table() 

        # domains are mocked by default.
        DYNAMO_MOCK.ResetMock()
        t = cls._GetTable()
        DYNAMO_MOCK._domains = {}
        t.Table() 
            
        # all items must have an ID.
        DYNAMO_MOCK.ResetMock()
        DYNAMO_MOCK.MockTable(domain='t', table='T', items=[{'ID':3}])
        with TESTS.AssertValidation():
            DYNAMO_MOCK.MockTable(domain='t', table='T', items=[{'ID2':4}])


    @classmethod
    def TestCalculateID(cls):

        TESTS.AssertEqual(cls._GetTable(keys=None)._calculateID({'ID':1}), '1')
        TESTS.AssertEqual(cls._GetTable(keys=['A'])._calculateID({'A':1}), '1')
        TESTS.AssertEqual(cls._GetTable(keys=['C','A'])._calculateID({'A':1,'B':2,'C':3}), '3/1')
        TESTS.AssertEqual(cls._GetTable(keys=['A','B','C'])._calculateID({'A':1,'B':2,'C':3}), '1/2/3')
        
        with TESTS.AssertValidation():
            cls._GetTable(keys=None)._calculateID({'A':1})

        with TESTS.AssertValidation():
            cls._GetTable(keys=['C','A'])._calculateID({'A':1})
        

    @classmethod
    def TestGetItem(cls):
        
        t = cls._GetTable(keys=['A','B'], items=[{'ID':'1/2', 'A':1, 'B':2, 'C':3}])
        TESTS.AssertEqual(t.GetItem({'A':1,'B':2}).RequireID(), '1/2')
        TESTS.AssertEqual(t.GetItem('1/2').RequireID(), '1/2')
        TESTS.AssertTrue(t.GetItem(1).IsMissingOrEmpty())

        t = cls._GetTable(keys=None, items=[{'ID':1}])
        TESTS.AssertEqual(t.GetItem(1).RequireID(), 1)
        TESTS.AssertTrue(t.GetItem(2).IsMissingOrEmpty())

        t = cls._GetTable(keys=None, items=[{'ID':'a'}])
        TESTS.AssertEqual(t.GetItem('a').RequireID(), 'a')
        TESTS.AssertTrue(t.GetItem('b').IsMissingOrEmpty())
        

    @classmethod
    def TestRequire(cls):

        t = cls._GetTable(keys=['A','B'], items=[{'ID':'1/2', 'A':1, 'B':2, 'C':3}])
        TESTS.AssertEqual(t.Require({'A':1,'B':2}).RequireID(), '1/2')
        TESTS.AssertEqual(t.Require('1/2').RequireID(), '1/2')
        with TESTS.AssertValidation():
            t.Require(1)

        t = cls._GetTable(keys=None, items=[{'ID':1}])
        TESTS.AssertEqual(t.Require(1).RequireID(), 1)
        with TESTS.AssertValidation():
            t.Require(2)

        t = cls._GetTable(keys=None, items=[{'ID':'a'}])
        TESTS.AssertEqual(t.Require('a').RequireID(), 'a')
        with TESTS.AssertValidation():
            t.Require('b')
    

    @classmethod
    def TestQuery(cls):
        t = cls._GetTable(items=[{'ID':1,'A':'x'}, {'ID':2,'A':'y'}, {'ID':3,'A':'x'}])

        items = t.Query('A', equals='x')
        TESTS.AssertEqual(len(items), 2)
        TESTS.AssertEqual(items[0].RequireID(), 1)
        TESTS.AssertEqual(items[1].RequireID(), 3)
        TESTS.AssertEqual(items[1].RequireStr('A'), 'x')

        items = t.Query('A', equals='z')
        TESTS.AssertEqual(len(items), 0)

        items = t.Query('B', equals='z')
        TESTS.AssertEqual(len(items), 0)


    @classmethod
    def TestInsert(cls):

        TESTS.AssertEqual(cls._GetTable(keys=['A','B']).Insert({'A':1, 'B':2}).RequireID(), '1/2')
        TESTS.AssertEqual(cls._GetTable(keys=None).Insert({'ID':0, 'A':1}).RequireID(), 0)
        TESTS.AssertEqual(cls._GetTable().Insert(STRUCT({'ID':0})).RequireID(), 0)
        TESTS.AssertEqual(cls._GetTable().Insert({'ID':0}).RequireID(), 0)
        
        # Require all attribute keys on insert.
        with TESTS.AssertValidation():
            cls._GetTable(keys=['A','C']).Insert({'ID':0, 'A':1}).RequireID()

        # Disallow duplicates on insert.
        t = cls._GetTable()
        t.Insert({'ID':0})
        with TESTS.AssertValidation():
            t.Insert({'ID':0})
        
       
    @classmethod    
    def TestUpdate(cls):
        
        # Happy path 1
        t = cls._GetTable(items=[{'ID':1,'A':1,'B':'x'}])
        t.Update({'ID':1, 'A':2})
        i = t.GetItem(1)
        TESTS.AssertEqual(i.RequireAtt('A'), 2)
        TESTS.AssertEqual(i.RequireAtt('B'), 'x')

        # Happy path 2
        i = cls._GetTable(items=[{'ID':1,'A':1,'B':'x'}]).GetItem(1)
        i.SetAtt('A',3)
        i.UpdateItem()
        TESTS.AssertEqual(i.RequireAtt('A'), 3)
        TESTS.AssertEqual(i.RequireAtt('B'), 'x')

        # Missing ID Exception!
        with TESTS.AssertValidation():
            cls._GetTable(items=[]).Update({'ID':4,'A':4})

        # Concurrency Exception!
        t = cls._GetTable(items=[{'ID':1,'A':1,'ItemVersion':'x'}])
        i = t.GetItem(1)
        
        t.Update({'ID':1, 'A':2})
        TESTS.AssertEqual(t.GetItem(1).RequireAtt('A'), 2)

        i.SetAtt('A',3)
        with TESTS.AssertValidation():
            i.UpdateItem()
    
        
    @classmethod
    def TestUpsert(cls):
        t = cls._GetTable(items=[])

        t.Upsert({'ID':1,'A':1})
        TESTS.AssertEqual(t.GetItem(1).RequireAtt('A'), 1)

        t.Upsert({'ID':1,'A':2})
        TESTS.AssertEqual(t.GetItem(1).RequireAtt('A'), 2)
        

    @classmethod
    def TestDelete(cls):
        t = cls._GetTable(
            keys=['A','B'],
            items=[
                {'ID':'1/2','A':1,'B':2},
                {'ID':'3/4','A':3,'B':4},
            ])
        
        i = t.Require('1/2')
        i.Delete()
        with TESTS.AssertValidation():
            t.Require('1/2')

        i = t.Require({'A':3,'B':4})
        i.Delete()
        with TESTS.AssertValidation():
            t.Require({'A':3,'B':4})
        
    
    @classmethod
    def TestGetAll(cls):
        '''❗NOTE: this assumes that only 10 records are returned per page.
        * That's true for the Mock, but for AWS.
        * In AWS, DynamoDB returns a variable number of items, up to 1MB.
        '''
        
        max = 25
        lst = cls._GetTable(items= [
            {'ID':n,'A':n}
            for n in range(max)
        ]).GetAll()

        TESTS.AssertEqual(len(lst), max)
        TESTS.AssertClass(lst[0], ITEM)
        TESTS.AssertEqual(lst[0], {'ID':0,'A':0})
        TESTS.AssertEqual(lst[0].RequireID(), 0)
        TESTS.AssertEqual(lst[max-1].RequireAtt('A'), max-1)
        

    @classmethod
    def TestTTL(cls):
        TESTS.AssertNotEqual(cls.TTL(days=1), None)

        with TESTS.AssertValidation():
            cls.TTL(days=0)

        with TESTS.AssertValidation():
            cls.TTL(days=-1)
    
        with TESTS.AssertValidation():
            cls.TTL(days=1000)

        with TESTS.AssertValidation():
            cls.TTL(days=None)
    

    @classmethod
    def TestGetPageFromTimestamp(cls):
        '''❗NOTE: this assumes that only 10 records are returned per page.
        * That's true for the Mock, but for AWS.
        * In AWS, DynamoDB returns a variable number of items, up to 1MB
        '''
        
        fromTimestamp= '003'
        t = cls._GetTable(items= [
            {'ID':n,'A':n,'Timestamp':str(n).rjust(3, '0')}
            for n in range(20)
        ])
        
        # First page.
        page = t.GetPageFromTimestamp(
            timestamp= fromTimestamp,
            exclusiveStartKey= None)
        
        page = STRUCT(page)
        items = page.Structs('Items')
        TESTS.AssertEqual(len(items), 10)
        TESTS.AssertEqual(items[0].GetAtt('A'), 3)
        lastEvaluatedKey = page.RequireAtt('LastEvaluatedKey')

        # Second page.
        page = t.GetPageFromTimestamp(
            timestamp= fromTimestamp,
            exclusiveStartKey= lastEvaluatedKey
        )
        page = STRUCT(page)
        TESTS.AssertEqual(len(page.Structs('Items')), 7)
        TESTS.AssertEqual(page.GetAtt('LastEvaluatedKey'), None)


    @classmethod
    def TestParseStream(cls):

        event = {
            'Records': [
                {
                    'dynamodb': {
                        'NewImage': {
                            'ID': {
                                'S': n
                            }
                        }
                    }
                }
                for n in range(10)
            ]
        }

        lst = DYNAMO_MOCK.ParseStream(event)

        TESTS.AssertEqual(len(lst), 10)
        TESTS.AssertClass(lst[0], STRUCT)
        TESTS.AssertEqual(lst[0], {'ID':0})
        TESTS.AssertEqual(lst[0].GetAtt('ID'), 0)
        TESTS.AssertEqual(lst[9].GetAtt('ID'), 9)


    @classmethod
    def TestAllDynamo(cls):
        LOG.Print('MOCK_DYNAMO_TESTS.TestAllDynamo() ==============================')
        
        cls.TestTable()
        cls.TestCalculateID()
        cls.TestGetItem()
        cls.TestRequire()
        cls.TestQuery()
        cls.TestInsert()
        cls.TestUpdate()
        cls.TestUpsert()
        cls.TestDelete()
        cls.TestGetAll()
        cls.TestTTL()
        cls.TestGetPageFromTimestamp()
        cls.TestParseStream()