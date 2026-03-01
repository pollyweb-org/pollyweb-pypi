# 📚 UTILS

from .FILESYSTEM_OBJECT import FILESYSTEM_OBJECT
import os

from .SETTINGS import SETTINGS


class FILE(FILESYSTEM_OBJECT):
    '''👉️ Wrapper for a file in the operating system.'''

    ICON = '📝'
    

    def __init__(self, name:str, dummy:str) -> None:
        '''👉️ Wrapper for a file in the operating system.'''    
        super().__init__(name)  

    
    def GetExtension(self):
        '''👉️ Returns the extension of the file name.'''
        file_name, file_extension = os.path.splitext(self.GetName())
        return file_extension


    def GetNameWithoutExtension(self):
        '''👉️ Returns the name with the extension.'''
        file_name, file_extension = os.path.splitext(self.GetName())
        if ':' in str(file_name):
            from .LOG import LOG
            LOG.RaiseException(f'Unexpected path containing json:', file_name)
        return file_name
    

    def Exists(self) -> bool:
        '''👉️ Indicates of the file path exists.'''
        return os.path.isfile(self.GetPath())
    

    def GetPath(self)->str:
        ''' 👉️ Get the path of the object.'''

        if not SETTINGS.ICONS_ENABLED:
            return self._path
        
        # Try to use the path in memory first.
        if os.path.isfile(self._path):
            return self._path
        
        # If not found, get the path from the uuid.
        from .FILESYSTEM import FILESYSTEM
        ret = FILESYSTEM.GetPathByUuid(self._uuid)
        
        # Update the path in memory.
        self._path = ret
        self._name = os.path.basename(ret)

        return ret
    

    def ReadText(self) -> str:
        '''👉️ Returns the string content of the file.'''
        from .LOG import LOG
        LOG.Print(self.ReadText, f'({self.GetPath()})', f'path={self.GetPath()}')
        
        self.AssertExists()
        f = open(self.GetPath(), "r")
        return f.read()


    def ReadLines(self) -> list[str]:
        '''👉️ Returns the lines of the file as a list of strings.'''
        f = open(self.GetPath(), "r")
        lines = f.readlines()
        return [
            line.replace('\n','').replace('\r','')
            for line in lines
        ]
    

    def ReadLogLines(self) -> list[str]:
        '''👉️ Returns the lines of the file as a list of strings, 
            reversed and without empty strings.
        
        Example:
            * ['\n', 'line1\n', 'line2\n', '\n'] -> ['line2', 'line1']
        '''
        self.AssertExists()
        from .UTILS import UTILS
        lines = self.ReadText().splitlines()
        reversedLines = UTILS.ReverseStrList(lines)
        logLines = UTILS.RemoveEmptyStrings(reversedLines)
        return logLines


    def ReadJson(self) -> any:
        '''👉️ Returns the object stored in a Json file.'''

        self.LOG().Print('📝 FILE.ReadJson()', f'path={self.GetPath()}')

        text = self.ReadText()
        obj = self.UTILS().FromJson(text)
        return obj
    

    def ReadYamlStruct(self):
        '''👉️ Returns as a STRUCT the object stored in a YAML file.'''

        self.LOG().Print('📝 FILE.ReadYamlStruct()')
        
        yaml = self.ReadYaml()
        from .STRUCT import STRUCT
        return STRUCT(yaml)

    
    def ReadYaml(self) -> any:
        '''👉️ Returns the object stored in a YAML file.'''

        self.LOG().Print(self.ReadYaml, f'path={self.GetPath()}')
        
        self.UTILS().AssertEqual(
            given= self.GetExtension(), 
            expect= '.yaml', 
            msg= f'Unexpected YAML extension on file `{self.GetPath()}`')

        self.AssertExists()
        text = self.ReadText()
        yaml = self.UTILS().FromYaml(text)
        return yaml
    

    def ReadPython(self):
        '''👉️ Returns a module from the python code in the file.
        * Source: https://stackoverflow.com/questions/27189044/import-with-dot-name-in-python
        '''
        
        from .UTILS import UTILS

        UTILS.AssertEqual(
            given= self.GetExtension(), 
            expect= '.py', 
            msg= f'Unexpected extension for File={self.RequirePath()}')
        
        path = self.RequirePath()
        
        import importlib.util 
        spec = importlib.util.spec_from_file_location(
            name= path, 
            location= path)
        
        my_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(my_module)

        return my_module
    

    def WriteText(self, content:str):
        '''👉️ Writes string content to the file.'''

        self.LOG().Print(self.WriteText, f'(path={self.GetPath()})')

        f = open(self.GetPath(), "w")
        f.write(content)
        return self
    

    def WriteJson(self, content:dict):
        '''👉️ Writes string content to the file.'''
        
        from .UTILS import UTILS
        from .STRUCT import STRUCT

        obj = STRUCT(content).Obj()
        json = UTILS.ToJson(obj, indent= 4)
        self.WriteText(json)
        return self


    def WriteYaml(self, content:dict):
        '''👉️ Writes string content to the file.'''
        if isinstance(content,type):
            self.LOG().RaiseException(f'Types are not allowed - pass a value! content={content}')
        
        yaml = self.UTILS().ToYaml(content)
        self.WriteText(yaml)
        return self
    

    def AppendLines(self, lines:list[str]) -> None:
        '''👉️ Appends string lines to the file.'''
        
        self.GetParentDir().AssertExists()
        path = self.GetPath()

        f = open(path, "a")
        lines2 = '\n'.join([
            str(line)
            for line in lines
        ])
        lines2 = '\n' + lines2 
        
        f.write(lines2)
        return self


    def WriteLines(self, lines:list[str]) -> None:
        '''👉️ Writes string lines to the file.'''
                    
        self.GetParentDir().AssertExists()
        path = self.GetPath()

        f = open(path, "w")
        lines2 = '\n'.join(lines)
        f.writelines(lines2)
        return self


    def Delete(self, reason:str=None, safe:bool=False):
        '''👉️ Deletes the file.'''

        path = self.GetPath()
        self.LOG().Print(
            f'📝 FILE.Delete({path=}, {reason=}, exists={os.path.isfile(path)})')

        if safe:
            if not self.Exists():
                return self
                    
        self.TESTS().AssertTrue(self.Exists())
        os.remove(path)
        self.TESTS().AssertFalse(self.Exists())

        self.LOG().Print(f'📝 FILE.Delete({path=}, exists={os.path.isfile(path)} (after))')
        return self
    

    def RequireExtension(self, extension:str):
        '''👉️ Raises an error if the file does not have the expected extension.'''
        
        # Ensure the extension has a dot.
        if '.' in extension:
            ext = extension 
        else:
            ext = '.' + extension

        # Check the extension.
        self.UTILS().AssertEqual(
            given= self.GetExtension(), 
            expect= ext,
            msg= f'Unexpected extension for File=`{self.RequirePath()}`')
        
        # Return the file.
        return self
        

    def Unzip(self, target:str=None):
        '''👉️ Unzips the file into a target directory.'''
        
        # Ensure the file exists.
        self.AssertExists()

        # Set the target directory if not set.
        if target is None:
            target = self.GetParentDir().GetPath()
        
        # Ensure the target directory exists.
        from .FILESYSTEM import FILESYSTEM
        target = FILESYSTEM.DIRECTORY(target).RequirePath()

        # Unzip the file.
        self.UTILS().Unzip(
            file= self.RequirePath(),
            into= target)
        

    def CopyTo(self, target:str):
        '''👉️ Copies the file to a target directory.'''

        from .FILESYSTEM import FILESYSTEM
        from .DIRECTORY import DIRECTORY

        # Ensure the file exists.
        self.AssertExists()

        # Ensure the target exists.
        self.UTILS().AssertIsType(target, [str, DIRECTORY], require=True)
        if self.UTILS().IsType(target, DIRECTORY):
            targetDir = target
        elif self.UTILS().IsString(target): 
            targetDir = FILESYSTEM.DIRECTORY(target)

        # Merge the target with the file name
        target = targetDir.RequirePath()
        target = os.path.join(target, self.GetName())

        # Copy the file.
        from shutil import copyfile
        copyfile(self.RequirePath(), target)
        return FILESYSTEM.FILE(target)


    def MoveTo(self, target:str):
        '''👉️ Moves the file to a target directory.'''
        copy = self.CopyTo(target)
        self.Delete()
        self._SetPath(copy.GetPath())


    def Touch(self):
        '''👉️ Creates an empty file, if necessary.'''
        if self.Exists():
            return self
        f = open(self.GetPath(), "w")
        f.close()
        return self
    

    def TextLenght(self):
        '''👉️ Returns the number of characters in the file.'''
        return len(self.ReadText())