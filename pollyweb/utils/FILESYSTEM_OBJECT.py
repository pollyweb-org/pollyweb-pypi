from __future__ import annotations
import os
from typing import Union
from .PRINTABLE import PRINTABLE


class FILESYSTEM_OBJECT(PRINTABLE):

    ICON = '📂'


    def __init__(self, name:Union[str, "FILESYSTEM_OBJECT"]) -> None:

        from .UTILS import UTILS
        UTILS.AssertIsAnyType(name, 
            options= [str, FILESYSTEM_OBJECT], 
            require=True)

        if isinstance(name, FILESYSTEM_OBJECT):
            name = name.GetPath()

        self._uuid = UTILS.UUID()
        self._name = os.path.basename(name)

        # Use expanduser to expand the home directory shortcut
        if name.startswith('~'):
            name = os.path.expanduser(name)
        # Set the path.
        self._path = os.path.abspath(name)

        # Set the string representation.
        super().__init__(toJson= self.ToJson)

        return
    

    def ToJson(self):   
        return self._name
       

    def Exists(self) -> bool:
        '''👉️ Indicates if the object path exists.'''
        self.LOG().RaiseException('@ Implement Exists() in the subclass.')


    def AssertExists(self):
        '''👉️ Raises an error if the file does not exist.'''
        if not self.Exists():
            self.LOG().RaiseValidationException(f'@: Path does not exist: {self.GetPath()}')
        return self


    def Touch(self) -> FILESYSTEM_OBJECT:
        '''👉️ Creates the object if it does not exist.'''
        self.LOG().RaiseException('@: Implement Touch() in the subclass.')


    def GetParentDir(self):
        '''👉️ Returns the parent directory.'''
        path = self.GetPath()
        parent = os.path.dirname(path)
        from .FILESYSTEM import FILESYSTEM
        return FILESYSTEM.DIRECTORY(parent)
    

    def GetName(self):
        '''👉️ Returns the base name of the file.'''
        path = self.GetPath()
        name = os.path.basename(path)
        return name
    

    def AssertName(self, name:str):
        '''👉️ Raises an error if the name is not the same.'''
        if self.GetName() != name:
            self.LOG().RaiseValidationException(f'@: Object name should be [{name}].', self) 
        return self
    

    def AssertSimpleName(self, name:str):
        '''👉️ Raises an error if the name is not the same.'''
        if self.GetSimpleName() != name:
            self.LOG().RaiseValidationException(f'@: Object name should be [{name}].', self) 
        return self


    def RequirePath(self) -> str:
        '''👉️ Returns the full path of the object.
            * raises an error if it does not exist.'''
        self.AssertExists()
        return self.GetPath()
    

    def _SetPath(self, path:str):
        '''👉️ Sets the path of the object.'''
        self._path = path
        self._name = os.path.basename(path)
        return self


    def GetPath(self)->str:
        ''' 👉️ Get the path of the object.'''
        self.LOG().RaiseException(
            '@: Implement GetPath() in the subclass.')
    

    def Rename(self, new_name:str):
        '''👉️ Renames the object.'''

        self.LOG().Print(
            f'@({new_name})', f'{new_name=}', self)

        from .FILESYSTEM import FILESYSTEM
        FILESYSTEM.Rename(self, new_name)
        return self
    


    # =================================
    # ICONS
    # =================================


    def GetIconName(self):
        icon = self.GetIcon()
        if icon == '🟢':
            return 'DONE'
        if icon == '🔴':
            return 'FAILED'
        if icon == '🟡':
            return 'RUNNING'
        if icon == '🔵':
            return 'PENDING'
        return None
            

    def GetIcon(self):
        '''👉️ Returns the icon from the object's name.
        
        Directory Examples:
            * stack -> None
            * 🧱 Starting -> 🧱
            * Ending 🐍 -> 🐍
            * Between 🧪 Words -> None

        File Examples:
            * stack.yaml -> None
            * 🧱 Starting.yaml -> 🧱
            * Ending 🐍.yaml -> 🐍
            * Between 🧪 Words.yaml -> None
        '''

        # Get the name without the extension.
        name = self.GetNameWithoutExtension()
        from .UTILS import UTILS
        return UTILS.GetEmojiInName(name)
        

    def GetNameWithoutExtension(self):
        return self.GetName()
    
    
    def GetSimpleName(self):
        '''👉️ Returns the name without icon.'''
        '''👉️ Returns the name without icon and extension.
        
        Example:
        * stack.yaml -> stack
        * 🧱 Starting.yaml -> Starting
        * Ending 🐍.yaml -> Ending
        * 🧪 Two Words.yaml -> Two Words
        '''
        name = self.GetNameWithoutExtension()
        icon = self.GetIcon()
        if icon:
            name = name.replace(f'{icon}', '')
        return name.strip()


    def GetNameWithoutIcon(self):
        '''👉️ Returns the name without icon.'''

        # Calculate the name.
        name = self.GetName()
        icon = self.GetIcon()
        if icon:
            name = name.replace(f'{icon}', '')
        name = name.strip()

        return name
    

    def AssertNameWithoutIcon(self, name:str):
        '''👉️ Raises an error if the name is not the same.'''
        withoutIcon = self.GetNameWithoutIcon()
        if withoutIcon != name:
            self.LOG().RaiseValidationException(f'@: Object name should be [{name}].', self) 
        return self


    def AssertSimpleName(self, name:str):
        '''👉️ Raises an error if the name is not the same.'''
        simple = self.GetSimpleName()

        if simple != name \
        and f'{simple}' != name:
            
            self.LOG().RaiseValidationException(
                f'@" Object simple name should be "{name}", '
                f'but found "{simple}"', self) 
            
        return self


    def SetIcon(self, newIcon:str):
        '''👉️ Sets the icon for the object.'''
        
        from .UTILS import UTILS
        
        self.LOG().Print(
            f'@({newIcon}) in {self.GetName()}', 
            f'{newIcon=}', self)
        
        UTILS.RequireArgs([newIcon])
        self.AssertExists()
        
        # Ignore if the icon is already set.
        if self.GetIcon() == newIcon:
            self.LOG().Print(self.SetIcon, f': icon is already {newIcon=}')
            return self

        nameWithoutIcon = self.GetNameWithoutIcon()

        # Don't allow changes to the PARALLEL directory.
        if nameWithoutIcon == 'PARALLEL':    
            self.LOG().RaiseException(f'@: to avoid bugs, setting an icon on PARALLEL directory is not allowed.')
          
        oldPath = self.GetPath()
        newPath = f'{newIcon} {nameWithoutIcon}'
        self.Rename(newPath)

        if os.path.exists(oldPath):
            self.LOG().RaiseException(
                f'Failed to rename '
                f'\n from: {oldPath}'
                f'\n   to: {newPath}')

        # Confirm.
        UTILS.AssertEqual(
            self.GetIcon(), newIcon,
            msg= f'Failed to set icon to {newIcon} on {self.GetName()}.')

        return self
    

    def SetPending(self):
        '''👉️ Sets the status to pending.'''
        self.LOG().Print(self.SetPending, self)
        if self.GetIcon() == None:
            self.SetIcon('🔵')
        return self
    

    def SetRunning(self):
        '''👉️ Sets the status to running.'''
        self.LOG().Print(self.SetRunning, f'([{self.GetName()}])', self)
            
        if self.GetSimpleName() == 'PARALLEL':
            self.LOG().RaiseException(
                f'Setting PARALLEL directory to running is not allowed.')

        if self.GetIcon() not in ['🟢', '🔴']:
            self.SetIcon('🟡')

        return self

    
    def SetDone(self, icon:str='🟢'):
        '''👉️ Sets the status to success.'''
        
        self.LOG().Print(self.SetDone, f'({self.GetName()})', self)

        currentIcon = self.GetIcon()

        if currentIcon == icon:
            self.LOG().Print(self.SetDone, f': icon already set', self)
            return 
        
        if currentIcon == '🔴':
            self.LOG().Print(self.SetDone, f': icon already failed 🔴', self)
            return
        
        self.SetIcon(icon)

        # Clean up running logs.
        nameWithoutIcon = self.GetNameWithoutIcon()
        for file in self.GetParentDir().GetFiles(endsWith= f'{nameWithoutIcon}'):
            if False and file.GetIcon() == '🔵':
                file.Delete()

        return self
        

    def SetFailed(self):
        '''👉️ Sets the status to failed.'''
        self.LOG().Print(self.SetFailed, self)
        self.SetIcon('🔴')
        return self
    

    def SetStatus(self, status:str):
        '''👉️ Sets the status of the object.'''
        if status == 'PENDING':
            self.SetPending()
        elif status == 'RUNNING':
            self.SetRunning()
        elif status == 'DONE':
            self.SetDone()
        elif status == 'FAILED':
            self.SetFailed()
        else:
            self.LOG().RaiseException(f'Unknown status: {status}')
        return self


    def IsFailed(self) -> bool:
        '''👉️ Returns True if the object is failed.'''
        return self.GetIcon() == '🔴'


    def IsDone(self) -> bool:
        '''👉️ Returns True if the object is done.'''
        return self.GetIcon() == '🟢'
    

    def MoveTo(self, target:str):
        '''👉️ Moves the object to a target directory.'''
        self.LOG().RaiseException('@: Implement MoveTo() in the subclass.')
