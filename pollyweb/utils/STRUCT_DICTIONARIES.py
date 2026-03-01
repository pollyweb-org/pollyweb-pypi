# 📚 STRUCT

from __future__ import annotations

from .UTILS import UTILS

from .STRUCT_ATTRIBUTES import STRUCT_ATTRIBUTES
from .STRUCT_BASE import STRUCT_BASE


class STRUCT_DICTIONARIES(
    STRUCT_ATTRIBUTES,
    STRUCT_BASE
): 
    

    def items(self):
        '''👉 Returns the items of the internal dictionary.
        
        Example:
            ```python
            obj = STRUCT({'a': 1, 'b': 2})
            print(obj.items())
            # Output: dict_items([('a', 1), ('b', 2)])
            ```

        Example using a for loop:
            ```python
            obj = STRUCT({'a': 1, 'b': 2})
            for key, value in obj.items():
                print(key, value)
            # Output:
            # a 1
            # b 2
            ```

        '''
        
        # Ensure the object has content.
        self.Require()
        obj = self.Obj()

        # Ensure the object is a dictionary or a STRUCT.
        UTILS.AssertIsAnyType(obj, [dict, STRUCT_BASE])

        # Return the items of the internal dictionary.
        obj:dict = obj
        return obj.items()
    
