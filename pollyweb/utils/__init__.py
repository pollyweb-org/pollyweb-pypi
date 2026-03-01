class LOADER:

    @classmethod
    def AppendFolderToPath(cls, folder:str):
        '''👉️ Appends a folder to the system path.'''
        import sys
        from pathlib import Path

        # Path to the folder containing this __init__.py
        current_dir = Path(__file__).resolve().parent

        # Path to the 'tests' folder (child folder)
        folder_dir = current_dir / folder

        # Add to sys.path if not already there
        if str(folder_dir) not in sys.path:
            sys.path.append(str(folder_dir))


    @classmethod
    def LoadImports(cls):
        '''👉 Loads the imports.'''
        cls.AppendFolderToPath('init')
        from .IMPORTS import IMPORTS 
        

#LOADER.LoadImports()





# Expose main classes and functions for easier imports
from .DIRECTORY import DIRECTORY
from .FILESYSTEM_OBJECT import FILESYSTEM_OBJECT
from .FILESYSTEM import FILESYSTEM
from .FILE import FILE
from .LOG import LOG
from .LOG_BUFFER import LOG_BUFFER
from .LOG_BUFFER_INFO import LOG_BUFFER_INFO
from .PRINTABLE import PRINTABLE
from .PYTHON_METHOD import PYTHON_METHOD
from .RUNNER import RUNNER
from .STRUCT import STRUCT
from .TESTS import TESTS, AssertException, ValidationException
from .UTILS import UTILS
from .UTILS_CACHE import UTILS_CACHE
from .UTILS_TYPES import UTILS_TYPES
from .UUID import UUID
from .PYTHON_CLASS import PYTHON_CLASS
from .STRUCT_CONVERT import STRUCT_CONVERT
from .LOG_SETTINGS import LOG_SETTINGS
from .LOG_EXCLUDES import LOG_EXCLUDES

__all__ = [
    "AssertException",
    "ValidationException",
    "DIRECTORY", 
    "FILESYSTEM_OBJECT",
    "FILESYSTEM", 
    "FILE",
    "LOG", 
    "LOG_BUFFER",
    "LOG_BUFFER_INFO",
    "PRINTABLE",
    "PYTHON_METHOD",
    "STRUCT", 
    "RUNNER",
    "UTILS", 
    "UTILS_CACHE",
    "UTILS_TYPES",
    "UUID",
    "PYTHON_CLASS",
    "STRUCT_CONVERT",
    "LOG_SETTINGS",
    "LOG_EXCLUDES",
    "TESTS"
]