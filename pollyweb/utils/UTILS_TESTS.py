# 📚 UTILS

from .UTILS_OS_TESTS import UTILS_OS_TESTS
from .UTILS_PYTHON_TESTS import UTILS_PYTHON_TESTS
from .UTILS_YAML_TESTS import UTILS_YAML_TESTS
from .UTILS_TIME_TESTS import UTILS_TIME_TESTS
from .UTILS_OBJECTS_TESTS import UTILS_OBJECTS_TESTS
from .UTILS_LISTS_TESTS import UTILS_LISTS_TESTS
from .UTILS_TYPES_TESTS import UTILS_TYPES_TESTS
from .LOG import LOG


class UTILS_TESTS(
    UTILS_OS_TESTS,
    UTILS_PYTHON_TESTS,
    UTILS_YAML_TESTS,
    UTILS_TIME_TESTS,
    UTILS_LISTS_TESTS,
    UTILS_TYPES_TESTS, 
    UTILS_OBJECTS_TESTS): 


    @classmethod
    def TestAllUtils(cls):
        LOG.Print('UTILS_TESTS.TestAllUtils() ==============================')
        
        cls.TestAllOS()
        cls.TestAllYaml()
        cls.TestAllTime()
        cls.TestAllObjects()
        cls.TestAllTypes()
        cls.TestAllLists()
        cls.TestAllPython()