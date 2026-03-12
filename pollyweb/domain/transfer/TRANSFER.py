
from PW_AWS.AWS import AWS
from NLWEB import NLWEB
from PW_AWS.ITEM import ITEM
from pollyweb import LOG
from MSG import MSG
from pollyweb import UTILS


class TRANSFER(ITEM):
    ''' 
    👉 Allows for 2 domains to securily transfer files between each other
    without adding the content of the file to the requests.

    Origin: any-receiver.com
    TransferID: <uuid>
    Type: SENT|RECEIVED
    Location: 's3://...'
    TTL: <timestamp>
    '''


    def RequireLocation(self):
        return self.RequireStr('Location')

    def RequireType(self):
        ret = self.RequireStr('Type')
        UTILS.AssertIsAnyValue(ret, ['SENT', 'RECEIVED'])
        return ret
    
    def RequireOrigin(self):
        return self.RequireStr('Origin')
    

    @classmethod
    def _Table(cls):
        return AWS.DYNAMO('TRANSFERS', keys=['Origin','TransferID'])
    

    @classmethod
    def _GetFromDynamo(cls, origin:str, transferID:str):
        ''' 👉 Get from the database.'''
        item = cls._Table().Require({
            'Origin': origin, 
            'TransferID': transferID
        })
        return cls(item)
    

    def _GetFromS3(self):
        ''' 👉 Get from S3.'''
        uri = AWS.S3().URL(self.RequireLocation())
        return AWS.S3().ReadBytes(
            bucket= uri.bucket,
            key= uri.key)
        

    @classmethod
    def _SaveTransfer(cls, direction:str, origin:str, content:bytes, transferID:str=None):
        '''👉️ Saves to S3+DynamoDB, and returns the ID.'''

        LOG.Print(
            '🛄 TRANSFER._SaveTransfer()', 
            f'Domain= {NLWEB.CONFIG().RequireDomain()}',
            f'{origin=}', f'{transferID=}', 
            f'content.type=', type(content).__name__)

        UTILS.RequireArgs([direction, origin, content])
        UTILS.AssertIsType(content, bytes)
        UTILS.AssertIsAnyValue(direction, ['SENT', 'RECEIVED'])

        if transferID == None:
            transferID = UTILS.UUID()

        # TODO: auto delete from S3 on DynamoDB delete.
        location = AWS.S3().WriteBytes(
            content= content, 
            key= f'/TRANSFERS/{direction}/{origin}/{transferID}')

        item = {
            'Origin': origin,
            'TransferID': transferID,
            'Type': direction,
            'Location': location
        }

        # Insert with a time to live.
        cls._Table().Insert(item, days=1)

        return transferID
    

    @classmethod
    def StageTransfer(cls, origin:str, content:bytes) -> str:
        '''👉️ Saves the content locally, to be ready to be downloaded.'''
        
        LOG.Print(
            '🛄 TRANSFER.StageTransfer()', 
            f'Domain= {NLWEB.CONFIG().RequireDomain()}',
            f'{origin=}', 
            f'content.type=', type(content).__name__)

        transferID = cls._SaveTransfer(
            direction='SENT', 
            origin=origin, 
            content=content)
        
        return transferID


    @classmethod
    def InvokeDownload(cls, origin:str, transferID:str):
        LOG.Print(
            '🛄 TRANSFER.InvokeDownload()', 
            f'Domain= {NLWEB.CONFIG().RequireDomain()}',
            f'{origin=}', f'{transferID=}')

        # Download the base64 string from the remote server.
        ret = NLWEB.BEHAVIORS().SYNCAPI().Invoke(
            to= origin, 
            subject= 'Download@Transfer',
            body= {
                'TransferID': transferID
            })
        
        # Get the base 64 string.
        content_base64 = ret.RequireStr('Base64')

        # Convert into raw bytes.
        content_bytes = UTILS.FromBase64(
            base64_string= content_base64)
        
        # Save locally.
        cls._SaveTransfer(
            direction= 'RECEIVED', 
            origin= origin, 
            content= content_bytes, 
            transferID= transferID)
        

    @classmethod
    def HandleDownload(cls, event):
        LOG.Print(
            '🛄 TRANSFER.HandleDownload()', 
            f'Domain= {NLWEB.CONFIG().RequireDomain()}',
            event)

        msg = MSG(event)
        msg.MatchSubject('Download@Transfer')

        # Get the details from the database.
        transferID = msg.RequireUUID('TransferID')
        transfer = cls._GetFromDynamo(
            origin= msg.RequireFrom(),
            transferID= transferID)
        
        # Confirm that this transfer was sent to this domain.
        UTILS.AssertEqual(msg.RequireFrom(), transfer.RequireOrigin())
        UTILS.AssertEqual(transfer.RequireType(), 'SENT')

        base64 = UTILS.ToBase64(transfer._GetFromS3())
        return {
            'Base64': base64
        }


    @classmethod
    def GetReceivedTransfer(cls, origin:str, transferID:str) -> bytes:
        '''👉 Reads from the local database a transfer that has previously been downloaded.'''
        LOG.Print('🛄 TRANSFER.ReceivedTransfer()')

        # Read the details from the database.
        transfer = cls._GetFromDynamo(
            origin= origin,
            transferID= transferID)
        
        # Ensure this was a received transfer.
        UTILS.AssertEqual(transfer.RequireType(), 'RECEIVED')
        
        # Read the content from S3.
        location = AWS.S3().URL(transfer.RequireLocation())
        content = AWS.S3().ReadBytes(
            bucket= location.bucket, 
            key= location.key)

        # return the content in bytes.
        return content
    

    @classmethod
    def DeleteTransfer(cls, origin:str, transferID:str):
        LOG.Print('🛄 TRANSFER.DeleteTransfer()')

        # Read the details from the database.
        transfer = cls._GetFromDynamo(
            origin= origin,
            transferID= transferID)
        
        # Delete from S3.
        uri = S3.URL(transfer.RequireLocation())
        S3.Delete(
            bucket= uri.bucket,
            key= uri.key)
        
        # Delete from the database.
        transfer.Delete()