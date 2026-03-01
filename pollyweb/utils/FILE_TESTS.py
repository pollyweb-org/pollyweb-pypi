# 📚 UTILS

from __future__ import annotations
from .TESTS import TESTS
from .FILE import FILE
import os

from .FILESYSTEM import FILESYSTEM


class FILE_TESTS(TESTS):
    

    @classmethod
    def TestGetPath(cls):
        '''👉️ Test the GetPath() method.'''
        file = FILESYSTEM.FILE('README.md')
        cls.AssertEqual(
            file.GetPath(),
            os.path.abspath('README.md'))
    

    @classmethod
    def TestGetName(cls):
        '''👉️ Test the GetName() method.'''
        file = FILESYSTEM.FILE('README.md')
        cls.AssertEqual(
            file.GetName(), 
            'README.md')
        
    
    @classmethod    
    def TestGetExtension(cls):
        '''👉️ Test the GetExtension() method.'''
        file = FILESYSTEM.FILE('README.md')
        cls.AssertEqual(
            file.GetExtension(),
            '.md')
    

    @classmethod
    def TestGetSimpleName(cls):
        '''👉️ Test the GetSimpleName() method.'''
        
        file = FILESYSTEM.FILE('README.md')
        cls.AssertEqual(file.GetSimpleName(), 'README')
        
        file = FILESYSTEM.FILE('🧱 README.md')
        cls.AssertEqual(file.GetSimpleName(), 'README')
        
        file = FILESYSTEM.FILE('🧱  README.md')
        cls.AssertEqual(file.GetSimpleName(), 'README')

        file = FILESYSTEM.FILE('README 🧱.md')
        cls.AssertEqual(file.GetIcon(), '🧱')
        cls.AssertEqual(file.GetSimpleName(), 'README')

        file = FILESYSTEM.FILE('README🧱.md')
        cls.AssertEqual(file.GetSimpleName(), 'README🧱')

        file = FILESYSTEM.FILE('READ ME 🧱.md')
        cls.AssertEqual(file.GetSimpleName(), 'READ ME')


    @classmethod
    def TestGetIcon(cls):
        '''👉️ Test the GetIcon() method.'''

        file = FILESYSTEM.FILE('README.md')
        cls.AssertEqual(file.GetIcon(), None)
        
        file = FILESYSTEM.FILE('🐍 README.md')
        cls.AssertEqual(file.GetIcon(), '🐍')
        
        file = FILESYSTEM.FILE('🧱  README.md')
        cls.AssertEqual(file.GetIcon(), '🧱')

        file = FILESYSTEM.FILE('README🧱.md')
        cls.AssertEqual(file.GetIcon(), None)

        file = FILESYSTEM.FILE('README 🧱.md')
        cls.AssertEqual(file.GetIcon(), '🧱')

        file = FILESYSTEM.FILE('READ ME 🧪.md')
        cls.AssertEqual(file.GetIcon(), '🧪')
        
        file = FILESYSTEM.FILE('READ 🧪 ME.md')
        cls.AssertEqual(file.GetIcon(), None)


    @classmethod
    def TestGetNameWithoutExtension(cls):
        '''👉️ Test the GetNameWithoutExtension() method.'''

        file = FILESYSTEM.FILE('README.md')
        cls.AssertEqual(file.GetNameWithoutExtension(), 'README')
            
        file = FILESYSTEM.FILE('🧱 README.md')
        cls.AssertEqual(file.GetNameWithoutExtension(), '🧱 README')
        
        file = FILESYSTEM.FILE('🧱  README.md')
        cls.AssertEqual(file.GetNameWithoutExtension(), '🧱  README')

        file = FILESYSTEM.FILE('README🧱.md')
        cls.AssertEqual(file.GetNameWithoutExtension(), 'README🧱')

        file = FILESYSTEM.FILE('READ ME🧱.md')
        cls.AssertEqual(file.GetNameWithoutExtension(), 'READ ME🧱')


    @classmethod
    def TestRequirePath(cls):
        '''👉️ Test the RequirePath() method.'''
        from .UTILS_OS import UTILS_OS
        file = UTILS_OS().GetClassFile(cls)
        cls.AssertTrue(
            file.RequirePath().endswith('FILE_TESTS.py'))
        

    @classmethod 
    def TestWriteText(cls):
        '''👉️ Test the WriteText() method.'''
        try:
            file = FILESYSTEM.FILE('TestWriteText.md')
            file.WriteText('Hello World!')
            cls.AssertEqual(
                file.ReadText(), 
                'Hello World!',
                msg='Text mishmatch in TestWriteText')
        finally:        
            file.Delete()


    @classmethod
    def TestReadText(cls):
        '''👉️ Test the ReadText() method.'''
        try:
            texts = [
                'Hello World!\n.'
                'Hello World!\n \n.'
                'Hello World!\n \n\n.'
                'Hello World!\n \n\n  \n .',
                'Emojy 🧱\n.',
            ]

            file = FILESYSTEM.FILE('TestReadText.md')
            for text in texts: 
                file.WriteText(text)
                cls.AssertEqual(
                    file.ReadText(), 
                    text,
                    msg='Text mishmatch in TestReadText')
                
        finally:        
            file.Delete()


    @classmethod
    def TestWriteLines(cls):
        '''👉️ Test the WriteLines() method.'''
        try:
            file = FILESYSTEM.FILE('TestWriteLines.md')
            file.WriteLines(['l1', '', '  ', 'l3'])

            cls.AssertEqual(
                file.ReadText(), 
                'l1\n\n  \nl3',
                msg='Text mishmatch in TestWriteLines')
        finally:        
            file.Delete()


    @classmethod
    def TestReadLines(cls):
        '''👉️ Test the ReadLines() method.'''
        try:
            file = FILESYSTEM.FILE('TestReadLines.md')
            
            file.WriteText('l1\n\n  \nl2')
            cls.AssertEqual(file.ReadLines(), ['l1', '', '  ', 'l2'])
            
            file.WriteLines(['l1', '', '  ', 'l3'])
            cls.AssertEqual(file.ReadLines(), ['l1', '', '  ', 'l3'])

        finally:        
            file.Delete()


    @classmethod
    def TestReadLogLines(cls):
        '''👉️ Test the ReadLogLines() method.'''
        try:
            file = FILESYSTEM.FILE('TestReadLogLines.md')
            file.WriteLines(['l1', '', '  ', 'l3'])
            
            cls.AssertEqual(
                file.ReadLogLines(), 
                ['l3', 'l1'], 
                msg='LogLines mishmatch in TestReadLogLines')
        finally:        
            file.Delete()


    @classmethod
    def TestTextLenght(cls):
        '''👉️ Test the TextLenght() method.'''
        try:
            file = FILESYSTEM.FILE('TestTextLenght.md')
            file.WriteText('Hello World!')
            cls.AssertEqual(file.TextLenght(), 12)
        finally:        
            file.Delete()


    @classmethod
    def TestAllFile(cls):
        '''👉️ Test all methods in the FILE class.'''
        cls.TestGetPath()
        cls.TestGetName()
        cls.TestGetExtension()
        cls.TestGetSimpleName()
        cls.TestGetIcon()
        cls.TestGetNameWithoutExtension()
        cls.TestRequirePath()

        cls.TestWriteText()
        cls.TestReadText()
        cls.TestWriteLines()
        cls.TestReadLines()
        cls.TestReadLogLines()
        cls.TestTextLenght()