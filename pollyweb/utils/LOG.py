import traceback
import logging
from typing import Union


from .LOG_EXCLUDES import LOG_EXCLUDES
from .LOG_PARALLEL import LOG_PARALLEL
from .LOG_PLACEHOLDER import LOG_PLACEHOLDER
from .LOG_SETTINGS import LOG_SETTINGS


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LOG(LOG_PARALLEL, LOG_EXCLUDES):
    '''👉️ Methods for logging.'''


    @classmethod
    def hello(cls):
        return "Hi from pollyweb_utils, from inside LOG!"

    @classmethod
    def EXCLUDES(cls):
        '''👉 Exclusions from logging.'''
        return cls._excludes
    

    @classmethod
    def PARALLEL(cls):
        '''👉 Methods for parallel logging.'''
        return LOG_PARALLEL()
    
    
    @classmethod
    def _Debug(cls, msg:str):
        '''👉 Method to act on specific messages.'''
        return
        if msg.startswith('LOG.Print(') \
        and '📦 UTILS.OBJ.IsNoneOrEmpty' not in msg:
            print(f'🐞 {msg}')
            


    _settings = LOG_SETTINGS()
    '''👉️ Settings for the log.'''

    @classmethod
    def Settings(cls): 
        '''👉️ Returns the logging settings.'''
        return cls._settings


    _placeholder = LOG_PLACEHOLDER()
    @classmethod
    def Placeholder(cls): return cls._placeholder
    

    @classmethod
    def Buffer(cls):
        '''👉 Returns the buffer.'''
        if hasattr(cls, '_buffer') == False:
        
            from .LOG_BUFFER import LOG_BUFFER
            file = cls.GetLogDir().GetFile('LOG.md')
            cls._buffer = LOG_BUFFER(
                path= file.GetPath(), 
                deleteFirst=True)
            
        return cls._buffer
    

    _lastLog:str = None
    _lastArgs = None
    

    @staticmethod
    def Init():
        '''👉 Initialization for testing.'''
        if LOG.IsLambda():
            raise Exception('Cannot use Init() in Lambda.')
        LOG.DeleteDumps()
        LOG.GetLogDir().Touch()
        LOG.Buffer().Clean()


    @classmethod
    def AssertInProjectRoot(cls):
        '''👉️ Exists if the script is not running in the root folder.'''
        from .DIRECTORY import DIRECTORY
        dir = DIRECTORY.GetCurrent()
        is_pkg_repo = dir.ContainsFile('pyproject.toml') and (
            dir.ContainsDirectory('src') or
            dir.ContainsDirectory('pollyweb')
        )
        is_pollyweb_repo = (
            dir.ContainsDirectory('python') and
            (dir.ContainsDirectory('tests') or dir.ContainsDirectory('layers'))
        )
        if not (is_pkg_repo or is_pollyweb_repo):
            print('🙀 Run this on the base directory of the project.')
            print('🙀 It is missing pyproject.toml and a src/ or pollyweb/ directory.')
            exit(1)


    @classmethod
    def DeleteDumps(cls):
        '''👉 Deletes the __dumps__ directory.'''
        cls.AssertInProjectRoot()
        return cls.Buffer().GetDir().Delete(recursive=True)


    @classmethod
    def GetLogDir(cls):
        '''👉️ Returns the __dumps__ directory.'''

        if cls.IsLambda():
            raise Exception('Cannot use GetLogDir() in Lambda.')
        
        cls.AssertInProjectRoot()
        from .UTILS import UTILS
        return UTILS.OS().Directory('__dumps__').Touch()
        

    @classmethod
    def _PrintArg(cls, arg, lines:list):

        # For lists, print the individual elements.
        if isinstance(arg, list) or isinstance(arg, tuple):
            for x in arg[:20]: # Limit to 20 elements.
                cls._PrintArg(arg=x, lines=lines)
            return

        # Process function pointers.
        if type(arg).__name__ == 'method':
            arg = f'{arg}'

        # Process native types.
        if type(arg) in [str, int, float, bool]:

            # ignore empty messages.
            if arg == 'msg=None':
                return

            # print native variables as is.
            if type(arg) != str:
                lines.append(f'  > {type(arg).__name__}: `{arg}`')
                return
            
            # Process a string with multiple lines.
            parts = arg.split('\n')
            if len(parts) == 1:
                lines.append(f'  > {arg}')
                return

            for line in parts:
                line = line.strip()
                if line != '' and line != 'None':
                    lines.append(f'  > {line}')
            return

        # Process complex objects.
        if type(arg).__name__ == 'method':
            arg = arg()

        # If the arg has its own ToYaml, use it.
        if hasattr(arg, 'ToYaml') or hasattr(arg, '__to_yaml__'):
            if isinstance(arg, list): indent = 4
            else: indent = 6

            if hasattr(arg, 'ToYaml'):
                yaml = arg.ToYaml(indent=indent)
            elif hasattr(arg, '__to_yaml__'):
                yaml = arg.__to_yaml__(indent=indent)
            else:
                raise Exception('Invalid operation')

            from .UTILS import UTILS
            yaml = UTILS.LimitLines(yaml, 100)

        # If the object doesn't have its own ToYaml, use the UTILS.ToYaml().
        else: 
            import json
            try:
                raw = json.loads(json.dumps(arg))
            except Exception as e:
                print('#####')
                print(arg)
                print('#####')
                print(type(arg))
                print(type(arg).__name__)
                print('#####')
                raise

            if isinstance(raw, list): indent = 4
            else: indent = 6

            from .UTILS import UTILS
            yaml = UTILS.ToYaml(raw, 
                indent=indent, maxLines=20)

        # If the YAML is a one liner, then add the type inline.
        if yaml.strip().count('\n') == 0:
            lines.append(f'[{type(arg).__name__}] {yaml.strip()}')

        # If the YAML has many lines, then add the type above.
        else: lines.append(f'    [{type(arg).__name__}]\n{yaml}')


    _printDepth = 0
    

    @classmethod
    def IsInLoop(cls):
        '''👉 Returns True if the Print is in a loop.'''
        return cls._printDepth > 1
    

    @classmethod
    def Print(cls, msg:any, *args):
        '''👉️ Adds the message to an array, and prints (.) only.'''
        cls._Debug(f'LOG.Print({msg})')

        if LOG.Settings().GetTestFast():
            return
            
        try:                 
            LOG._printDepth = LOG._printDepth+1
            if LOG._printDepth > 1:
                cls._Debug(f'LOG.Print: Loop detected, exiting...')
                #stack = traceback.format_stack()
                #for line in stack: print(line)
                return f'<IN LOOP> {msg}'
                raise Exception('Loop detected.')
            
            msg = cls.ReplaceCallable(msg)

            isLambda = cls.IsLambda()
            
            if not isLambda and type(msg) is not str:
                #raise Exception(f'msg should be a string, but found {msg=}')
                msg = f'{msg}'

            msg = cls.ReplacePlaceholders(msg, goUp=1)

            # Add the message to the log.
            cls._PrintInternal(isLambda, msg, args)
            return msg
        finally:
            LOG._printDepth = LOG._printDepth-1


    @classmethod    
    def ReplaceCallable(cls, 
        msg:any
    ):
        if not callable(msg):
            return msg
        
        from .PYTHON_METHOD import PYTHON_METHOD
        caller = PYTHON_METHOD(msg)
        icon = caller.GetIcon()
        name = caller.GetFullName()
        
        msg = f'{icon} {name}()'
        
        return msg
        

    @classmethod    
    def ReplacePlaceholders(cls, 
        msg:str,
        goUp:int=0
    ):
        
        # Look for the caller's reference.
        caller = None

        # If callable.
        if callable(msg):
            from .PYTHON_METHOD import PYTHON_METHOD 
            caller = PYTHON_METHOD(msg)
            msg = caller.GetFullName()
            return msg
        
        # If not callable.
        if '@' in str(msg):
            from .UTILS import UTILS
            caller = UTILS.GetCaller(goUp= goUp+1)

        # Try to replace the '@.*' with the caller's class icon.
        if str(msg).startswith('@'):
            icon = caller.GetIcon()
            msg = msg.replace('@', f'{icon} @')

        # Try to replace the '* @.*' with '* {caller's name}.*'
        if str(msg).endswith(' @'):
            msg = msg.replace(' @', 
                f' {caller.GetFullName()}()')
        elif ' @' in str(msg):
            msg = msg.replace(' @', 
                f' {caller.GetFullName()}')
            
        return msg


    @classmethod
    def _PrintInternal(cls, isLambda:bool, msg:str, *args):
        '''👉 Adds a message to the log.'''

        # Ignore duplicate of the last message.
        if msg == LOG._lastLog:
            if str(LOG._lastArgs) == str(args):
                cls._Debug(f'LOG.Print: same as last line')
                return
        
        LOG._lastLog = msg
        LOG._lastArgs = args
        
        cls._Debug(f'LOG._PrintInternal: {msg}')

        ## DELETE ME
        # if isLambda:
        # print(msg)
        # print(args)

        # ping only once in a while.
        if not isLambda and not LOG.Settings().GetWriteToConsole():
            LOG.Placeholder().Ping()

        # Exclude certain messages.
        if isLambda:
            if type(msg) is str:
                for exclude in LOG._excludesLambda:
                    if exclude in msg:
                        cls._Debug(f'LOG.Print: excluded line1')
                        return
        elif not isLambda:
            if type(msg) is str:
                for exclude in LOG._excludes:
                    if exclude in msg:
                        cls._Debug(f'LOG.Print: excluded line2')
                        return
                        
        # Add the args.
        lines:list[str] = []
        if args != None:
            
            # If it's a list in tuple, just break them.
            if len(args) == 1 and isinstance(args[0], tuple):
                args = args[0]

            if isLambda:
                # In Lambda, add the objects to print JSON.
                lines += args
            else:
                # In local, convert them to YAML.
                cls._PrintArg(arg=args, lines=lines)
            
        # Add a missing > to allow collapsing.
        if not isLambda:
            if len(lines) == 1 and not f'{lines[0]}'.strip().startswith('>'):
                lines = ['  > ' + f'{lines[0]}'.strip()]

        # Add the message.
        if type(msg) is str:
            log = f'{msg.lstrip()}'
        else:
            log = msg

        # Prepare the arguments.
        if not isLambda:
            lines = [l.rstrip() for l in lines if l.strip() != '']

        # Merge every 2 lines where #1 ends with =, and #2 is a single line.
        if not isLambda:
            previous:str = None
            for line in lines:

                if previous == None \
                or not previous.endswith('=') \
                or '\n' in line:
                
                    previous = line 
                    continue

                index= lines.index(previous)
                lines[index] = previous + line.replace(' > ','')
                lines.remove(line)

                if len(lines) > index+1:
                    previous = lines[index+1]
            

        # Remove (NoneType) when there's no = on the previous line.
        if not isLambda:
            previous:str = None
            for line in lines:

                if previous == None \
                or previous.endswith('=') \
                or not line.lstrip().startswith('(NoneType)'):
                
                    previous = line 
                    continue

                index= lines.index(previous)
                lines.remove(line)

                if len(lines) > index+1:
                    previous = lines[index+1]

        if LOG.Settings().GetWriteToConsole():
            if LOG.Settings().GetPingOnly():
                LOG.Placeholder().Ping()
            else:
                print(msg, flush=True)
                #for line in lines: print(f' > {line}')

        cls._Debug(f'LOG._PrintInternal2: {msg}')
        if isLambda:
            # For Lambda, print as json immediatly.
            # > CloudWatch N lines as N different messages.
            
            obj = { "Log": msg }
            if len(lines) > 0:
                obj["More"] = lines
            
            from .UTILS import UTILS
            logger.info(
                UTILS.ToJson(obj, indent=2))
            
        else:
            # For local tests, add the arguments and append to log.
            more = '\n'.join(lines)
            if more.strip() != '':
                log = f'{log}\n{more}'
            
            cls._Append(log)
            cls._Debug(f'LOG._PrintInternal2: {msg} {log}')

        # Add separator blank lines.
        cls._Append('')


    @classmethod 
    def RaiseException(cls, msg=None, *args):
        '''👉 Raises an exception.'''
    
        cls.PrintStack()
        
        e:Exception = None
        if msg == None: 
            msg = 'Exception'
        elif type(msg) is Exception:
            e = msg
        else:
            msg = cls.ReplacePlaceholders(msg, goUp=1)

        cls.Print(f'💥 {msg}', msg, args)

        if len(args) > 0:
            args = [x for x in args if isinstance(x,str)]
            out = f'💥 {msg}' + '\n'.join(args)
        else:
            out = f'💥 {msg}'
        
        if e != None:
            raise Exception(out) from e
        else:
            raise Exception(out)


    @classmethod 
    def RaiseValidationException(cls, msg:str=None, *args):
        '''👉 Raises a ValidationException.'''
        
        cls.PrintStack()

        if msg == None: msg = 'Exception'
        msg = cls.ReplacePlaceholders(msg, goUp=1)

        cls.Print(f'⛔ Validation Exception: {msg}', msg, args)

        from .TESTS import ValidationException
        if len(args) > 0:
            args = [
                str(x) for x in args 
                #if type(x) in [str,bool,int,float,tuple,list]
            ]

            # Merge the lines.
            txt = '\n'.join(args)

            # limit to N lines of text.
            N = 20
            if txt.count('\n') > N:
                txt = txt.split('\n')[:N]
                txt.append('...')
                txt = '\n'.join(txt)
            
            # raise the exception.
            raise ValidationException(f'⛔ {msg} {txt}')
        else:
            raise ValidationException(f'⛔ {msg}')
        

    @classmethod
    def RaiseUrlNotFoundException(cls, *args):
        '''👉 Raises an UrlNotFoundException.'''
        
        cls.PrintStack()
        cls.Print('⛔ UrlNotFound Exception', args)
        
        from .WEB_BASE import UrlNotFoundException
        if len(args) > 0:
            args = [x for x in args if isinstance(x,str)]
            raise UrlNotFoundException('\n'.join(args))
        else:
            raise UrlNotFoundException()
        

    @classmethod
    def RaiseAssertException(cls, *args):
        '''👉 Raises an AssertException.'''
        
        cls.PrintStack()
        cls.Print('⛔ Assert Exception', args)

        from .TESTS import AssertException
        import json
        if len(args) > 0:
            args = [
                json.dumps(x) 
                for x in args 
                #if isinstance(x,str)
            ]
            raise AssertException('\n'.join(args))
        else:
            raise AssertException()

    
    @classmethod
    def PrintException(cls, 
        exception:Exception,
        stackTrace:Union[str, list[str], None] = None
    ):
        '''👉️ Sets the status of the current task to FAILED.'''
        cls.Print(f'💥 Exception:', exception)
        cls.PrintStack(stackTrace)


    @classmethod 
    def PrintStack(cls, stack:Union[str, list[str], None]=None):
        '''👉 Prints the call stack.'''
        logs = cls.ParseStack(stack)
        cls._Append(logs)
    

    @classmethod 
    def ParseStack(cls, 
        stack:Union[str, list[str], None]=None,
        viewerDirPath:str=None,
    ):
        '''👉 Parses the call stack.
            * Returns a list of strings.
            * If stack is None, it uses the current stack.
            * If reverse is True, it reverses the stack.

        Arguments:
            * `stack` {list[str]} -- The stack to parse. (default: {None})
            * `reverse` {bool} -- If True, it reverses the stack. (default: {False})
        
        Usage:
            stack = traceback.format_stack()
            logs = LOG.ParseStack(stack)
            for log in logs: print(log)
        '''
        
        # If the stack is not given, use the current stack.
        if stack == None:
            stack = traceback.format_stack()
        elif isinstance(stack, str):
            stack = [stack]
        
        # Loop through the stack.
        ret = []
        for i in range(len(stack)):
            if i < 2:
                continue

            call = stack[i]
            #File "/Users/jorgemf/AWS/POLLYWEB/cdk-ts/python/pollyweb.source/utils/python/TESTS_TESTS.py", line 140, in _raiseValidationException
            #LOG.ValidationException()
            
            if '/Frameworks/Python.framework/Versions/' in call:
                continue

            # Remove the first part.
            parts = call.split('  File "')
            if len(parts) > 1: 
                call = parts[1]
        
            #python/pollyweb.source/utils/python/TESTS_TESTS.py", line 140, in _raiseValidationException
            #LOG.ValidationException()

            parts = call.split('", line ')
            file = parts[0]
            #python/pollyweb.source/utils/python/TESTS_TESTS.py
             
            if len(parts) > 1:
                parts = parts[1].split(', in ')
                number = parts[0]
                # 140

                # Identify the module.
                if len(parts) > 1:
                    parts = parts[1].split('\n')
                    module = parts[0]
                else:
                    module = '(module?)'
                
                # Identify the call.
                if len(parts)>1: call = parts[1].strip()
                else: call = ''

                # Remove the last (
                if call.endswith('('):
                    call = call[:-1]

                # Remove the last {
                if call.endswith('{'):
                    call = call[:-1]

            else:
                number = '???'
                #call = '???'
                module = '???'
            
            # Print the details.
            if not file.endswith('/LOG.py'):
                
                import os
                file = os.path.relpath(file, viewerDirPath) 
                file = '../../' + file

                ret.append(f'    module={module}, call={call}')
                ret.append(f'  > []({file}#L{number})')
                
        # Add a collapsable group.
        
        ret.append(f'\n📚 Stack ({len(stack)}):')
        
        #TODO: remove this - used because the stack is too long.
        #return []

        return ret


    @classmethod
    def DumpToFile(cls):
        '''👉 Dumps the logs to the LOG.md file.
            * Returns the file object.'''
        
        if cls.IsLambda():
            raise Exception('Cannot use DumpToFile() in Lambda.')
            
        cls.PARALLEL()._DumpToFile()
        cls.GetLogDir().Touch()
        return cls.Buffer().DumpToFile()
    

    _isLambda = None
    @classmethod
    def IsLambda(cls):
        '''👉 Returns True if the code is running in a Lambda.'''
        if cls._isLambda == None:
            import os
            cls._isLambda = 'AWS_EXECUTION_ENV' in os.environ
        return cls._isLambda


    @classmethod
    def _Append(cls, log:Union[str, list]):
        '''👉 Appends the log to the buffer.'''
        
        # Ignore if in Lambda.
        if cls.IsLambda(): return 

        cls.Buffer().Append(log)
        cls._AppendParallel(log)


    @classmethod
    def Delete(cls):
        '''👉 Deletes the LOG file and PARALLEL folder.'''
        cls.Buffer().Delete(reason='LOG.delete()')
        cls._DeleteParallel()
