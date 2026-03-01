from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL
from pollyweb.utils.LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS


class APPRUNNER_SERVICE(AWS_RESOURCE_ITEM):


    def __init__(self, 
        pool:AWS_RESOURCE_POOL,
        client,
        meta:dict|STRUCT
    ) -> None:
        
        meta = STRUCT(meta)
        if meta.ContainsAtt('Service'):
            meta = meta['Service']

        self.Arn:str = meta['ServiceArn']
        self.Name:str = meta['ServiceName'] 
        self.Tags = meta['Tags'] if 'Tags' in meta else None
        self.Url = meta['ServiceUrl']
        self.ID = meta['ServiceId'] 

        AWS_RESOURCE_ITEM.__init__(self, 
            pool= pool,
            client= client,
            arn= meta['ServiceArn'],
            name= meta['ServiceName'])


    def _Delete(self):
        '''👉️ Deletes the service.'''
        self.Client.delete_service(ServiceArn= self.Arn)


    def WaitUntilReady(self):
        '''👉️ Waits until the service is ready.'''
        LOG.Print(f"@")

        while True:

            # Fetch service details
            response = self.Client.describe_service(
                ServiceArn= self.Arn)
            
            # Extract the status
            status = response['Service']['Status']
            LOG.Print(f"@: Current status: {status}")
            
            # Check if the service is running
            if status == "RUNNING":
                LOG.Print("@: Service is now running and ready to handle requests!")
                return

            elif status in ["OPERATION_IN_PROGRESS", "CREATING"]:
                # Wait for a bit before checking again
                LOG.Print("@: Hold on, still in progress...")
                UTILS.TIME().Sleep(3)

            else:
                response = STRUCT(response)
                status = response.GetStruct('Service').GetStruct('StatusMessage')
                LOG.RaiseException(f"@: Service encountered an issue: {status}")
