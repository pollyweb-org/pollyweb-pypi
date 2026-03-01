# 📚 ITEM

from __future__ import annotations
from typing import Union, Any

from ..utils import UTILS
from ..utils import STRUCT
from ..utils import LOG


class ITEM_TABLE:

    ICON = '🪣'

    def Update(self, item: Union[dict[str, Any], STRUCT]) -> "ITEM":
        LOG.RaiseException('Please override!')

    def Delete(self, struct: "ITEM"):
        LOG.RaiseException('Please override!')

    def Require(self, key: Union[str, int, STRUCT, dict[str, str]]) -> "ITEM":
        LOG.RaiseException('Please override!')


class ITEM(STRUCT):
    ''' 👉 STRUCT created from a DynamoDB item (see DYNAMO).
    1. table = DYNAMO(alias)
    2. item = table.Get(key, require=True)
    3. item.Att('a',1)
    4. item.Update()
    '''

    def __init__(self, item: Any = {}, table: Union[ITEM_TABLE, None] = None):
        if table is not None:
            UTILS.AssertIsType(table, ITEM_TABLE)
            self.__itemTable = table
        elif isinstance(item, ITEM):
            self.__itemTable = item.__itemTable
        else:
            self.__itemTable = None

        super().__init__(item)

    def RequireID(self) -> str:
        '''👉 The ID property.
        * All items using DYNAMO will have an ID.
        * The ID can be composed - see DYNAMO.'''
        return self.RequireAtt('ID')

    def HasTable(self) -> bool:
        '''👉 Indicates if this item was loaded from a table.'''
        return self.__itemTable is not None

    def SetTable(self, table: ITEM_TABLE):
        '''👉 Sets the table for this item.'''
        self.__itemTable = table

    def _itemTable(self) -> ITEM_TABLE:
        '''👉 Reference to the internal DYNAMO table.'''
        if not self.__itemTable:
            LOG.RaiseException(
                f'Table not defined in item={type(self).__name__}:{self._obj}!')
        return self.__itemTable

    def Delete(self):
        ''' 👉 Deletes the item from its original table.

        Usage:
        1. item=table.Get(key)
        2. item.Delete()
        '''
        self.Require()
        self._itemTable().Delete(self)

    def UpdateItem(self):
        ''' 👉 Updates the item on its original table.

        Usage:
        1. item=table.Get(key);
        2. item.Att(a,1);
        3. item.Update()
        '''
        self.Require()

        # Update the database.
        item = self._itemTable().Update(self)

        # Replace the content, to receive the ItemVersion.
        self._obj = item._obj

    @classmethod
    def FromItems(cls, items: list["ITEM"]):
        '''👉 Transforms a list of DB items into a list of Class instances.'''
        return [
            cls(item)
            for item in items
        ]

    def Reload(self):
        '''👉 Reloads the item for short transactions.'''
        return self._itemTable().Require(
            key=self.RequireID())
