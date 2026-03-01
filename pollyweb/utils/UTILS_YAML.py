# 📚 YAML

from datetime import datetime
from io import BufferedReader
import json

from json import JSONEncoder

from .LOG import LOG
from .LOG import LOG


# 👉 yaml.load RecursionError: maximum recursion depth exceeded
# Source: https://github.com/yaml/pyyaml/issues/592
import sys
sys.setrecursionlimit(10 ** 6)


def _default(self, obj):
    ''' 👉 Module that monkey-patches json module when it's imported so
    JSONEncoder.default() automatically checks for a special "to_json()"
    method and uses it to encode the object if found.
    * https://stackoverflow.com/questions/18478287/making-object-json-serializable-with-regular-encoder/18561055#18561055'''

    # Check for to_json method.
    to_json = getattr(obj.__class__, "__to_json__", None) # From STRUCT, PRINTABLE
    to_yaml = getattr(obj.__class__, "ToYaml", None)
    

    if to_json != None:
        if LOG.IsInLoop():
            return f'<{type(obj).__name__}>'
        return to_json(obj)
    
    elif to_yaml != None:
        if LOG.IsInLoop():
            return f'<{type(obj).__name__}>'
        return to_yaml(obj)
    
    # Check for __str__ method.
    elif '__str__' in obj.__class__.__dict__:  
        return str(obj)
    
    # Check for set class.
    elif isinstance(obj, set):
        return '<SET>'
    
    # Check for type class.
    elif isinstance(obj, type):
        return '<TYPE>'
    
    # Format dates to ISO.
    elif isinstance(obj, datetime):
        return obj.isoformat()
    
    elif type(obj).__name__ in ['callable', 'method']:
        return {
            '<Callable>': {
                'Module': obj.__module__,
                'Method': obj.__name__
            }
        }

    elif isinstance(obj, Exception):
        return {
            'Type': type(obj).__name__,
            'Message': str(obj)
        }
    
    elif type(obj).__name__ == 'function':
        return {
            'Name': obj.__name__,
            'Module': obj.__module__
        }
    
    elif type(obj).__name__ == '_Environ':
        import os
        return [
            { key: value }
            for key, value in os.environ.items()
        ]

    try:    
        ret = _default.backup(self, obj)
    except TypeError as e:
        if 'is not JSON serializable' in str(e):
            return f'<{type(obj).__name__}>'

    return ret
    ##return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.backup = JSONEncoder.default  # Save unmodified default.
JSONEncoder.default = _default # Replace it.


# ✅ DONE
class UTILS_YAML: 

    ICON= '🧶'


    @classmethod
    def FromJson(cls, text: str) -> any:
        return json.loads(text)
        
    
    @classmethod
    def ToJson(cls, obj: any, indent:int=None, safe:bool=False):
        ''' 👉 Converts the object into a json string.'''
        ##LOG.Print(f'@(obj={obj})')
        try:
            return json.dumps(obj, indent=indent)
        except Exception as e:

            try: 
                LOG.Print(cls.ToJson, f': error', obj)
            except:
                try: 
                    LOG.Print(cls.ToJson, f': error1!')
                except: 
                    try: print(f'@: error2!')
                    except: pass

            if not safe:
                raise e
    
    
    @classmethod
    def FromYamlStruct(cls, text: str):
        ''' 👉 Loads an object from an YAML string and wraps it in a STRUCT.'''
        from .STRUCT import STRUCT
        ret = cls.FromYaml(text)
        return STRUCT(ret)
    

    @classmethod
    def FromYaml(cls, text: str) -> any:        
        ''' 👉 Loads an object from an YAML string.

        - https://yaml.readthedocs.io/en/latest/detail.html
        - https://stackoverflow.com/questions/50846431/converting-a-yaml-file-to-json-object-in-python
        - https://yaml.readthedocs.io/en/latest/
        - https://pyyaml.org/wiki/PyYAMLDocumentation
        '''
        ##LOG.Print(f'@: {text=}')

        if not isinstance(text, str):
            LOG.RaiseValidationException(
                f'FromYaml only accepts str, but type(text)={type(text).__name__}!')

        # "products:\n  - item 1\n  - item 2\n"
        
        try:
            import yaml
            data = yaml.safe_load(text)
        except Exception as e:
            LOG.RaiseValidationException(
                f'Invalid or unsafe YAML payload: {e}')
        
        # Convert to plain objects.
        jsonStr = json.dumps(data)
        obj = json.loads(jsonStr)

        LOG.Print(cls.FromYaml, f': returning...', obj)
        return obj
        
        
    @classmethod
    def ToYaml(cls, obj: any, indent:int=0, maxLines:int=None) -> str:
        ''' 👉 https://pyyaml.org/wiki/PyYAMLDocumentation '''
        # {'products': ['item 1', 'item 2']}
        
        data = json.loads(json.dumps(obj))
        
        try:
            import yaml
            class _IndentDumper(yaml.SafeDumper):
                def increase_indent(self, flow=False, indentless=False):
                    return super().increase_indent(flow, False)

            text = yaml.dump(
                data,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                indent=2,
                Dumper=_IndentDumper,
            )
        except Exception:
            text = '<UTILS.ToYaml(): unreadable, returning json> ' + json.dumps(data)
    
        # Remove the last empty line.
        text = text.rstrip()

        # Indent all lines, if requested.
        if indent != None and indent > 0:
            lines = text.split('\n')
            for i in range(len(lines)):
                lines[i] = (' '*indent) + lines[i]
            text = '\n'.join(lines)

        # Limit the number of lines, if requested.
        if maxLines != None:
            lines = text.split('\n')
            if len(lines) > maxLines:
                text = '\n'.join(lines[:maxLines])
                text += '\n...'

        # return yaml in text.
        return text


    @classmethod
    def FromJsonToYaml(cls, text: str) -> str:
        obj = cls.FromJson(text)
        return cls.ToYaml(obj)
        
        
    @classmethod
    def FromYamlToJson(cls, text: str) -> str:
        obj = cls.FromYaml(text)
        return cls.ToJson(obj)
    

    @classmethod
    def DecodeTextBase64(cls, encoded:str):
        # Decode the Base64 string
        import base64
        return base64.b64decode(encoded).decode('utf-8')


    @classmethod
    def EncodeTextBase64(cls, text:str):
        # Encode the string to bytes, then to Base64
        import base64
        encoded_bytes = base64.b64encode(text.encode('utf-8'))
        return encoded_bytes.decode('utf-8')


    @classmethod
    def ToBase64(cls, raw_bytes:bytes):
        '''👉 Takes byte content and returns its base64 string representation.'''
        import base64
        base64_bytes = base64.b64encode(raw_bytes)
        return base64_bytes.decode('ascii')
    

    @classmethod
    def FromBase64(cls, base64_string:str) -> bytes:
        '''👉 Takes a base64 string and returns the equivalent in raw bytes.
        * Source: https://stackabuse.com/encoding-and-decoding-base64-strings-in-python/'''

        LOG.Print(cls.FromBase64, base64_string)

        import base64
        base64_bytes = base64_string.encode('ascii')
        raw_bytes = base64.b64decode(base64_bytes)
        
        LOG.Print(
            '@: raw_bytes as string:', 
            raw_bytes.decode('ascii'))
        return raw_bytes
