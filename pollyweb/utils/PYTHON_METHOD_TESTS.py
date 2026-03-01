from .LOG import LOG
from .TESTS import TESTS 


class PYTHON_METHOD_TESTS:



    @classmethod
    def TestClsMethod(cls):
        pass

    @classmethod
    def TestPythonMethod_Callable(cls):
        
        from .PYTHON_METHOD import PYTHON_METHOD
        m = PYTHON_METHOD(PYTHON_METHOD_TESTS.TestClsMethod)
        
        TESTS.AssertEqual(m.GetFileName(), 'PYTHON_METHOD_TESTS.py')
        TESTS.AssertTrue(m.GetFileName().endswith('PYTHON_METHOD_TESTS.py'))
        TESTS.AssertEqual(m.GetMethodName(), 'TestClsMethod')
        TESTS.AssertEqual(m.GetParentMethodName(), 'TestClsMethod', 'Wrong parent method name.')
        
        #TODO: uncomment
        #TESTS.AssertEqual(m.GetModuleName(), 'PYTHON_METHOD_TESTS', 'Wrong module name.')

        #TODO: uncomment
        #TESTS.AssertEqual(m.GetPackageName(), '', 'Wrong package name.')

        TESTS.AssertEqual(m.GetQualName(), 'PYTHON_METHOD_TESTS.TestClsMethod', 'Wrong qualified name.')    
        TESTS.AssertEqual(m.GetFullName(), 'PYTHON_METHOD_TESTS.TestClsMethod', 'Wrong full name.')
        TESTS.AssertEqual(m.GetClassName(), 'PYTHON_METHOD_TESTS', 'Wrong class name.')
        TESTS.AssertEqual(m.GetIcon(), '🐠')  
        TESTS.AssertEqual(m.IsLocal(), False)
        TESTS.AssertEqual(m.GetFileName(), 'PYTHON_METHOD_TESTS.py', 'Wrong file name.')
        m.GetClass()  # Ensure the class can be retrieved without error.


    @classmethod
    def TestPythonMethod_CodeType(cls):
        PYTHON_METHOD_TESTS().TestSelfMethod()


    def TestSelfMethod(self):
        from .PYTHON_METHOD import PYTHON_METHOD

        m = PYTHON_METHOD(self.TestSelfMethod.__code__, self.__class__)
        
        TESTS.AssertEqual(m.GetClassName(), 'PYTHON_METHOD_TESTS', 'Wrong class name.')
        TESTS.AssertEqual(m.GetIcon(), '🐠')  
        TESTS.AssertEqual(m.IsLocal(), False)

        TESTS.AssertEqual(m.GetPackageName(), '', 'Wrong package name.')
        TESTS.AssertEqual(m.GetModuleName(), 'PYTHON_METHOD_TESTS', 'Wrong module name.')
        TESTS.AssertEqual(m.GetFileName(), 'PYTHON_METHOD_TESTS.py', 'Wrong file name.')
        #TESTS.AssertTrue(m.GetFileName().endswith('PYTHON_METHOD_TESTS.py'))
        TESTS.AssertEqual(m.GetMethodName(), 'TestSelfMethod', 'Wrong method name.')
        TESTS.AssertEqual(m.GetParentMethodName(), 'TestSelfMethod', 'Wrong parent method name.')
        TESTS.AssertEqual(m.GetQualName(), 'PYTHON_METHOD_TESTS.TestSelfMethod', 'Wrong qualified name.')
        TESTS.AssertEqual(m.GetFullName(), 'PYTHON_METHOD_TESTS.TestSelfMethod', 'Wrong full name.')
        
        m.GetClass()  # Ensure the class can be retrieved without error.


    @classmethod
    def IsThisFruitNice(self, fruit:str = 'Rice'):

        LOG.Print(self.IsThisFruitNice, f'({fruit})')
        LOG.Print(f'Inside IsThisFruitNice.')

        return f'Yes, {fruit} is nice.' 
        

    @classmethod
    def TestPythonMethod_Invoke(cls):

        handler = PYTHON_METHOD_TESTS.IsThisFruitNice
        
        from .PYTHON_METHOD import PYTHON_METHOD
        method = PYTHON_METHOD(handler)

        result = method.InvokeWithMatchingArgs(
            args= dict(fruit= 'Banana'))
        TESTS.AssertEqual(result, 'Yes, Banana is nice.', 'Wrong result from InvokeWithMatchingArgs.')

        result = method.InvokeWithMatchingArgs(
            args= dict())
        TESTS.AssertEqual(result, 'Yes, Rice is nice.', 'Wrong result from InvokeWithMatchingArgs.')


    @classmethod
    def TestAllPythonMethod(cls):
        
        # DEFINITION
        cls.TestPythonMethod_Callable()
        cls.TestPythonMethod_CodeType()

        # INVOCATION
        cls.TestPythonMethod_Invoke()