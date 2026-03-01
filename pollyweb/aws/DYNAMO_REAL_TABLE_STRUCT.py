# 📚 DYNAMO

from AWS_RETRY import RetryWithBackoff
from DYNAMO_REAL_TABLE_DATA import DYNAMO_REAL_TABLE_DATA
from LAMBDA_FUNCTION_REAL import LAMBDA_FUNCTION_REAL
from pollyweb.utils.LOG import LOG

import boto3
from botocore.exceptions import ClientError


import boto3
dynamoResource = boto3.resource('dynamodb')
dynamodb = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')


from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS


class DYNAMO_REAL_TABLE_STRUCT(DYNAMO_REAL_TABLE_DATA):
    '''👉 Real implementation of a Dynamo table on AWS.'''

    ICON = '🪣'


    @classmethod
    def CLIENT(cls):
        '''👉 Returns the Dynamo client.'''
        from DYNAMO_REAL_CLIENT import DYNAMO_REAL_CLIENT
        return DYNAMO_REAL_CLIENT(dynamoResource.meta.client)


    def GetStatus(self) -> str:
        '''👉 Returns the status of the table.'''
        return self.Table().table_status


    CACHE:STRUCT = None
    def GetCache(self):
        '''👉 Loads the cache.'''
        if DYNAMO_REAL_TABLE_STRUCT.CACHE is None:
            tables = self.CLIENT().GetTableDetails()
            DYNAMO_REAL_TABLE_STRUCT.CACHE = STRUCT(tables)
        return DYNAMO_REAL_TABLE_STRUCT.CACHE
    

    def Exists(self, cache:bool=False) -> bool:        
        '''👉 Returns True if the table exists.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.Exists({self.Name()})')

        if cache:
            mem = self.GetCache()
            return self.Name() in mem.Keys()

        #return tableName in cls.GetTableNames()
        
        try:
            # Attempt to retrieve the table status. 
            status = self.GetStatus()

            # If we got here, the table exists.
            LOG.Print(f"@: Table {self.Name()} found with status: {status}.")
            return True

        except ClientError as e:
            # If the table doesn't exist, return False
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                LOG.Print(f"@: Table [{self._name}] does not exist.")
                return False
            
            # Rethrow the exception if it wasn't a ResourceNotFoundException
            raise
    

    def SetReadCapacityUnits(self, units:int) -> None:
        '''👉 Sets the read capacity units.'''
        self.SetAtt('ReadCapacityUnits', units)


    def GetReadCapacityUnits(self) -> int:
        '''👉 Returns the read capacity units.'''
        return self.GetInt('ReadCapacityUnits', default=0)


    def SetWriteCapacityUnits(self, units:int) -> None:
        '''👉 Sets the write capacity units.'''
        self.SetAtt('WriteCapacityUnits', units)


    def GetWriteCapacityUnits(self) -> int:
        '''👉 Returns the write capacity units.'''
        return self.GetInt('WriteCapacityUnits', default=0)


    def GetProvisionedThroughput(self):
        '''👉 Returns the provisioned throughput.'''
        read = self.GetReadCapacityUnits()
        write = self.GetWriteCapacityUnits()
        if not read and not write:
            return None
        return {
            'ReadCapacityUnits': read,
            'WriteCapacityUnits': write
        }


    def GetDefaultSchema(self) -> dict:
        '''👉 Returns the schema of the table.'''
        # KeySchema
        return [
            {
                'AttributeName': 'ID',
                'KeyType': 'HASH'
            }
        ]
    

    def GetDefaultAttributes(self) -> dict:
        '''👉 Returns the attributes of the table.'''
        return [
            {
                'AttributeName': 'ID',
                'AttributeType': 'S'
            }
        ]


    def Create(self, tags:dict):
        '''👉 Creates a table.'''

        LOG.Print(f'@({self.Name()=})')
        
        # Ensure the tags are a dictionary
        UTILS.AssertIsDict(tags, require=True, itemType=str)

        tags = [
            {
                'Key': key,
                'Value': value
            }
            for key, value in tags.items()
        ]

        # Get the default schema, attributes, and provisioned throughput
        keySchema = self.GetDefaultSchema()
        attributeDefinitions = self.GetDefaultAttributes()
        provisionedThroughput = self.GetProvisionedThroughput()
        name = self.Name()

        # Create the table
        if provisionedThroughput is None:
            create = dynamoResource.create_table(
                TableName= name,
                KeySchema= keySchema,
                AttributeDefinitions= attributeDefinitions,
                BillingMode='PAY_PER_REQUEST',
                Tags= tags)
        else:
            create = dynamoResource.create_table(
                TableName= name,
                KeySchema= keySchema,
                AttributeDefinitions= attributeDefinitions,
                ProvisionedThroughput= provisionedThroughput,
                BillingMode='PROVISIONED',
                Tags= tags)
            
        # Wait until the table exists.
        create.wait_until_exists()
    
        LOG.Print(
            f"🪣 DYNAMO.TABLE.CreateTable().created: {create.table_name}", 
            create)

    
    def EnsureExists(self, tags:dict, cache:bool=False) -> None:
        '''👉 Creates a table if it doesn't exist.'''
        LOG.Print(f'@({self.Name()=}, {cache=})')
        
        if not self.Exists(cache=cache):
            self.Create(tags=tags)


    def EnsureStream(self, enabled:bool=True) -> None:
        '''👉 Creates a stream if it doesn't exist.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.EnsureStream({self.Name()=})')
        
        actuallyEnabled = self.IsStreamEnabled()

        if enabled and not actuallyEnabled:
            self.SetStream(enabled=True)
            
        elif not enabled and actuallyEnabled:
            self.SetStream(enabled=False)


    def IsStreamEnabled(self) -> bool:
        '''👉 Returns True if the stream is enabled.'''

        table = self.Table()

        # Get the current stream specification from the table's description
        try:
            current_stream_specification = table.stream_specification
            if current_stream_specification is None:
                 return False
            stream_enabled = current_stream_specification.get(
                'StreamEnabled', False)
        except KeyError:
            current_stream_specification = None
            stream_enabled = False

        return stream_enabled
    

    def SetStream(self, enabled:bool=True):
        '''👉 Sets the stream.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.SetStream({self.Name()=})')
        
        table = self.Table()

        stream = {
            'StreamEnabled': enabled,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'
        }
        table.update(StreamSpecification=stream)

        LOG.Print(f"Stream enabled for table {self.Name()}.")


    def IsTtlEnable(self) -> bool:
        '''👉 Returns True if the TTL is enabled.'''
                
        # Access the low-level client from the resource
        client = dynamoResource.meta.client

        # Get the current TTL settings for the table
        ttl_description = client.describe_time_to_live(
            TableName= self.Name())

        # Check if TTL is enabled
        if ttl_description['TimeToLiveDescription']['TimeToLiveStatus'] != 'ENABLED':
            # LOG.Print("TTL is not enabled.")
            return False
        
        else:
            # LOG.Print("TTL is already enabled with settings:", ttl_description['TimeToLiveDescription'])
            return True
        

    def EnableTtl(self):
        '''👉 Enables the TTL.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.EnableTtl({self.Name()=})')
        
        # Access the low-level client from the resource
        client = dynamoResource.meta.client

        # Enable TTL for the table
        client.update_time_to_live(
            TableName= self.Name(),
            TimeToLiveSpecification={
                'AttributeName': 'TTL',
                'Enabled': True
            })
        

    def EnsureTtl(self, enabled:bool=True):
        '''👉 Ensures the TTL is enabled.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.EnsureTtl({self.Name()=})')
        
        actualEnabled = self.IsTtlEnable()
        if enabled and not actualEnabled:
            self.EnableTtl()
            LOG.Print(f'TTL is enabled on [{self.Name()}].', self)


    def IsPitrEnabled(self) -> bool:
        '''👉 Returns True if Point-In-Time Recovery is enabled.'''
        
        # Access the low-level client from the resource
        client = dynamoResource.meta.client

        # Get the current PITR settings for the table
        pitr_description = client.describe_continuous_backups(
            TableName= self.Name())

        s = STRUCT(pitr_description)
        s = s.RequireStruct('ContinuousBackupsDescription')
        s = s.RequireStruct('PointInTimeRecoveryDescription')
        s = s.RequireStr('PointInTimeRecoveryStatus')

        # Check if PITR is enabled
        if s != 'ENABLED':
            # LOG.Print("PITR is not enabled.")
            return False
        
        else:
            # LOG.Print("PITR is already enabled with settings:", pitr_description['ContinuousBackupsDescription'])
            return True


    @RetryWithBackoff(codes= ['ContinuousBackupsUnavailableException'])
    def EnsurePitr(self):
        '''👉 Enables Point-In-Time Recovery.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.EnsurePitr({self.Name()=})')
        
        if self.IsPitrEnabled():
            return

        # Access the low-level client from the resource
        client = dynamoResource.meta.client

        # Enable PITR for the table
        response = None
        try:
            response = client.update_continuous_backups(
                TableName= self.Name(),
                PointInTimeRecoverySpecification={
                    'PointInTimeRecoveryEnabled': True
                })
        except ClientError as e:
            if type(e).__name__ == 'ContinuousBackupsUnavailableException':
                LOG.Print(f"PITR is being enabled on {self.Name()}.")
        
        # Confirm if the response is successful
        if response is not None:
            s = STRUCT(response)
            s = s.GetStruct('ContinuousBackupsDescription')
            s = s.GetStruct('PointInTimeRecoveryDescription')
            s = s.GetStr('PointInTimeRecoveryStatus')
            if s != 'ENABLED':
                LOG.RaiseException(f'PITR was unsuccessful on {self.Name()}.', 
                    self, response)
                
        # Wait for backups to become available
        table_name = self.Name()
        while True:
            response = dynamodb.describe_continuous_backups(
                TableName= table_name)
            status = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
            if status == 'ENABLED':
                #print("Continuous backups are now available.")
                break
            else:
                #LOG.Print("Waiting for continuous backups to become available...")
                import time
                time.sleep(1)  # wait for 10 seconds before checking again


    def GetGlobaIndexes(self) -> list[str]:
        '''👉 Returns the global indexes.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.GetGlobalIndexes({self.Name()=})')
        
        client = dynamoResource.meta.client
        # Get the current indexes
        response = client.describe_table(
            TableName= self.Name())

        # Access the global secondary indexes
        table = response.get('Table', {})
        indexes = table.get('GlobalSecondaryIndexes', [])

        LOG.Print(f"🪣 DYNAMO.TABLE.GetGlobalIndexes.ret:", indexes)
        return indexes
    

    def GetGlobaIndexNames(self) -> list[str]:
        '''👉 Returns the global indexes.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.GetGlobaIndexNames({self.Name()=})')
        
        ret = [
            index['IndexName']
            for index
            in self.GetGlobaIndexes()
        ] 

        LOG.Print(f"🪣 DYNAMO.TABLE.GetGlobaIndexNames.ret:", ret)    
        return ret


    def EnsureIndexes(self, indexes:list[str]):
        '''👉 Ensures the indexes are created.'''
        LOG.Print(f'🪣 DYNAMO.TABLE.EnsureIndexes({self.Name()=})')
        
        if indexes is None: return
        if len(indexes) == 0: return

        client = dynamoResource.meta.client

        # Get the current index names
        current_index_names = self.GetGlobaIndexNames()

        # Create the indexes
        for index in indexes:
            if index not in current_index_names:
                client.update_table(
                    TableName= self.Name(),
                    AttributeDefinitions=[
                        {
                            'AttributeName': index,
                            'AttributeType': 'S'
                        }
                    ],
                    GlobalSecondaryIndexUpdates=[
                        {
                            'Create': {
                                'IndexName': index,
                                'KeySchema': [
                                    {
                                        'AttributeName': index,
                                        'KeyType': 'HASH'
                                    }
                                ],
                                'Projection': {
                                    'ProjectionType': 'ALL'
                                },
                                #'ProvisionedThroughput': {
                                #    'ReadCapacityUnits': 5,
                                #    'WriteCapacityUnits': 5
                                #}
                            }
                        }
                    ]
                )
                LOG.Print(f"Index {index} created.")
            else:
                LOG.Print(f"Index {index} already exists.")

        #LOG.Exception('Confirm indexes are created.', self)


    def GetArn(self):
        table_name = self.Name()
        response = dynamodb.describe_table(TableName=table_name)        
        arn = STRUCT(response).RequireStruct('Table').RequireStr('TableArn')
        return arn
    

    def GetStreamArn(self):
        table_name = self.Name()
        response = dynamodb.describe_table(TableName=table_name)
        stream_arn = STRUCT(response).RequireStruct('Table').RequireStr('LatestStreamArn')
        return stream_arn


    def TriggerLambda(self, fn:LAMBDA_FUNCTION_REAL):
        
        # Get the stream ARN for the DynamoDB table
        table_name = self.Name()
        stream_arn = self.GetStreamArn()

        # Create event source mapping
        try:
            response = lambda_client.create_event_source_mapping(
                EventSourceArn=stream_arn,
                FunctionName= fn.RequireName(),  # Replace with your Lambda function name
                Enabled= True,
                BatchSize= 100,  # Number of records to send to Lambda in each batch
                StartingPosition= 'LATEST'  # Options: 'TRIM_HORIZON', 'LATEST', 'AT_TIMESTAMP'
            )
            LOG.Print(f"@: Event source mapping created for table {table_name}.")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                LOG.Print(f"@: Event source mapping already exists for table {table_name}.")
            else:
                raise e