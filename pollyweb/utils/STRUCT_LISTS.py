# 📚 STRUCT

from __future__ import annotations
from typing import Union

from .LOG import LOG
from .UTILS import UTILS
from .LOG import LOG

from .STRUCT_ATTRIBUTES import STRUCT_ATTRIBUTES
from .STRUCT_BASE import STRUCT_BASE


class STRUCT_LISTS(
    STRUCT_ATTRIBUTES,
    STRUCT_BASE
): 
    


    def RemoveItem(self, att:str, item:any):
        '''👉 Removes an item from a list attribute,'''
        items:list = self.Obj()[att]
        items.remove(item)
    


    @classmethod
    def FromStructs(cls, 
        structs:Union[list[STRUCT_BASE], dict[str, STRUCT_BASE], STRUCT_BASE]
    ):
        ''' 👉 Casts a struct into a list of the class type.
        * class A(STRUCT); A.CastStructs([$:STRUCT]) -> [$:A]
        '''
        
        # Get the object inside any struct.
        if isinstance(structs, STRUCT_BASE):
            structs = structs.Obj()

        # Convert a dictionary into a list.
        if isinstance(structs, dict):
            structs = list(structs.values())

        # Ensure the object is a list.
        if not isinstance(structs, list):
            LOG.RaiseValidationException('A list was expected!')

        # Cast the list of structs.
        return [
            cls(struct)
            for struct in structs
        ]
    


    def Last(self, att:str=None):
        ''' 👉 Returns the last element of a list attribute.
        * Source: https://www.geeksforgeeks.org/python-how-to-get-the-last-element-of-list/
        * $([1,2,3]).Last() -> 3
        * $([1]).Last() -> 1
        * $([]).Last() -> Exception!
        * $(None).Last() -> Exception!
        * $({}).Last() -> Exception!
        '''
        from .STRUCT import STRUCT

        if att != None:
            obj = self.GetAtt(att)
        else:
            obj = self.Obj()

        if obj == None:
            LOG.RaiseValidationException('Empty object!')
        elif type(obj) != list:
            LOG.RaiseValidationException('A list was expected!')
        
        array:list[any] = obj
        if len(array) == 0:
            LOG.RaiseValidationException('The list is empty!')
        
        return STRUCT(array[-1])
    


    def AppendToAtt(self, att:str, items:Union[list[any],any]):
        ''' 👉 Adds an object to a list attribute. 
        * ${}.AppendToAtt(a, [1]) -> ${a:[1]} (creates the list, if necessary)
        * ${a:[1]}.AppendToAtt(a, [2]) -> ${a:[1,2]} (appends to an existing list)
        * ${a:[1,2]}.AppendToAtt(a, [2]) -> ${a:[1,2]} (dedups existing items)
        * ${a:[1,2]}.AppendToAtt(a, [2,3,4]) -> ${a:[1,2,3,4]} (adds multiple)
        '''
        from .STRUCT import STRUCT

        self.Default(att, default=[])
        array:list[any] = self.GetAtt(att)
        if items != None:

            # Convert a single item into a list, if necessary.
            if not isinstance(items, list):
                items = [items]

            # Iterate the given list.
            for item in items:
                if isinstance(item, STRUCT):
                    val = item#.Obj()
                    if val == None:
                        raise Exception('Cannot append a None object!')
                    if val not in array:
                        array.append(val)
                else:
                    if item == None:
                        raise Exception('Cannot append a None item!')
                    if item not in array:
                        array.append(item)

        return self
        

    
    def Append(self, any:any):
        ''' 👉 Adds an object to itself, assuming it's a list. Returns the list. 
        * $(None).Append(1) -> $([1])
        * $([]).Append(1) -> $([1])
        * $([1]).Append(1) -> $([1,1])
        * $({}).Append(1) -> Exception!
        '''
        obj = self.Obj()
        
        if obj == None:
            self.Obj([])
            lst:list = self.Obj()    
        elif not isinstance(obj, list):
            LOG.RaiseValidationException('A list was expected!')
        else:
            lst:list = obj

        lst.append(any)
        return self


    
    def Any(self, att:Union[str,dict[str,any]]=None, equals:str=None) -> bool:
        ''' 👉 Indicates if an any or one specific element exists.
        * att: name of the attribute to search in the list of objects;
        * equals: expected value of the attribute.

        Without att:
        * $[].Any() -> False
        * $[1,2,{}].Any() -> True
        * ${}.Any() -> Untested behaviour!
        
        With att as string:
        * $[{x:1},{x:2},{x,3}].Any(x, equals=2) -> True
        * $[{x:1},{x:2},{x,3}].Any(x, equals=5) -> False
        * $[{x:1},{x:2},{x,3}].Any(y, equals=1) -> False
        * $[].Any(y, equals=1) -> False
        * ${}.Any(x, equals=y) -> Untested behaviour!

        With att as a dictionary:
        * $[{x:1},{x:2}].Any({x:1}) -> True
        * $[{x:1},{x:2}].Any({x:3}) -> False
        * $[{x:1},{x:2}].Any({y:1}) -> False
        '''
        ##LOG.Print(f'STRUCT.Any(att={att}, equals={equals})')

        # For an empty list, it's always false.
        if len(self.GetList()) == 0:
            return False

        # If att is None, return True if the list has elements.
        if att == None:
            return True
        
        # If att is a string, look for an element where the attribute equals something.
        elif isinstance(att, str):
            UTILS.RequireArgs([att, equals])
            return not self.First(att, equals= equals).IsMissingOrEmpty()
        
        # If att is a dictionary, look to match all given attributes.
        elif isinstance(att, dict):
            for item in self.Structs():
                ##LOG.Print(f'STRUCT.Any(att={att}, equals={equals})')

                itemOK = True
                for key in list(att.keys()):

                    if not item.ContainsAtt(key):
                        itemOK = False
                        break

                    if item.GetAtt(key) != att[key]:
                        itemOK = False
                        break

                if itemOK == True:
                    return True # This item matches all atts, nice!
                
                if itemOK != True:
                    continue # Not lucky, let's see the next item.
                    
            # Sorry, no item matches all atts - better luck next time!
            return False
        
        # Otherwise, raise an exception.
        else:
            LOG.RaiseValidationException(f'Unexpected att type: [{type(att)}]!')
    


    def Pop(self, att:str, msg:str=None):
        ''' 👉 Removes and returns the top element of a list. 
        * s=$([1,2,3]).Pop() -> $3, s==$[1,2]
        * s=$([]).Pop() -> Exception!
        '''
        from .STRUCT import STRUCT

        calls = self.GetList(att)
        
        if len(calls) == 0:
            return None
            LOG.RaiseValidationException(
                'Cannot pop an empty list!',
                'msg=', msg)

        item = calls.pop()
        return STRUCT(item)



    def Where(self, 
        att:str, 
        equals:str, 
        part:str=None
    ) -> list[Union["STRUCT_LISTS", any]]:
        LOG.RaiseValidationException('Unusable, not tested!')
    
        ''' 👉 Loops a list to find any children with a matching property. 

        Without part:
        * $[{a:x,b:1}, {a:y,b:2}, {a:y,b:3}].Where(a, equals=y) -> [${a:y,b:2}, ${a:y,b:3}]
        * $[{a:x,b:1}].Where(a, equals=y) -> []
        * $None.Where(a, equals=y) -> []

        With part:
        * $[{a:x,b:1}, {a:y,b:2}, {a:y,b:3}].Where(a, equals=y, part=b) -> [$2, $3]
        '''
        list = []
        for child in self.Structs():
            if child.GetAtt(att) == equals:
                list.append(child)

        # Get parts.
        if part == None:
            return list
        
        parts = []
        for item in list:
            struct = self(item).RequireAtt(part)
            parts.append(struct)

        return parts





    def ListStr(self, 
        att:str=None, 
        part:str=None, 
        require:bool=False, 
        msg:str=None,
        noHierarchy: bool= False
    ) -> list[str]:
        """ 👉 Returns a list of values referenced by the property. 
        * ${[1,x]}.ListStr() -> ['1','x']
        * ${a:[1,x]}.ListStr() -> Exception!
        * ${a:[1,x]}.ListStr(att=b) -> []
        * ${a:[1,x]}.ListStr(att=a) -> ['1','x']
        """
        ret:list[str] = []
        for x in self.GetList(
            att= att, 
            part= part, 
            mustExits= require, 
            noHierarchy= noHierarchy
        ):

            if isinstance(x, int):
                x = str(x)

            if isinstance(x, str):
                x = x.strip()

            if not isinstance(x, str):
                return LOG.RaiseException(
                    f'Invalid type for ListStr x={type(x).__name__}:{x}', msg)
                
            ret.append(x)
            
        return ret


    def RequireList(self,
        att:str=None,
        part:str=None,
        msg:str=None,
        noHierarchy: bool= False
    ) -> list[any]:
        ''' 👉 Returns a list of values referenced by the property.
        
        Without att:
        * $None.RequireList() -> Exception!
        * $[].RequireList() -> Exception!
        * $[1,2,3].RequireList() -> [1,2,3]
        * $[{},{},{}].RequireList() -> [{},{},{}]

        With att:
        * ${a:[1,2,3]}.RequireList(a) -> [1,2,3]
        * ${a:[{},{}].RequireList(a) -> [{},{}]
        * ${a:[{},{}].RequireList(b) -> Exception!
        '''
        return self.GetList(
            att= att, 
            part= part, 
            mustExits= True, 
            msg= msg,
            noHierarchy= noHierarchy)


    def GetList(self, 
        att:str=None, 
        part:str=None, 
        mustExits:bool=False, 
        msg:str=None,
        noHierarchy: bool= False,
        itemType: type = None
    ) -> list[any]:
        """ 👉 Returns a list of values referenced by the property. 

        Without att:
        * $None.List() -> [] (safe missing)
        * $[].List() -> [] (reads root)
        * $[1,2,3].List() -> [1,2,3] (reads root)
        * $[{},{}].List() -> [{},{}] (reads root)

        With att:
        * ${a:[1,2,3]}.List(a) -> [1,2,3] (reads attributes)
        * ${a:[{},{}]}.List(a) -> [{},{}] (reads attributes)
        * ${a:[{},{}]}.List(b) -> [] (safe missing)

        With part:
        * ${a:[{x:1,y:5},{x:2,y:6}]}.List(a,part=x) -> [1,2] (reads atts of elements)

        Exceptions, not a list:
        * $({}).List()
        * $({'a':1}).List('a')
        """

        from .STRUCT import STRUCT

        # Get elements.
        if att != None:
            lst = self.GetAtt(att, noHierarchy=noHierarchy)
        else:
            lst = self.Obj()
            
        if lst == None:
            if mustExits == True:
                if att != None:
                    LOG.RaiseValidationException(
                        f'List [{att}] is required!', msg,
                        f'None was found on internal object=', self)
                else:
                    LOG.RaiseValidationException(
                        f'The struct can not be None, it should be a list!')
            lst = []

        if type(lst) != list:
            LOG.RaiseValidationException(
                f'A list was expected', 
                f'but found type=({type(lst).__name__}) for lst=({lst})!',
                f'self=', self)

        # Get parts.
        parts = lst
        if part != None:
            parts = []
            for item in lst:
                struct = STRUCT(item).RequireAtt(part)
                parts.append(struct)
                
        # Verify the type.
        if itemType != None:
            for item in lst:
                if not isinstance(item, itemType):
                    LOG.RaiseValidationException(
                        f'Invalid item type={type(item).__name__}!',
                        f'Expected={itemType.__name__}!',
                        f'Item={item}',
                        f'part={part}',
                        f'att={att}',
                        f'parts={parts}',
                        f'lst={lst}',
                        f'self=',self)

        return parts



    
    def Size(self, att:str=None) -> int:
        ''' 👉 Returns the size of the internal list or a list property. 
        * $[].Size() -> 0
        * $[1,2,3].Size() -> 3
        * $[{},{},{}].Size() -> 3
        * ${...}.Size() -> Untested behaviour!
        * ${a:[]}.Size(a) -> 0
        * ${a:[{},{},{}]}.Size(a) -> 3
        * ${a:{...}}.Size(a) -> Untested behaviour!
        '''
        
        if att != None:
            list = self.GetList(att, mustExits=True)
        else:
            list = self.GetList(mustExits=True)
        return len(list)


    def RemoveFirst(self, 
        att:str=None, 
        equals:Union[str,float,int,bool]=None
    ):
        ''' 👉 Loops a list to find and remove a child with a matching property. 
        * $[{a:x,b:1}], {a:y,b:2}, {a:y,b:3}].RemoveFirst(a, equals=y) -> $[{a:x,b:1}], {a:y,b:3}]
        * $[].RemoveFirst(a, equals=y) -> $[]
        * ${...}.RemoveFirst(a, equals=y) -> Exception!
        '''
        
        lst = self.Obj()
        
        if type(lst) != list:
            LOG.RaiseValidationException('The inner object should be a list!')
        
        if att == None:
            lst.pop(0)

        elif att != None:
            UTILS.RequireArgs([att, equals])
            for index, value in enumerate(lst):
                if value[att] == equals:
                    lst.pop(index)
                    return self
            
        return self
            

    def First(self, 
        att:str=None, 
        equals:Union[str, float, int, bool]=None, 
        require:bool=False
    ):
        ''' 👉 Loops a list to find the first child with a matching property. 

        Without att:
        * $[{a:1},{b:2}].First() -> ${a:1}
        * $None.First() -> ${}

        With att:
        * $[{a:x,b:1}, {a:y,b:2}, {a:y,b:3}].First(a, equals=y) -> ${a:y,b:2}
        * $[{a:x,b:1}].First(a, equals=y) -> ${}
        * $None.First(a, equals=y) -> ${}
        '''
        from .STRUCT import STRUCT

        if self.IsMissingOrEmpty():
            if require == True:
                LOG.RaiseValidationException(f'Given an empty object/list to searching for ({att})=({equals})!')
            else:
                return STRUCT({})
            
        else:
            for child in self.Obj():
                struct = STRUCT(child)
                # Without att
                if att == None and equals == None:
                    return struct
                # With att
                if struct.GetAtt(att) == equals:
                    return struct
                
            if require == True:
                LOG.RaiseValidationException(
                    f'({att})=({equals}) not found in={self.Raw()}!')
            else:
                return STRUCT({})
    
    
