# 📚 BUS

import json

import boto3

from LOG import LOG
events = boto3.client('events')

class EVENTBRIDGE_REAL:
        
    # 👉 https://blog.knoldus.com/how-to-create-an-eventbridge-application-in-python/
    # 👉 https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/events.html
    # 👉 https://boto3.amazonaws.com/v1/documentation/api/1.10.46/reference/services/events.html
    def Publish(self, eventBusName:str, source:str, detailType:str, detail:dict):

        LOG.Print(f'🚌 BUS.Publish()', 
            f'{source=}', f'{detailType=}', 'detail=', detail)
        
        return events.put_events(
            Entries=[
                {
                    'Source': source,
                    'DetailType': detailType,
                    'Detail': json.dumps(detail),
                    'EventBusName': eventBusName
                }
            ])


    