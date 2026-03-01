from __future__ import annotations
from types import CodeType
from typing import Union
from .PRINTABLE import PRINTABLE


class PYTHON_METHOD(PRINTABLE):

    ICON= ' 🐍'
    

    def __init__(self, method:Union[CodeType, callable], cla=None) -> None:

        if isinstance(method, CodeType):
            self._InitCodeType(method, cla)

        elif callable(method):
            self._InitCallable(method)

        else:
            raise Exception(f'Invalid method type: {type(method).__name__}')

        self._InitRest()


    def _InitCodeType(self, method:CodeType, cla):
        
        self._type = 'CodeType'
        self._moduleName = ''
        self._providedClass = cla if isinstance(cla, type) else None

        # `co_qualname` is not available on older Python versions (e.g. 3.10).
        if hasattr(method, 'co_qualname'):
            self._qualName = method.co_qualname
        else:
            qualname = method.co_name
            frame_locals = getattr(cla, 'f_locals', None)
            frame_globals = getattr(cla, 'f_globals', None)

            if isinstance(cla, type):
                qualname = f'{cla.__name__}.{qualname}'
            elif isinstance(frame_locals, dict):
                inferred_class_name = None

                # Prefer exact code-object matching against classes in module globals.
                if isinstance(frame_globals, dict):
                    for global_value in frame_globals.values():
                        if not isinstance(global_value, type):
                            continue
                        candidate = getattr(global_value, method.co_name, None)
                        candidate = getattr(candidate, '__func__', candidate)
                        if getattr(candidate, '__code__', None) is method:
                            inferred_class_name = global_value.__name__
                            break

                self_obj = frame_locals.get('self')
                cls_obj = frame_locals.get('cls')

                if inferred_class_name is not None:
                    qualname = f'{inferred_class_name}.{qualname}'
                elif self_obj is not None:
                    qualname = f'{self_obj.__class__.__name__}.{qualname}'
                elif hasattr(cls_obj, '__name__'):
                    qualname = f'{cls_obj.__name__}.{qualname}'

            if isinstance(frame_globals, dict):
                self._moduleName = frame_globals.get('__name__', '') or ''

            self._qualName = qualname
        
        #from PYTHON_CLASS import PYTHON_CLASS
        #if cla.__name__ == 'frame':
        #    c = PYTHON_CLASS(method.co_qualname.split('.')[0])
        #else:
        #    c = PYTHON_CLASS(cla)
        #self._moduleName = c.GetModuleName()
        
        # If module name is empty, try to use the class name from qualname
        if not self._moduleName and self._qualName:
            # Extract the class name from qualified name (first part before '.')
            qual_parts = self._qualName.split('.')
            if qual_parts:
                self._moduleName = qual_parts[0]
        
        # remove the last part after split('.')
        all_parts = self._moduleName.split('.') if self._moduleName else ['']
        if len(all_parts) > 1:
            self._packageName = '.'.join(all_parts[:-1])
        else:
            self._packageName = ''  # Changed from all_parts[0] to avoid empty string package

        if self._moduleName == '.frame':
            if self._packageName and self._packageName != '?':
                self._moduleName = self._packageName + '.' + '.'.join(self._qualName.split('.')[:-1])
            else:
                self._moduleName = self._qualName

        if self._moduleName.endswith('.AssertName'):
            raise Exception(
                f'PYTHON_METHOD5: Invalid module name [{self._moduleName}]'
                f' on package [{self._packageName}].'
            )
            

    def _InitCallable(self, method:callable):
        self._type = 'callable'
        self._moduleName = method.__module__
        self._qualName = method.__qualname__
        self._callable = method
        self._providedClass = None  # No class provided for callable methods

        # remove the last part after split('.')
        all_parts = self._moduleName.split('.') if self._moduleName else ['']
        if len(all_parts) > 1:
            self._packageName = '.'.join(all_parts[:-1])
        else:
            self._packageName = ''
        
        #self._packageName = "TODO2"


    def _InitRest(self):
        parts = self._qualName.split('.')
        self._className = parts[0]
        self._methodName = parts[-1]

        if '?' in self._methodName:
            raise Exception(
                f'PYTHON_METHOD6: Invalid method name [{self._methodName}]'
                f' on class [{self._className}].'
            )
        
        self._parentMethodName = parts[1] if len(parts) > 1 else f'{{self._methodName}}'

        super().__init__(self.ToJson)


    def ToJson(self):
        return dict(
            FullName= self._qualName,
            ClassName= self._className)
    

    def GetModuleName(self):
        '''👉️ Returns the module name.'''
        return self._moduleName if self._moduleName else self.GetClassName()


    def GetType(self):
        '''👉️ Returns the type of the method.'''
        return self._type


    def GetQualName(self):
        '''👉️ Returns the qualified name of the method.'''
        return self._qualName
    

    def GetPackageName(self):
        if self._packageName == self._className:
            return ''
        return self._packageName


    def GetFullName(self):
        '''👉️ Returns the full name of a method.'''
        #return f'{self._qualName}'
        if self.GetClassName() != '?':
            return f'{self.GetClassName()}.{self.GetMethodName()}'
        return self.GetQualName()
    

    def GetFileName(self):
        ret = self._moduleName 
        # remove the package name if it exists
        if '.' in ret:
            ret = ret.split('.')[-1:][0]
        if not ret:
            return '?'
        ret = f'{ret}.py'
        return ret
    

    def IsLocal(self):
        '''👉️ Returns True if the method is inside another method.'''
        return self._qualName.split('.')[-2] == '<locals>'
    

    def GetClassName(self):
        '''👉️ Returns the class name.'''
        return self._className
    
    
    def GetMethodName(self):
        '''👉️ Returns the method name.'''
        return self._methodName


    def GetParentMethodName(self):
        '''👉️ Returns the parent method name.'''
        return self._parentMethodName
    

    _GetClassCache = {}
    def GetClass(self):
        '''👉️ Returns the class.'''

        if self._moduleName.startswith('?'):
            return None

        # Check if the class is already in the cache
        if self._className in PYTHON_METHOD._GetClassCache:
            return PYTHON_METHOD._GetClassCache[self._className]

        # If we have a provided class object (from CodeType initialization), use it directly
        if hasattr(self, '_providedClass') and self._providedClass is not None:
            # Skip frame classes as they cause issues in PYTHON_CLASS
            if hasattr(self._providedClass, '__name__') and self._providedClass.__name__ == 'frame':
                pass  # Fall through to normal import logic
            else:
                from .PYTHON_CLASS import PYTHON_CLASS
                ret = PYTHON_CLASS(self._providedClass)
                # Cache the class
                PYTHON_METHOD._GetClassCache[self._className] = ret
                return ret

        cls = globals().get(self.GetModuleName())
        
        if not cls:
            import importlib

            if False and 'FILESYSTEM_OBJECT' in self._moduleName:
                raise Exception(
                    f'PYTHON_METHOD: Cannot import class [{self.GetClassName()}] from package [{self.GetPackageName()}].'
                    f' This is likely due to a circular import issue.'
                )
            
            # Try different import strategies
            module = None
            last_error = None
            
            # Strategy 1: Absolute import with module name
            if self.GetModuleName() and self.GetModuleName() != '':
                try:
                    module = importlib.import_module(self.GetModuleName())
                except (ImportError, ModuleNotFoundError) as e:
                    last_error = e
            
            # Strategy 2: Import with package context if available
            if module is None and self.GetPackageName():
                try:
                    module = importlib.import_module(
                        self.GetModuleName(), 
                        package=self.GetPackageName())
                except (ImportError, ModuleNotFoundError, TypeError) as e:
                    last_error = e
            
            # Strategy 3: Try importing using just the class name as module with package context
            if module is None and self.GetClassName() != '?':
                try:
                    # First try with current package context
                    current_module = globals().get('__name__', '')
                    if current_module and '.' in current_module:
                        package_name = '.'.join(current_module.split('.')[:-1])
                        module_name = f"{package_name}.{self.GetClassName()}"
                        module = importlib.import_module(module_name)
                    else:
                        # Fallback to direct import
                        module = importlib.import_module(self.GetClassName())
                except (ImportError, ModuleNotFoundError) as e:
                    last_error = e
            
            # Strategy 4: Try using the common package pattern for this codebase
            if module is None and self.GetClassName() != '?':
                try:
                    # Try the pollyweb.org.utils pattern specifically
                    module_name = f"{self.GetClassName()}"
                    module = importlib.import_module(module_name)
                except (ImportError, ModuleNotFoundError) as e:
                    last_error = e
            
            # If all strategies failed, raise an exception
            if module is None:
                raise Exception(
                    f'PYTHON_METHOD3({self.GetType()}): Cannot import class [{self.GetClassName()}] from package [{self.GetPackageName()}] with module [{self.GetModuleName()}].'
                    f' Last error: {last_error}'
                ) from last_error
                
            cls = getattr(module, self._className, None)
        
        if not cls:
            raise Exception(
                f'Class [{self._className}] not found in module [{self._moduleName}].')

        from .PYTHON_CLASS import PYTHON_CLASS
        ret = PYTHON_CLASS(cls)

        # Cache the class
        PYTHON_METHOD._GetClassCache[self._className] = ret

        return ret
    

    def GetIcon(self):
        '''👉️ Returns the icon of the class.'''
        try:
            cls = self.GetClass()
            if cls:
                return cls.GetIcon(default='🐠')
        except Exception:
            # Caller/class inference can be incomplete on older Python runtimes.
            return None
        return None

    
    def InvokeWithMatchingArgs(
        self,
        args:Union[list, dict[str, any]],
        optional:list[str] = []
    ):
        '''👉️ Call a function with only the arguments that match the function's signature.
        
        Usage:
            ```python

            # Define a sample function with specific arguments
            def M(A, B=2):
                print(f"A = {A}, B = {B}")
                if A !=1 or B != 2:
                    raise Exception('Invalid arguments')

            # Successful calls
            UTILS.CallWithMatchingArgs(M, {'A': 1, 'B': 2})
            UTILS.CallWithMatchingArgs(M, {'A': 1})

            # Error calls
            UTILS.CallWithMatchingArgs(M, {'A': 1, 'C': 2})
            ```
        '''
        func = self._callable

        self.LOG().Print(f'@ func={func.__qualname__}', dict(
            func=func,
            args=args,
            optional=optional
        ))

        # Validate the input arguments
        from .UTILS import UTILS
        UTILS.AssertIsCallable(func, require=True)  
        UTILS.AssertIsAnyType(args, [list,dict], require=True)

        # Import the inspect module
        import inspect

        def check_for_kwargs(func):
            sig = inspect.signature(func)
            for name, param in sig.parameters.items():
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    return True
            return False
        
        def check_for_args(func):
            sig = inspect.signature(func)
            for name, param in sig.parameters.items():
                if param.kind == inspect.Parameter.VAR_POSITIONAL:
                    return True
            return False

        # Get the signature of the function
        sig = inspect.signature(func)
        
        # Get the set of valid parameter names from the function
        valid_params = set(sig.parameters)
        
        # if a list was given, just call the function with the list.
        if UTILS.IsType(args, list):

            if check_for_args(func):
                return func(*args)
        
            if len(valid_params) != len(args):
                raise Exception(
                    f'Invalid number of arguments: {len(args)} when calling function {func.__name__}.'
                    f' Expected number of arguments: {len(valid_params)}.'
                    f' Valid keys are: {list(valid_params)}.'
                    f' Provided values are: {args}.')
            return func(*args)
        
        # if a dictionary was given, filter the dictionary to include only valid parameters
        if check_for_kwargs(func):
            return func(**args)
        
        if check_for_args(func):
            return func(*args.values())
        
        # Get the set of keys provided in the args_dict
        provided_keys = set(args.keys())
        
        # Find any keys in args_dict that are not valid parameters
        invalid_keys = provided_keys - valid_params

        # Ignore optional key.
        for key in optional:
            if key in invalid_keys:
                invalid_keys.remove(key)
        
        # Raise an error if there are any invalid keys
        if invalid_keys:
            self.LOG().RaiseValidationException(
                f'Invalid keys in arguments: {invalid_keys}'
                f' when calling function {func.__qualname__}.'
                f' Valid keys are: {list(valid_params)}.', 
                f'{args=}', 
                f'{func.__qualname__=}', 
                f'{valid_params=}', 
                f'{invalid_keys=}', 
                f'{provided_keys=}', 
                f'{check_for_args(func=func)=}',
                f'{check_for_kwargs(func=func)=}',)

        # Filter the dictionary to include only keys that are valid function parameters
        filtered_args = {
            k: v 
            for k, v 
            in args.items() 
            if k in valid_params
        }
        
        # Call the function with the filtered arguments
        return func(**filtered_args)
    

    def HasParameter(self, name:str):
        '''👉️ Returns True if the method has the given argument.'''
        
        import inspect
        sig = inspect.signature(self._callable)
        return name in sig.parameters.keys()
