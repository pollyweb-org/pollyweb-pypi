from __future__ import annotations
from .DIRECTORY import DIRECTORY
from .LOG import LOG
from .STRUCT import STRUCT
from .UTILS import UTILS


class ZIP_INFO(STRUCT):

    def __init__(self, info:any):
        super().__init__(info)


    def GetDirectory(self):
        from .FILESYSTEM import FILESYSTEM
        return FILESYSTEM.DIRECTORY(self.RequireStr('Directory'))


    def GetFileNames(self):
        '''👉️ Gets the file names.'''
        return list(self.RequireDict('Files').keys())


    def GetInfo(self):
        '''👉️ Gets the info.'''
        return self.RequireDict('Files')
    

    def IsSame(self, other:ZIP_INFO):

        UTILS.AssertIsAnyType(other, [ZIP_INFO], require=True)

        zip_info1 = self.GetInfo()
        zip_info2 = other.GetInfo()

        # Compare number of files
        if len(zip_info1) != len(zip_info2):
            LOG.Print(' ZIP.INFO.IsSame: Diferent number of files.')
            return False
        
        # Compare file details
        for filename in zip_info1:
            if filename not in zip_info2:
                LOG.Print(f' ZIP.INFO.IsSame: File {filename} not found.')
                return False
            if zip_info1[filename]['size'] != zip_info2[filename]['size']:
                LOG.Print(f' ZIP.INFO.IsSame: File {filename} has different size.')
                return False
            if zip_info1[filename]['crc'] != zip_info2[filename]['crc']:
                LOG.Print(f' ZIP.INFO.IsSame: File {filename} has different crc.')
                return False
        
        return True
    

    def Save(self, name:str, metadata:dict):
        '''👉️ Saves the ZIP_INFO to a file.'''

        # Assert the metadata is a dictionary
        UTILS.AssertIsType(metadata, dict, require=True)

        # Add the metadata to the ZIP_INFO
        self['Metadata'] = metadata

        # Save the ZIP_INFO to a file
        file = self.GetDirectory().GetParentDir().GetFile(
            f'{name}.zip.yaml'
        ).WriteYaml(self)
        
        LOG.Print(' ZIP.INFO.Save: Saved to:', f'{file.RequirePath()=}')

        return self


    def RequireMetadata(self):
        return self.RequireDict('Metadata')


    @staticmethod
    def Load(dir:DIRECTORY, name:str):
        file = dir.GetParentDir().GetFile(f'{name}.zip.yaml')
        if not file.Exists():
            return None
        yaml = file.ReadYaml()
        return ZIP_INFO(yaml)