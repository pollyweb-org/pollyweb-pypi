# 📚 UTILS

from __future__ import annotations
import os
from typing import Union
from .FILESYSTEM_OBJECT import FILESYSTEM_OBJECT
from .FILESYSTEM import FILESYSTEM
from .LOG import LOG
from .SETTINGS import SETTINGS


class DIRECTORY(FILESYSTEM_OBJECT):
    '''👉️ Wrapper for a directory in the operating system.'''

    ICON= '📂'

    
    def __init__(self, name:Union[str, "DIRECTORY"], dummy:str) -> None:
        '''👉️ Wrapper for a directory in the operating system.
        
        Arguments:
        - name: The name of the directory, or a DIRECTORY object.
        - dummy: A dummy argument to avoid creating directories by mistake.
        '''
        
        from .UTILS import UTILS
        UTILS.AssertIsAnyType(name, [str, DIRECTORY], require=True)

        super().__init__(name)

        self.RetainOnFailure = False
        self.Retain = False


    def __enter__(self) -> DIRECTORY:
        '''👉️ Enters the context.'''
        self.DeleteTree(safe=True)
        return self
    

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        '''👉️ Exits the context.'''
        if exc_type and self.RetainOnFailure: pass
        elif self.Retain: pass
        else: 
            self.DeleteTree(safe=True)
            pass
   

    def Exists(self) -> bool:
        '''👉️ Indicates of the directory path exists.'''
        return os.path.isdir(self.GetPath())
        
    
    def GetPath(self)->str:
        ''' 👉️ Get the path of the object.'''
        
        if not SETTINGS.ICONS_ENABLED:
            return self._path

        # Try to use the path in memory first.
        if os.path.isdir(self._path):
            return self._path
        
        # If not found, get the path from the uuid.
        from .FILESYSTEM import FILESYSTEM
        ret = FILESYSTEM.GetPathByUuid(self._uuid)
        
        # Update the path in memory.
        self._path = ret
        self._name = os.path.basename(ret)

        return ret
    
    
    def ChangeTo(self) -> None:
        '''👉️ Performs a CD to the directory.'''
        LOG.Print(f'📂 DIRECTORY.ChangeTo() -> {self.GetPath()}')
        # disable this, because is messing with the location of test files.
        # with the new multi-file log approach, this isn't necessary anymore.
        #os.chdir(self.GetPath())
        return self
    
    
    def GetSubDir(self, 
        name:str
    ):
        '''👉️ Returns a SUBDIRECTORY for the name.'''
        
        from .UTILS import UTILS
        UTILS.RequireArgs([name])

        if name.startswith('/'):
            LOG.RaiseException(f'Subdirs cannot start with /. Name={name}')

        # Search for the exact directory.
        path = os.path.join(self.GetPath(), name)
        return FILESYSTEM.DIRECTORY(path)


    def GetSubDirNames(self) -> list[str]:
        '''👉️ Returns the names of the subdirectories.'''
        ret = []
        for d in self.GetSubDirs():
            ret.append(d.GetName())
        return sorted(ret)


    def GetSubDirs(self) -> list[DIRECTORY]:
        '''👉️ Returns the subdirectories.'''
        ret:list[DIRECTORY] = []
        dir = self.RequirePath()
        for name in os.listdir(dir):
            path = os.path.join(dir, name)
            if os.path.isdir(path):
                ret.append(FILESYSTEM.DIRECTORY(path))
        return ret


    def GetDeepDirs(self, name:str=None) -> list[DIRECTORY]:
        '''👉️ Recursively returns all the directories in the dir and all the subdirectories.'''
        ret:list[DIRECTORY] = []

        # Add the top level directories.    
        for d in self.GetSubDirs():
            if name is None or d.GetName() == name:
                ret.append(d)

        # Add the subdirectories.
        for d in self.GetSubDirs():
            dirs = d.GetDeepDirs(name= name)
            ret.extend(dirs)
        
        # Sort by path.
        ret.sort(key=lambda d: d.GetPath())

        # Return the result.
        return ret        


    def GetDeepFiles(self, 
        endsWith:str=None,
        maxFiles:int=None
    ):
        '''👉️ Returns all the files in the dir and all the subdirectories.'''
        LOG.Print(self.GetDeepFiles, dict(endsWith=endsWith), self)
        
        from .FILE import  FILE
        ret:list[FILE] = []
        
        # Add the top level files.
        files = self.GetFiles(endsWith=endsWith)
        ret.extend(files)

        # Limit the number of files.
        if maxFiles is not None and len(ret) >= maxFiles:
            return ret

        # Add the subdirectories.
        for d in self.GetDeepDirs():
            files = d.GetFiles(endsWith= endsWith)
            ret.extend(files)        

        # Sort by path.
        ret.sort(key=lambda f: f.GetPath())

        # Return the result.
        return ret


    def GetFilePaths(self, endsWith:str=None) -> list[str]:
        '''👉️ Returns the names of the files in the dir.'''
        
        ret:list[str] = []

        dir = self.RequirePath()
        for file in os.listdir(dir):
            path = os.path.join(dir, file)
            if not os.path.isdir(path):
                if endsWith is None or path.endswith(endsWith):
                    ret.append(path)

        ret.sort()
        return ret
    

    def GetFileNames(self, endsWith:str=None):
        '''👉️ Returns the files in the dir.'''
        
        ret:list[str] = []

        for file in self.GetFiles(endsWith=endsWith):
            ret.append(file.GetName())

        ret.sort()
        return ret


    def GetFiles(self, endsWith:str=None):
        '''👉️ Returns the files in the dir.'''
        
        from .FILE import  FILE
        ret:list[FILE] = []

        for path in self.GetFilePaths(endsWith=endsWith):
            ret.append(FILESYSTEM.FILE(path))

        return ret
    

    def GetObjects(self, endsWith:str=None):
        '''👉️ Returns the files and subdirs in the dir.'''
        
        ret:list[FILESYSTEM_OBJECT] = []

        for file in self.GetFiles(endsWith=endsWith):
            ret.append(file)

        for dir in self.GetSubDirs():
            ret.append(dir)

        return ret


    def RequireFile(self, name:str):
        '''👉️ Returns a FILE for the name.
        * Raises an error if not found.'''
        
        file = self.GetFile(name)
        if not file.Exists():
            
            alternatives = '\n'.join([
                f'  - {a}'
                for a in self.GetFileNames()
            ])

            LOG.RaiseValidationException(
                f'File not found:'
                f'\n * Name:\n    {file.GetName()}',
                f'\n * Path:\n    {file.GetPath()}',
                f'\n * Alternatives: ', alternatives)
            
        return file


    def ContainsFile(self, name:str) -> bool:
        return self.GetFile(name).Exists()


    def GetFile(self, name:str):
        '''👉️ Returns a FILE for the name.'''
        
        LOG.Print(f'@({name})', 
            f'{name=}', f'{self.GetPath()=}')
        
        from .UTILS import UTILS
        UTILS.AssertIsStr(name, require=True)

        self.AssertExists()
            
        # Search for the exact file.
        path = self.GetPath()
        path = os.path.join(path, name)

        return FILESYSTEM.FILE(path)
    
    
    def Touch(self) -> DIRECTORY:
        '''👉️ Creates the dir, if necessary.'''
        LOG.Print(f'@({self.GetPath()})', self)
        self.GetParentDir().AssertExists()
        if not self.Exists():
            os.makedirs(name=self.GetPath(), exist_ok=True)
        return self
    

    def AssertExists(self) -> DIRECTORY:
        '''👉️ Raises an error if the directory does not exist.'''
        if not self.Exists():
            alternatives = ['x']
            
            try:
                parent = self.GetParentDir()
                if parent.Exists():
                    alternatives = parent.GetSubDirNames()
                else:
                    alternatives = ['no parent!']
            except:
                pass

            LOG.RaiseValidationException(
                f'Directory does not exist: '
                f'\n Target: {self.GetPath()}'
                f'\n Alternative: {alternatives}')
            
        return self
    

    def DeleteTree(self, safe:bool=False):
        '''👉️ Deletes the directory and all its contents.'''
        LOG.Print(self.DeleteTree, self)

        if safe and not self.Exists():
            return self
        
        self.Delete(recursive=True)
        return self


    def Delete(self, recursive:bool=False):
        '''👉️ Deletes the directory if it exists.'''

        LOG.Print(self.Delete, self)

        if not self.Exists():
            return  self
        
        if recursive:
            #for file in self.GetDeepFiles():
            #    file.Delete()
            import shutil
            shutil.rmtree(self.GetPath())
        else:
            os.rmdir(self.GetPath())

        return self


    def Clean(self, selfIncluded:bool=False) -> DIRECTORY:
        '''👉️ Empties the content of the directy.'''

        LOG.Print(f'📂 DIRECTORY.Clean({self.GetName()})', self)

        # delete all subfolders
        subfolders = self.GetSubDirs()
        LOG.Print(f'📂 DIRECTORY.Clean: {len(subfolders)=}', self)
        for d in subfolders:
            d.Clean(selfIncluded=True)

        # delete all files.
        files = self.GetFiles()
        LOG.Print(f'📂 DIRECTORY.Clean: {len(files)=} (before)', self)
        for f in files:
            f.Delete()
        files = self.GetFiles()
        LOG.Print(f'📂 DIRECTORY.Clean: {len(files)=} (after)', self)
        
        # delete self.
        if selfIncluded:
            self.Delete()


    @staticmethod
    def GetCurrent() -> DIRECTORY:
        '''👉️ Returns the current directory.'''
        path = os.getcwd()
        return FILESYSTEM.DIRECTORY(path)
    

    def FindSubDirectory(self, name:str) -> DIRECTORY:
        '''👉️ Returns the directory with the name in the directory.
        * Raises an error if not found'''
        
        LOG.Print(self.FindSubDirectory, f'{name=}')

        found = self._FindSubDirectory(name)
        if not found:
            LOG.RaiseValidationException(
                f'Directory [{name}] not found in: {self.GetPath()}')
        return found
    

    def _FindSubDirectory(self, name:str) -> DIRECTORY:
        '''👉️ Returns the directory with the name in the directory.'''
        
        # Search at top level.
        for d in self.GetSubDirs():
            if d.GetName() == name:
                return d
        
        # Search within each child directory.
        for d in self.GetSubDirs():
            found = d._FindSubDirectory(name=name)
            if found:
                return found
            
        # Not found.
        return None
    

    def Zip(self):
        '''👉️ Zips the directory.'''

        LOG.Print(self.Zip, self)

        import zipfile
        import io
        
        path = self.GetPath()

        # Create a BytesIO object to hold the zipped bytes
        buffer = io.BytesIO()
        
        # Create a ZipFile object with the BytesIO object as its file
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

            # Walk through the directory
            for root, dirs, files in os.walk(path):
                for file in files:
                    # Create the full path to the file
                    file_path = os.path.join(root, file)
                    # Write the file to the zip archive
                    # arcname is the name within the zip file
                    zip_file.write(file_path, arcname=os.path.relpath(file_path, start=path))
        
        # Seek to the beginning of the BytesIO buffer
        buffer.seek(0)
        
        # Return the bytes containing the zipped file
        bytes = buffer.getvalue()

        from .ZIP import ZIP
        return ZIP(bytes, directory=self)
        

    def ContainsDirectory(self, name:str) -> bool:
        '''👉️ Returns True if the directory contains a subdirectory with the name.'''
        for d in self.GetSubDirs():
            if d.GetName() == name:
                return True
        return False
    

    def GetFileIconned(self, name:str):
        '''👉️ Returns a FILE for the name'''
        LOG.Print(f'📂 DIRECTORY.GetFileIconned({name})', f'{name=}', self)

        # Check if any similar file exists with the same or diferent icon.
        file = self.GetFile(name)
        if file.Exists():
            return file
        
        # Search for a file that contains the name.
        from .FILE import  FILE
        options:list[FILE] = []
        for f in self.GetFiles():
            if name in f'{f.GetSimpleName()}{f.GetExtension()}':
                options.append(f)

        # Return the result if it's 1 and only 1 file.
        if len(options) == 1:
            return options[0]
        
        # Return the original path if none is found in options.
        elif len(options) == 0:
            return file
        
        # Raise an exception if multiple files are found.
        else:
            LOG.RaiseException(
                f'Multiple files found for [{name}]: {options}')
    

    def GetSubDirIconned(self, 
        name:str
    ) -> DIRECTORY:
        '''👉️ Returns a SUBDIRECTORY for the name.'''

        LOG.Print(f'📂 DIRECTORY.GetSubDirIconned({name})', f'{name=}', self)
        
        dir = self.GetSubDir(name)
        if dir.Exists():
            LOG.Print(f'📂 DIRECTORY.GetSubDirIconned[{name}]: exists')
            return dir

        # Search for a directory that contains the name.
        options = []
        for d in self.GetSubDirs():
            if d.GetSimpleName() in name:
                options.append(d)
            else:
                LOG.Print(
                    f'📂 DIRECTORY.GetSubDirIconned[{name}]: '
                    f'\n `{name}` not in `{d.GetSimpleName()}`')

        # Return the result if it's 1 and only 1 directory.
        if len(options) == 1:
            LOG.Print(f'📂 DIRECTORY.GetSubDirIconned[{name}]: found alternative: {options[0]}')
            return options[0]
        
        # Return the original path if none is found in options.
        elif len(options) == 0:
            LOG.Print(
                f'📂 DIRECTORY.GetSubDirIconned[{name}]:'
                f'\n no alternative found'
                f'\n only: {self.GetSubDirNames()}'
                f'\n returning the original')
            return dir
        
        # Raise an exception if multiple directories are found.
        else:
            LOG.RaiseException(
                f'Multiple directories found for [{name}]: {options}')
    
    
    def IsProjectRoot(self) -> bool:
        '''👉️ Returns True if the directory is the project root.'''

        LOG.Print(f'📂 DIRECTORY.IsProjectRoot({self.GetPath()})')
        
        if not self.Exists():
            return False
        
        # Get the subdirectories (don't call GetSubDirNames())
        subDirs = []
        for name in os.listdir(self.GetPath()):
            path = os.path.join(self.GetPath(), name)
            if os.path.isdir(path):
                subDirs.append(name)
        
        if 'python' in subDirs \
        and 'tests' in subDirs \
        and 'stacks' in subDirs:
            return True
        
        return False
    

    def MoveTo(self, target:str):
        '''👉️ Moves the directory to a target directory.'''
        
        LOG.Print(f'📂 DIRECTORY.MoveTo({target})', self)

        # Ensure the target exists.
        from .FILESYSTEM import FILESYSTEM
        from .UTILS import UTILS
        UTILS.AssertIsType(target, [str, DIRECTORY], require=True)
        if UTILS.IsType(target, DIRECTORY):
            target = target.RequirePath()
        elif UTILS.IsString(target): 
            target = FILESYSTEM.DIRECTORY(target).RequirePath()

        # Merge the target with the file name
        target = os.path.join(target, self.GetName())

        # Move the directory.
        os.rename(self.GetPath(), target)

        self._SetPath(target)


    def IsEmpty(self) -> bool:
        '''👉️ Returns True if the directory is empty.'''
        return len(os.listdir(self.GetPath())) == 0
    

    def DeleteIfEmpty(self):
        '''👉️ Deletes the directory if it is empty.'''
        if self.Exists() and self.IsEmpty():
            self.Delete()
        return self
    

    def CopyContentTo(self, dir:DIRECTORY):
        '''👉️ Copies the content of the directory to another directory.'''
        LOG.Print(f'@', self, dir)

        from .UTILS import UTILS
        UTILS.AssertIsType(dir, DIRECTORY, require=True)
        
        import shutil
        def copy_content(src, dst):
            # Check if the destination directory exists, create if not
            if not os.path.exists(dst):
                os.makedirs(dst)
            
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(dst, item)
                if os.path.isdir(s):
                    # Recursively copy a directory
                    if not os.path.exists(d):
                        os.makedirs(d)
                    copy_content(s, d)
                else:
                    # Copy files using copy2 to preserve metadata
                    shutil.copy2(s, d)

        copy_content(
            src= self._path, 
            dst= dir._path)
        

    @staticmethod
    def GetTempDir():
        '''👉️ Returns a temporary directory.'''
        from .UTILS import UTILS
        uuid = UTILS.UUID()
        base = LOG.GetLogDir().GetSubDir('DIRECTORY').Touch()
        dir = base.GetSubDir(uuid).Touch()
        return dir
