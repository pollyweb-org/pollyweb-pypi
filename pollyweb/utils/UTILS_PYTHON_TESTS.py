from __future__ import annotations
from .LOG import LOG
from .PYTHON_CLASS import PYTHON_CLASS
from .PYTHON_EDITOR_TEST import PYTHON_EDITOR_TEST
from .PYTHON_METHOD import PYTHON_METHOD
from .TESTS import TESTS
from .UTILS_PYTHON import UTILS_PYTHON
from .UTILS import UTILS

class MyLog:
        
    def log(self, 
        goUp:int=0
    ):
        self.ModuleName = UTILS_PYTHON.GetCallerClassName(goUp= goUp+1)
        self.Name = UTILS_PYTHON.GetCallerName(goUp= goUp+1)
        self.FullName = UTILS_PYTHON.GetCallerFullName(goUp= goUp+1)
        self.ParentFunctionInfo = UTILS_PYTHON.GetParentFunctionInfo(goUp= goUp+1)
        self.ParentFunctionName = UTILS_PYTHON.GetParentFunctionName(goUp= goUp+1)


class MyClass:

    def __init__(self, log:MyLog):
        self._log = log

    def outer_method(self):
        def inner_method():
            self._log.log()
        inner_method()

    def root_method(self):
        self._log.log()

        
class MyClassWithAnIcon:  
    ICON= '🧪'
    pass

class MyClassWithoutAnIcon:
    pass

class UTILS_PYTHON_TESTS(): 
    
    ICON='🐍'

    @classmethod
    def TestInnerMethods(cls):

        logInner = MyLog()
        logRoot = MyLog()
        
        MyClass(logInner).outer_method()
        MyClass(logRoot).root_method()

        TESTS.AssertEqual(logInner.Name, 'inner_method', msg='Different Name')
        TESTS.AssertEqual(logRoot.Name, 'root_method', msg='Different Name')
        
        # Verify ParentFunctionInfo
        
        TESTS.AssertEqual(logInner.ParentFunctionInfo, 
            dict(
                callable_is_inner= True,
                callable_parent_method_name= 'outer_method',
                callable_method_name= 'inner_method',
                qualname= 'MyClass.outer_method.<locals>.inner_method',
                class_name= 'MyClass'),
            msg='Different ParentFunctionInfo on inner_method')
        
        TESTS.AssertEqual(logRoot.ParentFunctionInfo, 
            dict(
                callable_is_inner= False,
                callable_parent_method_name= 'root_method',
                callable_method_name= 'root_method',
                qualname= 'MyClass.root_method',
                class_name= 'MyClass'),
            msg='Different ParentFunctionInfo on root_method')

        # Verify ParentFunctionName

        TESTS.AssertEqual(logInner.ParentFunctionName, 
            'outer_method', 
            msg='Different ParentFunctionName')
        
        TESTS.AssertEqual(logRoot.ParentFunctionName, 
            MyClass.root_method.__name__, 
            msg='Different ParentFunctionName')

        # Verify class name.

        TESTS.AssertEqual(logInner.ModuleName, 
            MyClass.__name__, 
            msg='Different ModuleName')
        
        TESTS.AssertEqual(logRoot.ModuleName, 
            MyClass.__name__, 
            msg='Different ModuleName')
        
        # Verify FullName

        TESTS.AssertEqual(logInner.FullName, 
            f'{MyClass.__name__}.{MyClass.outer_method.__name__}', 
            msg='Different FullName')
        
        TESTS.AssertEqual(logRoot.FullName, 
            f'{MyClass.__name__}.{MyClass.root_method.__name__}', 
            msg='Different FullName')


    
    @classmethod
    def TestClassIcons(cls):
        
        # Class with an icon.
        myClassWithAnIcon = PYTHON_CLASS(MyClassWithAnIcon)
        TESTS.AssertEqual(myClassWithAnIcon.RequireIcon(), '🧪')

        # Class without an icon.
        myClassWithAnIcon = PYTHON_CLASS(MyClassWithoutAnIcon)
        TESTS.AssertEqual(myClassWithAnIcon.GetIcon(), None)
        with TESTS.AssertValidation():
            myClassWithAnIcon.RequireIcon()


    @classmethod
    def TestLogPlaceholders(cls):  
                
        # Skip the test if the fast mode is enabled.
        if LOG.Settings().GetTestFast():
            return

        TESTS.AssertEqual(
            LOG.Print('🏎️ @: DummyRaceCar', 345),
            f'🏎️ UTILS_PYTHON_TESTS.TestLogPlaceholders: DummyRaceCar')
        
        TESTS.AssertEqual(
            LOG.Print('@ DummyPython', 123),
            f'🐍 UTILS_PYTHON_TESTS.TestLogPlaceholders DummyPython')
        
        TESTS.AssertEqual(
            LOG.Print('@: DummyPython', 123),
            f'🐍 UTILS_PYTHON_TESTS.TestLogPlaceholders: DummyPython')
        
        TESTS.AssertEqual(
            LOG.Print('@(DummyPython)', 123),
            f'🐍 UTILS_PYTHON_TESTS.TestLogPlaceholders(DummyPython)')
        
        TESTS.AssertEqual(
            LOG.Print(cls.TestLogPlaceholders, 345),
            f'🐍 UTILS_PYTHON_TESTS.TestLogPlaceholders()')
        
        TESTS.AssertEqual(
            LOG.Print(cls.TestLogPlaceholders, 345),
            f'🐍 UTILS_PYTHON_TESTS.TestLogPlaceholders()')


    @classmethod
    def TestCallWithMatchingArgs(cls):
        LOG.Print(cls.TestCallWithMatchingArgs)
        
        # Define a sample function with specific arguments
        def M(A, B=2):
            from .LOG import LOG
            LOG.Print(f"A = {A}, B = {B}")
            if A !=1 or B != 2:
                raise Exception('Invalid arguments')

        # Successful calls
        m = PYTHON_METHOD(M)
        m.InvokeWithMatchingArgs({'A': 1, 'B': 2})
        m.InvokeWithMatchingArgs({'A': 1})

        # Call the function using the utility function
        with TESTS.AssertValidation():
            m.InvokeWithMatchingArgs({'A': 1, 'C': 2})
    

    @classmethod
    def TestAllPython(cls):
        LOG.Print(cls.TestAllPython)


        from .PYTHON_CLASS_TESTS import PYTHON_CLASS_TESTS
        PYTHON_CLASS_TESTS.TestAllPythonClass()

        from .PYTHON_METHOD_TESTS import PYTHON_METHOD_TESTS
        PYTHON_METHOD_TESTS.TestAllPythonMethod()
        

        cls.TestInnerMethods()
        cls.TestClassIcons()
        cls.TestLogPlaceholders()
        cls.TestCallWithMatchingArgs()

        PYTHON_EDITOR_TEST.TestAllEditor()