from AWS_RESOURCE_ITEM import AWS_RESOURCE_ITEM_TYPE
from AWS_RESOURCE_POOL import AWS_RESOURCE_POOL, AWS_RESOURCE_WRAP
from pollyweb.utils.TESTS import TESTS

from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic


class AWS_RESOURCE_TESTER(ABC, Generic[AWS_RESOURCE_ITEM_TYPE]):

    ICON= '🧪'


    @classmethod
    def RunAllTests(cls):
        for test in cls.GetAllTests():
            test()


    @classmethod
    @abstractmethod
    def GetAllTests(cls) -> list:
        raise Exception('Implement')


    @classmethod
    def BasicTest(cls, 
        pool: AWS_RESOURCE_POOL[AWS_RESOURCE_ITEM_TYPE],
        name: str,
        client= None,
        resource= None,
        **args: dict,
    ):
        with pool.Test(
            name= name,
            client= client,
            resource= resource,
            **args
        ):
            pass