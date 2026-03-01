import os
from .FILESYSTEM_OBJECT import FILESYSTEM_OBJECT
from .SETTINGS import SETTINGS


class FILESYSTEM:
    ''' 👉️ Represents the filesystem twin.
        * The filesystem twin is a data structure that mirrors the filesystem.
        * It is used to keep track of the filesystem nodes and their objects.
        * It is used to map, rename, and delete objects in the filesystem.
        * Used for recursively updating the icons in files and directories.
    '''

    ICON:str = '🗃️'


    # Directory where the files will be stored
    directory = '__dumps__/FILESYSTEM/'


    @classmethod
    def LOG(cls):
        '''👉️ Returns the LOG object.'''
        from .LOG import LOG
        return LOG


    @classmethod
    def GetDir(cls):
        '''👉️ Cleans up the filesystem twin.'''
        return cls.DIRECTORY(cls.directory)


    @classmethod
    def DIRECTORY(cls, name:str):
        '''👉️ Returns a directory object.'''
        cls.LOG().Print(f'@({name=})')
        
        from .DIRECTORY import DIRECTORY
        obj = DIRECTORY(name, dummy=1) 
        cls._MapPathToObject(obj, obj._path)
        return obj
        

    @classmethod
    def FILE(cls, name:str):
        '''👉️ Returns a file object.'''
        cls.LOG().Print(f'@({name=})')
        
        from .FILE import FILE
        
        if name.startswith('/'):
            path = name
        else:
            path = os.path.abspath(name)

        obj = FILE(path, dummy=1) 
        cls._MapPathToObject(obj, path)
        return obj
    

    @classmethod
    def _MapPathToObject(cls, obj:FILESYSTEM_OBJECT, path:str):
        '''👉️ Maps a path to a filesystem node.'''

        from .SETTINGS import SETTINGS
        if not SETTINGS.ICONS_ENABLED:
            return obj

        uuid = obj._uuid

        # Create the directory if it does not exist
        os.makedirs(cls.directory, exist_ok=True)

        # Path to the markdown file
        file_path = f'{cls.directory}{uuid}.md'

        # Write the path to the markdown file
        with open(file_path, 'w') as file:
            file.write(path)

        return obj


    @classmethod
    def GetPathByUuid(cls, uuid:str):
        '''👉️ Retrieve the path by UUID from the filesystem node.'''

        # Directory where the file should be located
        file_path = f'{cls.directory}{uuid}.md'

        # Check if the file exists
        if os.path.exists(file_path):
            # Read the path from the markdown file
            with open(file_path, 'r') as file:
                return file.read().strip()
        else:
            # Return None or raise an error if the file does not exist
            # return None
            # Or, optionally raise an error:
            raise FileNotFoundError(
                f'No entry found for UUID [{uuid}]'
                f' in [{os.path.abspath(cls.directory)}]')
        

    @classmethod
    def Rename(cls, obj:FILESYSTEM_OBJECT, newName:str):
        
        # Prepare the variables.
        uuid = obj._uuid
        oldPath = obj.GetPath()
        newPath = os.path.join(os.path.dirname(oldPath), newName)

        # Rename the object.
        try:
            os.rename(oldPath, newPath)
        except Exception as e:
            if 'Directory not empty' in str(e):
                from .LOG import LOG
                LOG.RaiseException(
                    f'Renaming to an existing dir is not allowed: [{newPath}]')

        # Update the object's properties.
        obj._SetPath(newPath)

        if not SETTINGS.ICONS_ENABLED:
            return obj
        
        # Replace the path in the {uuid}.md file.
        file_path = f'{cls.directory}{uuid}.md'
        if os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write(newPath)

        # Replace '{oldPath}/' for '{newPath}/' in all files.
        for root, dirs, files in os.walk(cls.directory):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                with open(full_path, 'r') as file:
                    contents = file.read()
                new_contents = contents.replace(f'{oldPath}/', f'{newPath}/')
                with open(full_path, 'w') as file:
                    file.write(new_contents)

        return obj