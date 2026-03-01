# 📚 DYNAMO

from __future__ import annotations
from typing import Union

from boto3.dynamodb.conditions import Attr,Key,ConditionBase
from botocore.exceptions import ClientError

from time import time

from DYNAMO_BASE_TABLE import DYNAMO_BASE_TABLE
from ITEM import ITEM, ITEM_TABLE
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS
from pollyweb.utils.LOG import LOG


class DYNAMO_BASE(ITEM_TABLE):
    ''' 👉 DynamoDB table manager. '''


    def Table(self) -> DYNAMO_BASE_TABLE:
        '''👉 Returns the underlying table.'''
        LOG.RaiseException('Please override!')


    def __init__(self, alias:str=None, keys:list[str]=None):
        self._alias = alias
        self._keys:list[str] = keys


    def _calculateID(self, struct:Union[STRUCT, dict[str,any]]) -> str:
        ''' 👉 Returns the ID from a set of table keys
        * If keys is [C,A]: ${A:x, B:y, C:z} -> 'z/x' 
        * If keys is None: ${ID:x} -> x
        * If keys is None: ${A:x, B:y, C:z} -> Exception, ID missing!
        '''

        UTILS.Require(struct)
        UTILS.AssertIsAnyType(struct, [STRUCT,dict])

        if type(struct) != STRUCT:
            struct = STRUCT(struct)
            
        if not self._keys or self._keys == []:
            ret = struct.RequireAtt('ID')
            if type(ret) not in [int, str]:
                return str(ret)
            return ret
        
        vals = []
        for key in self._keys:
            val = str(struct.RequireAtt(key))
            vals.append(val)
        return '/'.join(vals)


    def Require(self, key:Union[str,int,STRUCT,dict[str,str]]) -> ITEM:
        ''' 👉 Gets a required item with ID=key, 
        or where the compositive key can be derived from the atributes of the given object.
        
        * For table.keys=[A,C]: Get({A:x, B:y, C:z}) -> Get(ID='x/z')
        * For table.keys=None: Get(123) -> Get(ID=123)
        * For table.keys=None: Get('abc') -> Get(ID='abc')
        '''
        ##LOG.Print(f'🪣 DYNAMO.Require(key={key})')

        UTILS.RequireArgs([key])
        UTILS.AssertIsAnyType(key, [str,int,STRUCT,dict])

        return self.GetItem(
            key= key, 
            require= True)


    def HasItem(self, key:Union[str,int,STRUCT,dict[str,str]], require:bool=False) -> bool:
        return not self.GetItem(key).IsMissingOrEmpty()


    def GetItem(self, key:Union[str,int,STRUCT,dict[str,str]], require:bool=False) -> ITEM:
        ''' 👉 Gets the item with ID=key, 
        or where the compositive key can be derived from the atributes of the given object.

        * For table.keys=[A,C]: Get({A:x, B:y, C:z}) -> Get(ID='x/z')
        * For table.keys=None: Get(123) -> Get(ID=123)
        * For table.keys=None: Get('abc') -> Get(ID='abc')
        '''
        ##LOG.Print(f'🪣 DYNAMO.GetItem(key={key}, require={require})')

        UTILS.Require(key)
        UTILS.AssertIsAnyType(key, [str,int,STRUCT,dict])

        if not key:
            LOG.RaiseValidationException(f'Is there a reason for the key to be empty?')
            ret = ITEM(None)

            if require == True:
                ret.Require()

            return ret
        
        id = None

        # If str or int...
        if isinstance(key, str) or isinstance(key, int):
            id = key

        # If struct...
        elif isinstance(key, STRUCT):
            id = self._calculateID(key)

        # If object...
        elif isinstance(key, dict):
            struct = STRUCT(key)
            id = self._calculateID(struct)

        else:
            LOG.RaiseException(f'Unexpected key! Type={type(key).__name__}, value=({key}).')

        ##LOG.Print(f'🪣 DYNAMO.GetItem().id = {id}')
        response = self.Table().get_item(
            Key= { 'ID': id }
        )
        ##print(f'DYNAMO.BASE.GetItem().{response=}')
        
        if 'Item' not in response:
            if require == True:
                
                from NLWEB import NLWEB
                domain = NLWEB.CONFIG().RequireDomain()

                '''
                toPrint = [
                    s.RequireID()
                    for s in self.GetAll()
                ]
                LOG.Print(f'  DYNAMO_BASE.{domain=}, {toPrint=}')
                '''
                
                LOG.RaiseValidationException(
                    f'No item found on table=({self._alias})'\
                    f' with ID=({id}) in domain=({domain})!'
                )
            else:
                return ITEM(None)

        item = response['Item']
        ##print(f'DYNAMO.GetItem().{item=}')
       
        ret = ITEM(
            item= item, 
            table= self
        )
        
        if require == True:
            ret.Require()

        return ret
    

    def Query(self, att:str, equals:Union[str,int,bool]) -> list[ITEM]:
        '''👉 Queries a global secondary index (GSI).'''

        UTILS.RequireArgs([att,equals])
        UTILS.AssertIsType(att, str)
        UTILS.AssertIsAnyType(equals, [str,int,bool])

        # https://aws.amazon.com/getting-started/hands-on/create-manage-nonrelational-database-dynamodb/module-3/
        resp = self.Table().query(
            IndexName= att+"Index",
            KeyConditionExpression= Key(att).eq(equals)
        )
        
        # Return the items as a list[ITEM].
        return [ITEM(item) 
            for item in resp['Items']]
            

    def _Save(self, item:Union[dict[str,any],STRUCT,ITEM], method:str, days:int=None) -> ITEM:  
        '''👉 Saves an item on the internal table. 

        Params:
        * `item`: object or STRUCT
        * `method`: one of ['UPDATE', 'INSERT', 'INSERT,UPDATE']
        * `days`: optional number of days for TTL (time to live).

        Usage:
        * ._save(item={a:1,b:2}, method=INSERT, days=1)
        * ._save(item=${ID:'1/2',a:1,b:2}, method=UPDATE)
        '''

        UTILS.RequireArgs([item, method])
        UTILS.AssertIsAnyType(item, [STRUCT,dict,ITEM])


        # Wrap the item with a struct
        struct = STRUCT(item)
        struct.RemoveAtt('🤝', safe=True)

        # Set the ID, if not set.
        struct.Default(
            name= 'ID', 
            default= self._calculateID(struct))
        LOG.Print(f'@', struct)

        # Set the TTL, if days were given.
        if days != None:
            struct.Default(
                name= 'TTL',
                default= self.TTL(days=days))
        
        ''' 👉 https://www.tecracer.com/blog/2021/07/implementing-optimistic-locking-in-dynamodb-with-python.html '''
        ''' 👉 https://boto3.amazonaws.com/v1/documentation/api/latest/_modules/boto3/dynamodb/conditions.html '''
        
        ''' Require a VersionID - this won't work for manually added items.
        ##print(f'>>>>>type:{type(item)}')
        if isinstance(item, ITEM):
            ##print(f'>>>>>{item.HasTable()=}, ({item.Obj()=})')
            if item.HasTable() and not item.ContainsAtt('ItemVersion'):
                LOG.ValidationException(f'An item with a table should have an ItemVersion! Given={item.Obj()}')
        '''

        condition:ConditionBase = None
        if method == 'INSERT':
            condition = Attr('ID').not_exists()
        elif method == 'UPDATE' and struct.ContainsAtt('ItemVersion'):
            condition = Attr('ItemVersion').eq(struct.RequireStr('ItemVersion')) 
        elif method == 'UPDATE':
            condition = Attr('ID').exists()

        # optimistic concurrency
        struct.SetAtt('ItemVersion', UTILS.UUID())

        # get paragmeters
        expression, values, names = self._get_update_params(struct.Obj())

        try:
            response = self.Table().update_item(
                Key= {'ID': struct.RequireAtt('ID') },
                UpdateExpression= expression,
                ExpressionAttributeValues= dict(values),
                ExpressionAttributeNames= dict(names),
                # 👉 https://www.tecracer.com/blog/2021/07/implementing-optimistic-locking-in-dynamodb-with-python.html
                ConditionExpression= condition)

        except ClientError as err:
            if err.response["Error"]["Code"] == 'ConditionalCheckFailedException':
                # Somebody changed the item in the db while we were changing it!
                raise ValueError("Record changed concurrently, retry!") from err
            else:
                raise err

        return ITEM(
            item= struct.Obj(), 
            table= self)


    def Insert(self, 
        item:Union[dict[str,any],STRUCT], 
        days:int=None
    ) -> ITEM:
        ''' 👉 Inserts an item where the ID doesn't exist. 
        
        Params:
        * `item`: object or STRUCT
        * `days`: optional number of days for TTL (time to live).

        Usage:
        * For table.keys=[A,C]: Insert({a:x, b:y}) -> inserts ID='x/y'
        * For table.keys=[A,C]: Insert({ID:1, a:x, b:y}) -> inserts ID=1
        * For table.keys=None: Insert({ID:1, a:x, b:y}) -> inserts ID=1
        * Insert(${}) == Insert({}) # supports Structs

        Exceptions:
        * if the Key already exists on the table -> Already Exists exception!
        '''
        return self._Save(
            item= item, 
            method= 'INSERT', 
            days= days)
    

    def Update(self, item:Union[dict[str,any],STRUCT]) -> ITEM:
        ''' 👉 Updates an item where the ID must exist.
        
        Params:
        * `item`: object or STRUCT
        * `days`: optional number of days for TTL (time to live).

        Usage:
        * item=Get(key); item.Att(a,1); Update(item)

        Exceptions:
        * if updated between Get and Update -> Concurrent Exception!
        * if composed ID doesn't exist -> Missing ID Exception!
        '''

        UTILS.Require(item)
        UTILS.AssertIsAnyType(item, [STRUCT,dict])

        return self._Save(
            item= item, 
            method= 'UPDATE')
    

    def Upsert(self, item:Union[dict[str,any],STRUCT], days:int=None):
        ''' 👉 Inserts or updates an item. 
        * `WARNING`: unsafe method for concurrency, prefer Insert/Update.'''

        self._Save(
            item= item, 
            method= 'INSERT,UPDATE', 
            days=days)
        
        return self.GetItem(item)


    def Delete(self, struct:ITEM):
        ''' 👉 Deletes an item. 
        Usages:
        * item=Get(key); Delete(item)
        * item={ID:id}; Delete(item)
        * Delete({ID:id})
        '''
        if not struct or struct.IsMissingOrEmpty():
            return 
        
        id = struct.RequireID()
        response = self.Table().delete_item(Key={ 'ID': id })
        status_code = response['ResponseMetadata']['HTTPStatusCode']

        ##LOG.Print(f'🪣 DYNAMO.BASE.Delete().{status_code=}')
        return status_code
    
    
    def GetAll(self) -> list[ITEM]:
        ''' 👉 Returns all items in the table. '''
        ##LOG.Print(f'🪣 DYNAMO.BASE.GetAll()')

        items:list[dict[str,any]] = []

        response = self._my_scan()
        items:list = response['Items']
        ##LOG.Print(f'🪣 DYNAMO.BASE.GetAll().my_scan[Items].len():', len(response['Items']))
        
        while 'LastEvaluatedKey' in response:
            lastEvaluatedKey = response['LastEvaluatedKey']
            if UTILS.IsNoneOrEmpty(lastEvaluatedKey):
                break
            
            response = self._my_scan(
                start= lastEvaluatedKey
            )
            ##print('DYNAMO.BASE.GetAll().my_scan[Items].len():', len(response['Items']))
            items.extend(response['Items'])
            
        ##print(f'DYNAMO.BASE.GetAll().{len(items)=}')

        ret:list[ITEM] = []
        for item in list(items):
            struct = ITEM(item, table=self)
            ret.append(struct)
        return ret
    

    def _get_update_params(self, body:dict[str,any]):
        '''👉 Given a dictionary we generate an update expression and a dict of values
        to update a dynamodb table.
        
        Params 
        * body (dict): Parameters to use for formatting.
        
        Returns: 
        * update expression (str)
        * update values (dict[str,any])
        * update names (dict[str,str])

        Usage:
        * expression, values, names = $.({'ID':0, 'A':1, 'B':2})
        * expression -> set #A=:A, #B=:B
        * values -> {':A':1, ':B':2}
        * names -> {'#A':1, '#B':2}
        '''

        update_expression = ["set "]
        update_values:dict[str,any] = dict()
        update_names:dict[str,str] = dict()

        for key in list(body.keys()):
            if key != 'ID':
                update_expression.append(f" #{key} = :{key},")
                update_values[f":{key}"] = body[key]
                update_names[f"#{key}"] = f"{key}"

        return "".join(update_expression)[:-1], update_values, update_names
            

    def _my_scan(self, index:str=None, start:dict[str,any]=None) -> dict[str, any]:
        ##LOG.Print(f'🪣 DYNAMO.BASE._my_scan(index={index}, start={start})')
        
        if not UTILS.IsNoneOrEmpty(index):
            
            if not UTILS.IsNoneOrEmpty(start):
                return self.Table().scan(
                    IndexName= index, 
                    ExclusiveStartKey= start)
            
            return self.Table().scan(
                IndexName= index)
        
        elif not UTILS.IsNoneOrEmpty(start):
            return self.Table().scan(
                ExclusiveStartKey= start)
        
        else:
            return self.Table().scan()
    

    @classmethod
    def TTL(cls, days:int) -> int:
        ''' 👉 Returns a TTL timestamp expression that DynamoDB understands. '''
        
        if days < 1:
            LOG.RaiseValidationException(f'Days should be > 1! Given={days}')
        
        if days > 366:
            LOG.RaiseValidationException(f'Days should be up to 1 year! Given={days}')
        
        return int(time()) + (days * 24 * 60 * 60)
    

    def GetPageFromTimestamp(self, 
        timestamp:str, 
        exclusiveStartKey:dict[str,any]= {},
        timestampColumn:str= 'Timestamp'
    ) -> dict[str,any]:
        ''' 👉 Returns paginated items from DynamoDB.
        
        Returns: {
            'Items': [...],
            'LastEvaluatedKey': {...}
        }
        
        Sources:
        * https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Query.Pagination.html 
        * https://stackoverflow.com/questions/49344272/finding-items-between-2-dates-using-boto3-and-dynamodb-scan
        * https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html#
        '''
        
        ##LOG.Print(f'🪣 DYNAMO.GetPageFromTimestamp[{self._alias}](timestamp={timestamp}, exclusiveStartKey={exclusiveStartKey})')

        # Create the filter.
        filter = {
            #'TableName': TABLE_NAME,
            #'IndexName': "main-index",
            'Select': "ALL_ATTRIBUTES",
            #'ExclusiveStartKey': exclusiveStartKey,
            'ExpressionAttributeNames': {
                "#f_up": timestampColumn
            },
            'ExpressionAttributeValues': {
                ":s_time": timestamp,
                ":e_time": UTILS.GetTimestamp()
            },
            'FilterExpression': "#f_up between :s_time and :e_time",
            'ScanIndexForward': "true"
        }

        # If there's an exclusive start key...
        if exclusiveStartKey:
            # Add the exclusive start key to the filter.
            response = self.Table().scan(
                FilterExpression= filter, 
                ExclusiveStartKey= exclusiveStartKey,
                TimestampColumn= timestampColumn)
        # If there's no exclusive start key...
        else:
            # Start the scan from the beginning.
            response = self.Table().scan(
                FilterExpression= filter,
                TimestampColumn= timestampColumn)
        
        return response
        '''
        {
            'Items': [...],
            'LastEvaluatedKey': {...}
        }
        '''


    @classmethod
    def ParseStream(cls, event:dict[str,any]) -> list[STRUCT]:
        ''' 
        👉 Parses an event from DynamoDB streams, returning an array of all DynamoDB items changed.

        Sources:
        * https://stackoverflow.com/questions/63126782/how-to-desalinize-json-coming-from-dynamodb-stream 
        * https://stackoverflow.com/questions/63050735/how-to-design-dynamodb-to-elastic-search-with-insert-modify-remove
        * https://www.thelambdablog.com/getting-dynamodb-data-changes-with-streams-and-processing-them-with-lambdas-using-python/
        * https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.Lambda.Tutorial.html
        '''

        if 'Records' not in event:
            return event
        
        result = []
        for r in event['Records']:
            tmp = {}

            new:dict[str,dict[str,any]] = r['dynamodb']['NewImage']
            for k, v in new.items():
                if "S" in v.keys() or "BOOL" in v.keys():
                    tmp[k] = v.get('S', v.get('BOOL', False))
                elif 'NULL' in v:
                    tmp[k] = None

            struct = STRUCT(tmp)
            result.append(struct)

        return result
    
