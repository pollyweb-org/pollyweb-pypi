# 📚 WEB

import json
from urllib.request import urlopen
from urllib.parse import urlparse
from urllib.parse import parse_qs
from urllib.parse import quote_plus
import base64
from .STRUCT import STRUCT
from .LOG import LOG


class UrlNotFoundException(Exception):
    pass


class WEB_BASE: 
    ''' 👉️ Generic web-related methods.'''

    HTTP_TIMEOUT_SECONDS = 10
    '''👉️ Default timeout for outgoing HTTP requests.'''


    @classmethod
    def HttpPost(cls, url: str, body: any) -> STRUCT:
        ''' 👉️ Executes a POST request.'''
        pass


    @classmethod
    def HttpGet(cls, url: str) -> str:
        ''' 👉️ Executes a GET request.'''
        pass


    @classmethod
    def HttpGetJson(cls, url: str) -> any:
        '''👉 Returns an object from remote JSON content.'''
        body = cls.HttpGet(url)
        return json.loads(body)
    

    @classmethod
    def Download(cls, url: str) -> str:
        ''' 👉️ https://stackoverflow.com/questions/38408253/way-to-convert-image-straight-from-url-to-base64-without-saving-as-a-file-in-pyt '''
        LOG.Print(f'WEB.Download: {url=}')
        
        return base64.b64encode(
            s= urlopen(url, timeout=cls.HTTP_TIMEOUT_SECONDS).read())  # nosec B310
    

    @classmethod
    def HttpGetImageQR(cls, data: str) -> str:
        '''👉 Gets an serialized image.'''

        # 👉 https://goqr.me/api/doc/create-qr-code/
        # Example: https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=...
        safe_data = quote_plus(data)
        base64 = cls.Download(
            f'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={safe_data}')

        # 👉 https://stackoverflow.com/questions/8499633/how-to-display-base64-images-in-html
        '''Display as 
        <img src="data:image/png;base64, iVBORw0KGgoAAAANSUhEUgAAAAUA
                AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
                9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot" />
        '''
        return base64
    

    @classmethod
    def HttpResponse(cls, body:any={}, status=200, format='json'):
        '''👉 Wrapper of an HTTP response for Lambda functions.
        * By default, it will accept a dict and serialize it to a json string.

        HttpResponse(code=200, body={'A':1}, format='json') ->
            statusCode: 200
            body: "{\"A\": 1}"
        
        HttpResponse(code=400, body={'B':2}, format='yaml') ->
            statusCode: 400
            body: "B: 2"
            headers: 
                content-type: application/x-yaml

        HttpResponse(code=400, body='{B:2}', format='text') ->
            statusCode: 400
            body: 
                B:2
        '''

        ##LOG.Print(f'HttpResponse: body={json.dumps(body, indent=2)}')
        ##LOG.Print(f'HttpResponse: format={format}')

        ret = {
            'statusCode': status
        }

        if format == 'json':
            from .UTILS_YAML import UTILS_YAML
            ret['body'] = UTILS_YAML.ToJson(body)

        elif format == 'yaml':
            from .UTILS_YAML import UTILS_YAML
            ret['body'] = UTILS_YAML.ToYaml(body)
            # contentType: text/yaml -> shows on browser (because all text/* are text)
            # contentType: application/x-yaml -> downloads (or is it application/yaml?)
            ret["headers"] = {
                "content-type": 'application/x-yaml'
            }

        elif format == 'text':
            ret['body'] = body

        else:
            ret['body'] = body

        ##LOG.Print(f'HttpResponse: {ret=}')
        return ret
    

    @classmethod
    def HttpGetQuery(cls, args:dict):
        '''👉 Creates parameters from a dictionary.
        * .({a:1,b:2}) -> 'a=1&b=2'
        '''

        params:list[str] = []
        for k,v in args.items():
            params.append(f'{k}={v}')
        return '&'.join(params)
    
    
    @classmethod
    def ParseUrlParameter(cls, url:str, param:str):
        '''👉 Gets the value of a parameter from an URL. '''
        parsed_url = urlparse(url)
        return parse_qs(parsed_url.query)[param][0]
    

    @classmethod
    def ParseUrlHostname(cls, url:str):
        '''👉 Gets the name of the domain an URL. '''
        parsed_url = urlparse(url)
        return parsed_url.netloc
