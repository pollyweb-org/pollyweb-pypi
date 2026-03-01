from typing import Union
from .PRINTABLE import PRINTABLE


class PYTHON_CLASS(PRINTABLE):
    
    ICON= ' 🐍'
    

    def __init__(self, class_:Union[str, type], checkType:str=None) -> None:
        
        if isinstance(class_, str):
            if checkType and checkType != 'str':
                raise Exception(f'Invalid class type: {type(class_)}, expected str.')
            self._type = 'str'

            if '.' in class_:
                # If the class name contains a dot, it is a module path
                import importlib
                self._module = '.'.join(class_.split('.')[:-1])
                self._class_name = class_.split('.')[-1]
                
                try:
                    mod = importlib.import_module(self._module)
                    self._class = getattr(mod, self._class_name)
                except AttributeError:
                    mod = importlib.import_module(self._module + '.' + self._class_name)
                    self._class = getattr(mod, self._class_name)

                    #raise Exception(f'Class {self._class_name} not found in module {self._module}.')

                self._name = self._class_name
                if self._class == None:
                    raise Exception(f'class {self._name} not found.')
                
            else:
                self._name = class_
                self._class = globals().get(class_)
                if self._class == None:
                    raise Exception(f'class {self._name} not found.')
        
            
        elif isinstance(class_, type):
            if checkType and checkType != 'type':
                raise Exception(f'Invalid class type: {type(class_)}, expected type.')
            self._type = 'type'

            if class_.__name__ == 'frame':
                raise Exception(f'Invalid class name [{class_.__name__}] in type [{self._type}].')

            self._name = class_.__name__
            self._module = '.'.join(class_.__module__.split('.')[:-1])
            self._class = class_

        else:
            if checkType and checkType != 'other':
                raise Exception(f'Invalid class type: {type(class_)}, expected other.')
            self._type = 'other'
            
            class_ = type(class_)
            self._module = '.'.join(class_.__module__.split('.')[:-1])
            self._name = class_.__name__
            self._class = class_
            #raise Exception(f'Invalid class type: {type(class_)}')

        if self._class == None:
            raise Exception(f'class {self._name} not found.')
        
        if self._name == 'frame':
                raise Exception(f'Invalid class name [{self._name}] in type [{self._type}].')    

        super().__init__(self.ToJson)


    def ToJson(self):
        '''👉️ Return the JSON representation of the object.'''
        return dict(
            Name= self._name,
            Icon= self.GetIcon())


    def HasAttribute(self, name:str) -> bool:
        '''👉️ Returns True if the class has the attribute.'''
        return hasattr(self._class, name)
    

    def GetAttribute(self, name:str, default:str=None) -> any:
        '''👉️ Returns the attribute of the class.'''
        if hasattr(self._class, name):
            return getattr(self._class, name)
        return default
    

    def RequireAttribute(self, name:str) -> any:
        '''👉️ Returns the attribute of the class or raises an exception.'''
        if hasattr(self._class, name):
            return getattr(self._class, name)
        
        self.LOG().RaiseValidationException(f'{self._name}.{name} not found.')
    

    def GetIcon(self, default:str=None) -> str:
        '''👉️ Returns the icon of the class.'''
        return self.GetAttribute('ICON', default=default)
    

    def RequireIcon(self) -> str:
        '''👉️ Returns the icon of the class or raises an exception.'''
        return self.RequireAttribute('ICON')
    

    def GetName(self) -> str:
        '''👉️ Returns the name of the class.'''
        return self._name
    

    def GetModuleName(self) -> str:
        '''👉️ Returns the module name of the class.'''
        ret = self._module + '.' + self._name if hasattr(self, '_module') else self._name
        
        #remove the initial dot, if there is one
        if ret.startswith('.'):
            ret = ret[1:]

        return ret
    

    def HasMethod(self, name:str) -> bool:
        '''👉️ Returns True if the class has the method.'''
        return hasattr(self._class, name)
    

    def GetFile(self):    
        '''👉️ Returns the file of the class.'''
        import inspect
        file_path = inspect.getfile(self._class)
        from .FILESYSTEM import FILESYSTEM 
        return FILESYSTEM.FILE(file_path)


    def GetDirectory(self):
        '''👉️ Returns the directory of the class.'''
        return self.GetFile().GetParentDir()
    

    def GetType(self) -> str:   
        '''👉️ Returns the type of the class.'''
        return self._type
