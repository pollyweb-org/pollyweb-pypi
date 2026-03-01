from .LOG import LOG
from .TESTS import TESTS 


class PYTHON_CLASS_TESTS:



    @classmethod
    def TestAllPythonClass_Str(cls):
        
        from .PYTHON_CLASS import PYTHON_CLASS

        m = PYTHON_CLASS('PYTHON_CLASS', checkType='str')
        TESTS.AssertEqual(m.GetModuleName(), 'PYTHON_CLASS', 'Wrong module name.')
        TESTS.AssertEqual(m.GetName(), 'PYTHON_CLASS', 'Wrong name.')
        
        
    @classmethod
    def TestAllPythonClass_Type(cls):
        
        from .PYTHON_CLASS import PYTHON_CLASS
        m = PYTHON_CLASS(PYTHON_CLASS_TESTS, checkType='type')
        
        TESTS.AssertEqual(m.GetName(), 'PYTHON_CLASS_TESTS', 'Wrong name.')
        
        #TODO: uncomment
        #TESTS.AssertEqual(m.GetModuleName(), 'PYTHON_CLASS_TESTS', 'Wrong module name.')


    @classmethod
    def TestAllPythonClass_Other(cls):
        
        from .PYTHON_CLASS import PYTHON_CLASS
        m = PYTHON_CLASS(PYTHON_CLASS_TESTS(), checkType='other')
        
        TESTS.AssertEqual(m.GetName(), 'PYTHON_CLASS_TESTS', 'Wrong name.')
        
        #TODO: uncomment
        #TESTS.AssertEqual(m.GetModuleName(), 'PYTHON_CLASS_TESTS', 'Wrong module name.')



    @classmethod
    def TestAllPythonClass(cls):
        
        cls.TestAllPythonClass_Type()
        cls.TestAllPythonClass_Other()
        cls.TestAllPythonClass_Str()
        