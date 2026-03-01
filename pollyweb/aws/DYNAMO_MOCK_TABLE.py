from NLWEB import NLWEB
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.LOG import LOG
from DYNAMO_BASE import DYNAMO_BASE_TABLE
from pollyweb.utils.UTILS import UTILS
from boto3.dynamodb.conditions import Key, ConditionBase, AttributeNotExists, Attr
from pollyweb.utils.LOG import LOG

class DYNAMO_MOCK_TABLE(DYNAMO_BASE_TABLE):
    

    def __init__(self, alias) -> None:
        super().__init__(alias)
        self._items:dict[str,dict[str:any]] = {}


    def __to_json__(self):
        return self._items

    
    def Append(self, items:list[dict[str,any]]) -> None:
        '''👉 Appends a mock item into the mocked table.'''
        for item in items:
            id = item['ID']
            self._items[id] = item

    
    def query(self, IndexName:str, KeyConditionExpression:ConditionBase) -> dict[str,any]: 
        ##LOG.Print(f'🪣 DYNAMO.MOCK.query({KeyConditionExpression=})')
        ##LOG.Print(f'🪣 DYNAMO.MOCK.query({KeyConditionExpression.get_expression()=})')
        
        key:Key = KeyConditionExpression._values[0]
        att = key.name
        value = KeyConditionExpression._values[1]

        ##LOG.Print(f'🪣 DYNAMO.MOCK.query().att={att}')
        ##LOG.Print(f'🪣 DYNAMO.MOCK.query().value={value}')
    
        items = []
        for key, item in self._items.items():
            
            if att not in item: 
                continue # Ignore the item if the attribute doesn't exist.

            if item[att] == value:
                items.append(item)
        
        return {
            'Items':items
        }
    

    def update_item(
            self, 
            Key:dict[str,any], 
            UpdateExpression:str, # e.g., set #A=:A, #B=:B
            ExpressionAttributeValues:dict,
            ExpressionAttributeNames:dict,
            ConditionExpression:ConditionBase):
        ''' 👉 https://www.tecracer.com/blog/2021/07/implementing-optimistic-locking-in-dynamodb-with-python.html'''

        from DYNAMO_MOCK import DYNAMO_MOCK
        LOG.Print('@',
            f'Domain= {DYNAMO_MOCK._activeDomain}',
            f'Table= {self._alias}',
            f'{Key=}',
            f'{UpdateExpression=}',
            f'{ExpressionAttributeValues=}',
            f'{ExpressionAttributeNames=}',
            #f'ConditionExpression=', ConditionExpression
            )        

        # Ensure the parameters.
        UTILS.AssertIsType(Key, dict)
        UTILS.AssertIsType(ExpressionAttributeValues, dict)
        UTILS.AssertIsType(ExpressionAttributeNames, dict)
        UTILS.AssertIsType(ConditionExpression, ConditionBase)

        # Convert the dictionaries to STRUCTs.
        expressionAttributeNames = STRUCT(ExpressionAttributeNames)
        expressionAttributeValues = STRUCT(ExpressionAttributeValues)

        # Get the item by key.
        item = None
        resp = self.get_item(Key)
        if 'Item' in resp:
            item = resp['Item']

        # Verify the item.
        if item == None:

            # Verify it should exist.
            if ConditionExpression != None:
                if ConditionExpression.expression_operator == 'attribute_exists':
                    keys= [ x for x in self._items ]
                    LOG.RaiseValidationException(
                        f'Item with [{Key}] not found to update! Keys={keys}')

            # Create a new item
            item = {}
            
        else:
            # Verify it shouldn't  exist.
            if isinstance(ConditionExpression, AttributeNotExists):
                LOG.RaiseValidationException(
                    f'Item with [{Key}] found, but should not exist!')
            
            # Get the item by key.
            item = self._items[Key['ID']]
            
            # Verify the condition
            if not UTILS.IsNoneOrEmpty(ConditionExpression):
                
                if 'AND' in ConditionExpression.expression_format:
                    LOG.RaiseValidationException(
                        f'AND is not implemented for conditions!')
                
                if ConditionExpression.expression_operator not in ['=','attribute_exists']:
                    msg = f'Only Equals(=) is implemented for conditions!'
                    msg = msg +  f'Given=[{ConditionExpression.expression_operator}]'
                    LOG.RaiseValidationException(msg)
            
                if ConditionExpression.expression_operator in ['=']:
                    field:Attr = ConditionExpression._values[0]
                    att = field.name
                    val = ConditionExpression._values[1]
                    if item[att] != val:
                        LOG.RaiseValidationException(
                            f'Condition failed: given={item[att]}, expected={val}!')

        # Perform the update.
        item['ID'] = Key['ID']
        
        # Remove the first 4 characters of the UpdateExpression.
        if UpdateExpression[0:4] == 'set ': 
            UpdateExpression = UpdateExpression[4:]
        
        # Update the item.
        for update in UpdateExpression.split(','):
            pair = update.strip().split('=')
            UTILS.AssertLenght(pair, 2, 'Unexpected update expression!')
            attName = pair[0].strip()
            valName = pair[1].strip()
            att = expressionAttributeNames.RequireAtt(attName)
            val = expressionAttributeValues.GetAtt(valName)
            item[att] = STRUCT.Unstruct(val)

        # Store the item.
        id = Key['ID']
        self._items[id] = item

        # Raise an event.
        event = self.MockStream(items=[item])
        self.OnStream(event)


    @classmethod
    def MockStream(cls, items:list) -> any:
        '''👉 Returns a mocked DynamoDB stream.'''
        
        records = []
        for struct in STRUCT(items).Structs():

            image = {}
            for att in struct.Attributes():
                image[att] = { 'S': struct[att] }

            records.append({
                'dynamodb': {
                    'NewImage': image
                }
            })

        return {
            'Records': records
        }
    

    def _Items(self):
        ret = self._items
        UTILS.AssertIsType(ret, dict)
        return ret


    def get_item(self, Key:dict[str,any]) -> dict[str,any]:
        ##LOG.Print(f'MOCK_TABLE.get_item(Key={Key})')
        ##LOG.Print(f'MOCK_TABLE.get_item().{self._items=})')

        if len(Key) != 1 or 'ID' not in Key:
            LOG.RaiseException('Please call with Key={ID:?}')
        
        id = Key['ID']

        if STRUCT(self._items).ContainsAtt(id):
            return {
                'Item': UTILS.Copy(self._items[id])
            }
        
        else:
            return {}
    

    def delete_item(self, Key:dict[str,any]):

        item = self.get_item(Key)
        if item == None:
            LOG.RaiseException(f'Item expected with Key: {Key}')
        
        id = Key['ID']
        del self._items[id]

        return { 
            'ResponseMetadata': { 
                'HTTPStatusCode': 'MOCK'
            }
        }
    

    def scan(
        self, 
        IndexName:str=None, 
        ExclusiveStartKey:dict[str,any]=None,
        FilterExpression:str=None,
        TimestampColumn:str= 'Timestamp'
    ) -> dict[str, any]:
        
        '''
        LOG.Print(f'🪣 DYNAMO.MOCK.scan(')
        LOG.Print(f'    IndexName= {IndexName},') 
        LOG.Print(f'    ExclusiveStartKey= {ExclusiveStartKey},')
        if FilterExpression == None:
            LOG.Print(f'    FilterExpression= {FilterExpression}')
        else:
            LOG.Print(f'    FilterExpression:')
            LOG.Print(f"        Select: {FilterExpression['Select']}")
            LOG.Print(f"        ExpressionAttributeNames: {FilterExpression['ExpressionAttributeNames']}")
            LOG.Print(f"        ExpressionAttributeValues: {FilterExpression['ExpressionAttributeValues']}")
            LOG.Print(f"        FilterExpression: {FilterExpression['FilterExpression']}")
            LOG.Print(f"        ScanIndexForward: {FilterExpression['ScanIndexForward']}")
        '''
        
        items = []
        lastEvaluatedKey = None
        interrupted = False

        # Skip until the last ID is found, and scan from there onwards.
        skipUntil = None
        if ExclusiveStartKey != None:
            skipUntil = ExclusiveStartKey['ID']
        
        allItems = list(self._items.values())
        ##LOG.Print(f'🪣 DYNAMO.MOCK.scan(). {len(allItems)=}')

        for item in allItems:
            append = False

            if skipUntil != None:
                # Skip until the last ID is found, and scan from there onwards.
                if skipUntil == item['ID']:
                    skipUntil = None
                ##LOG.Print(f'> skipped @DYNAMO.MOCK.scan()')
            
            elif FilterExpression == None:
                append = True
                ##LOG.Print(f'> no filter, to append @DYNAMO.MOCK.scan()')

            else:
                filter = FilterExpression['FilterExpression']
                if filter != '#f_up between :s_time and :e_time':
                    LOG.RaiseException('Only between filters are implemented!')
                
                s_time = FilterExpression['ExpressionAttributeValues'][':s_time']
                e_time = FilterExpression['ExpressionAttributeValues'][':e_time']
                
                if TimestampColumn not in item:
                    LOG.RaiseValidationException(
                        f'The item should have a timestamp attribute named [{TimestampColumn}]!')

                if item[TimestampColumn] >= s_time and item[TimestampColumn] <= e_time:
                    append = True
                    ##LOG.Print(f"> whitin filter, to append @DYNAMO.MOCK.scan(): {item[TimestampColumn]=}, {s_time=}, {e_time=}")
                else:
                    pass
                    ##LOG.Print(f"> filtered and ignored @DYNAMO.MOCK.scan(): {item[TimestampColumn]=}, {s_time=}, {e_time=}")

            if append:
                # Add and memorize the last Key for an eventual pagination.
                items.append(item)

                if 'ID' in item:
                    lastEvaluatedKey = { 'ID': item['ID'] }
                ##LOG.Print(f'> appended @DYNAMO.MOCK.scan(): {len(items)=}')

            if len(items) >= 10:
                
                if 'ID' not in item:
                    LOG.RaiseException('Pagination not supported for items without ID!')
                
                # Break on maximum 10 records.
                if item['ID'] != list(self._items)[-1]:
                    # If not the last item in the table.
                    interrupted = True
                    break

        ##LOG.Print(f'🪣 DYNAMO.MOCK.scan().{interrupted=}')
        if lastEvaluatedKey != None:
            if not interrupted:
                # If it wasn't interrupted, then we don't send the last ID.
                lastEvaluatedKey = None

        return {
            'Items': items,
            'LastEvaluatedKey': lastEvaluatedKey
        }
