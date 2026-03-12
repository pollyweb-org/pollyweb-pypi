from pollyweb.interfaces.CODE_TESTS import CODE_TESTS
from pollyweb.interfaces.PROMPT_TESTS import PROMPT_TESTS
from pollyweb.interfaces.QR_TESTS import QR_TESTS
from pollyweb.utils.STRUCT_TESTS import STRUCT_TESTS


def test_code_tests_suite():
    CODE_TESTS.TestAllCode()


def test_prompt_tests_suite():
    PROMPT_TESTS.TestAllPrompt()


def test_qr_tests_suite():
    QR_TESTS.TestAllQR()


def test_struct_tests_suite():
    STRUCT_TESTS.TestAllStruct()
