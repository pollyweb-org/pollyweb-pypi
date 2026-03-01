from .DIRECTORY import DIRECTORY


class PYTHON_APP:
    '''👉 A Python application.

    Properties:
        * `Dir`:DIRECTORY - The directory containing the application.
        * `Start`:str - The name of the .py file to start the application.
    '''


    def __init__(self, 
        dir:DIRECTORY= None, 
        start:str= None
    ):
        '''👉 Initializes the Python application.
            * If `dir` is not provided, a temporary directory is created.
            * If `start` is not provided, it stays None until manually set.
        
        Arguments:
            `dir` {DIRECTORY} -- The directory containing the application.
            `start` {str} -- The name of the .py file to start the application.
        '''
        self.GivenDir = dir
        self.Dir = dir if dir else DIRECTORY.GetTempDir()
        self.Start:str = start

        self.RetainOnFailure = False
        '''👉 Whether to retain the directory on failure.'''
        
        self.Retain = False
        '''👉 Whether to retain the directory after the application is done.'''


    def __enter__(self):
        return self
    

    def __exit__(self, type, value, traceback):
        if not self.GivenDir:
            self.Dir.RetainOnFailure = self.RetainOnFailure
            self.Dir.Retain = self.Retain
            self.Dir.__exit__(type, value, traceback)


    def AddHellowWorldPython(self):
        '''👉 Adds a Hello World file.'''
        file = self.Dir.GetFile('hello.py')
        file.WriteText('print("Hello, World!")')
        self.Start = file.GetName()
        return self
    

    def AddHellowWorldStreamlit(self):
        '''👉 Adds a Streamlit Hello World file.'''

        hello = self.Dir.GetFile('hello.py')
        hello.WriteLines([
            'import streamlit as st',
            'st.write("Hello world!")'
        ])
        self.Start = hello.GetName()

        requirements = self.Dir.GetFile('requirements.txt')
        requirements.WriteText('streamlit')
        
        return self
    
