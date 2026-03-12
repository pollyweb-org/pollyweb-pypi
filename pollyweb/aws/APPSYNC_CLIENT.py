# 📚 APPSYNC
# FROM: https://dev.to/trisduong/tutorial-use-aws-eventbridge-and-appsync-for-real-time-notification-to-client-side-405a


from LOG import LOG
   
from base64 import b64encode, decode
from datetime import datetime
from uuid import uuid4

import websocket
import threading
import ssl

import json


class APPSYNC_CLIENT():
        
    def __init__(self, API_URL:str, API_KEY:str) -> None:

        self.API_URL = API_URL
        self.API_KEY = API_KEY

        # Discovered values from the AppSync endpoint (API_URL)
        self.WSS_URL = API_URL.replace('https', 'wss').replace('appsync-api', 'appsync-realtime-api')
        self.HOST = API_URL.replace('https://', '').replace('/graphql', '')

        # Subscription ID (client generated)
        self.SUB_ID = str(uuid4())

        # Create API key authentication header
        self.api_header = {
            'host': self.HOST,
            'x-api-key': self.API_KEY
        }

        # Set up Timeout Globals
        self.timeout_timer:threading.Timer = None
        self.timeout_interval = 10


    # Calculate UTC time in ISO format (AWS Friendly): YYYY-MM-DDTHH:mm:ssZ
    def header_time(self, ):
        return datetime.utcnow().isoformat(sep='T', timespec='seconds') + 'Z'


    # Encode Using Base 64
    def header_encode(self, header_obj):
        return b64encode(json.dumps(header_obj).encode('utf-8')).decode('utf-8')


    # reset the keep alive timeout daemon thread
    def reset_timer(self, ws):

        if (self.timeout_timer):
            self.timeout_timer.cancel()

        self.timeout_timer = threading.Timer(
            self.timeout_interval, 
            lambda: ws.close())
        
        self.timeout_timer.daemon = True
        self.timeout_timer.start()


    # Socket Event Callbacks, used in WebSocketApp Constructor
    def on_message(self, ws, message):

        print('### message ###')
        print('<< ' + message)

        message_object = json.loads(message)
        message_type = message_object['type']

        if (message_type == 'ka'):
            self.reset_timer(ws)

        elif (message_type == 'connection_ack'):
            self.timeout_interval = int(
                json.dumps(
                    message_object['payload']['connectionTimeoutMs']))

            register = {
                'id': self.SUB_ID,
                'payload': {
                    'data': self.GQL_SUBSCRIPTION,
                    'extensions': {
                        'authorization': {
                            'host': self.HOST,
                            'x-api-key': self.API_KEY
                        }
                    }
                },
                'type': 'start'
            }
            start_sub = json.dumps(register)
            print('>> ' + start_sub)
            ws.send(start_sub)

        elif (message_type == 'data'):
            deregister = {
                'type': 'stop',
                'id': self.SUB_ID
            }
            end_sub = json.dumps(deregister)
            print('>> ' + end_sub)
            ws.send(end_sub)

        elif (message_object['type'] == 'error'):
            print('Error from AppSync: ' + message_object['payload'])


    def on_error(self, ws, error):
        print('### error ###')
        print(error)


    def on_close(self, ws):
        print('### closed ###')


    def on_open(self, ws):
        print('### opened ###')
        init = {
            'type': 'connection_init'
        }
        init_conn = json.dumps(init)
        print('>> ' + init_conn)
        ws.send(init_conn)


    def Subscribe(self, query:str, variables:dict, single:bool=False):
        '''👉 Subscribes to notifications.

        Arguments:
        * query: string used in appsync for a subscription.
        * variables: dictionary of variables and their values.
        * single: if true, it deregisters the subscription upon the 1st message.

        Example:
        * Subscribe( 
            query = """
                subscription MySubscription($walletID: ID!) {
                    onPush(walletID: $walletID) {
                        payload
                        walletID
                        command
                    }
                }
            """,
            variables = { 
                'walletID': '<my-wallet-id>'
            },
            single = True
        )
        '''

        # GraphQL subscription Registration object
        self.GQL_SUBSCRIPTION = json.dumps({
            "query": query,
            "variables": variables
        })

        # Uncomment to see socket bytestreams
        # websocket.enableTrace(True)

        # Set up the connection URL, which includes the Authentication Header
        #   and a payload of '{}'.  All info is base 64 encoded
        connection_url = self.WSS_URL 
        connection_url += '?header=' + self.header_encode(self.api_header) 
        connection_url += '&payload=e30='

        # Create the websocket connection to AppSync's real-time endpoint
        #  also defines callback functions for websocket events
        #  NOTE: The connection requires a subprotocol 'graphql-ws'
        print('Connecting to: ' + connection_url)

        ws = websocket.WebSocketApp(
            connection_url,
            subprotocols= ['graphql-ws'],
            on_open= self.on_open,
            on_message= self.on_message,
            on_error= self.on_error,
            on_close= self.on_close)

        ws.run_forever(
            sslopt={
                "cert_reqs": ssl.CERT_NONE, 
                "ssl_version": ssl.PROTOCOL_TLSv1_2
            })
