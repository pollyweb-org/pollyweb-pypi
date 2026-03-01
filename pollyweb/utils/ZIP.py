from __future__ import annotations

import zipfile
import io
import os
from typing import Union
from .DIRECTORY import DIRECTORY
from .PRINTABLE import PRINTABLE
from .UTILS import UTILS
from .LOG import LOG
from .ZIP_INFO import ZIP_INFO


class ZIP(PRINTABLE):


    def __init__(self, arg:Union[bytes, str], directory:DIRECTORY=None) -> None:
        '''👉️ Initializes the ZIP object.
        
        Arguments:
            * `arg` {bytes|str} -- The bytes or the path of the zip file.
        '''

        UTILS.Require(arg)

        if isinstance(arg, bytes):
            # Store the bytes given.
            self._bytes = arg
            self._directory = directory
            super().__init__('<ZIP>')

        elif isinstance(arg, str):
            # Read the bytes from the file path.
            self._bytes = UTILS.OS().ReadFileBytes(arg)
            super().__init__(arg)

            from .FILE import FILE
            self._directory = FILE(arg).GetParentDir()

        else:
            raise Exception(f"Invalid argument type: {type(arg)}")
        
        super().__init__(self.GetZipInfo)


    def GetBytes(self):
        '''👉️ Gets the bytes of the zip buffer.'''
        return self._bytes


    def GetZipInfo(self):
        '''👉️ Gets the info of the zip buffer.'''
        # Use BytesIO to treat bytes data as a file-like object
        bytes_data = self._bytes
        with zipfile.ZipFile(io.BytesIO(bytes_data), 'r') as zipf:
            info = {}

            info['Files'] = {
                file.filename: {
                    'size': file.file_size, 
                    'crc': file.CRC
                } for file in zipf.infolist()
            }

            info['Directory'] = self._directory.GetPath()

            return ZIP_INFO(info)


    def GetDirectory(self):
        return self.GetZipInfo().GetDirectory()


    def IsSameAs(self, zip:Union["ZIP", ZIP_INFO]):
        '''👉️ Compares the contents of the zip files.'''

        if zip is None:
            return False

        # Assert the input is a ZIP object
        UTILS.AssertIsAnyType(zip, [ZIP, ZIP_INFO], require=True)

        # Get the contents info of both zip files
        if isinstance(zip, ZIP):
            zip = zip.GetZipInfo()
        
        return self.GetZipInfo().IsSame(zip)
        

    def Unzip(self, into:str):
        '''👉️ Extracts the contents of the zip file to the specified path.'''

        # Assert the target directory exists
        from .FILESYSTEM import FILESYSTEM
        FILESYSTEM.DIRECTORY(into).AssertExists()

        zip_bytes = self._bytes
        target_directory = into
        
        # Open the ZIP file from bytes
        with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zipf:
            self._ValidateZipPaths(zipf, target_directory)
            # Extract all the contents into the target directory
            zipf.extractall(path= target_directory)
            LOG.Print(f"All files have been extracted to {target_directory}.")


    @staticmethod
    def _ValidateZipPaths(zipf:zipfile.ZipFile, target_directory:str):
        '''👉️ Block path traversal (Zip Slip) entries while extracting ZIPs.'''
        target_real = os.path.realpath(target_directory)
        for member in zipf.infolist():
            destination = os.path.realpath(
                os.path.join(target_real, member.filename))
            if destination != target_real and \
                not destination.startswith(target_real + os.sep):
                LOG.RaiseValidationException(
                    f'Unsafe ZIP entry path: {member.filename}')


    @staticmethod
    def LoadInfo(dir:DIRECTORY, name:str):
        return ZIP_INFO.Load(dir=dir, name=name)
