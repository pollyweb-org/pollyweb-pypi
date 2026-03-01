from __future__ import annotations
from .FILE import FILE

import zipfile
from .UTILS import UTILS
from .ZIP import ZIP
from .ZIP_INFO import ZIP_INFO


class ZIP_FILE(ZIP, FILE):


    def __init__(self, path:str) -> None:
        '''👉️ Initializes the ZIP_FILE object.
        
        Arguments:
            * `path` {str} -- The path of the zip file.
        '''
        super().__init__(path)

    
    def GetBytes(self):
        '''👉️ Gets the bytes of the zip file.'''
        path = self.RequirePath()

        # Open the zip file in binary read mode
        with open(path, 'rb') as file:
            zip_bytes = file.read()
        return zip_bytes


    def GetZipInfo(self):
        '''👉️ Gets the info of the zip file.'''
        zip_path = self.RequirePath()

        with zipfile.ZipFile(zip_path, 'r') as zipf:
            # Extract essential info for each file in the zip
            info = {}

            info['Files'] = {
                file.filename: {
                    'size': file.file_size, 
                    'crc': file.CRC
                } for file in zipf.infolist()
            }

            info['Directory'] = self._directory.GetPath()

            return ZIP_INFO(info)


    def Unzip(self, into:str):
        '''👉️ Extracts the contents of the zip file to the specified path.'''
        file = self.RequirePath()
        UTILS.Unzip(file, into=into)