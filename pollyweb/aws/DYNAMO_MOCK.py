from typing import Union
from pollyweb.utils.DIRECTORY import DIRECTORY
from DYNAMO_MOCK_TABLE import DYNAMO_MOCK_TABLE
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.LOG import LOG
from DYNAMO_BASE import DYNAMO_BASE, DYNAMO_BASE_TABLE
from pollyweb.utils.UTILS import UTILS
from pollyweb.utils.LOG import LOG


class DYNAMO_MOCK(DYNAMO_BASE):
    ''' 👉 Mocked table manager. '''

    ICON:str = '🪣'


    def __init__(self, alias:str=None, keys:list[str]=None) -> None:
        super().__init__(alias=alias, keys=keys)
        self._table = None


    _activeDomain:str = '*'
    _domains:dict[str,dict[str,DYNAMO_MOCK_TABLE]] = {'*': {}}


    @classmethod
    def ResetMock(cls):
        DYNAMO_MOCK._activeDomain = ''
        DYNAMO_MOCK._domains = {}


    @classmethod
    def SetMockDomain(cls, domain:str):
        DYNAMO_MOCK._activeDomain = domain


    def OnStream(self, handler:object):
        '''👉 Sets the placeholder for a streaming event'''
        if handler != None:
            self.Table().OnStream = handler


    @classmethod
    def MockTable(cls, 
        table:str, 
        items:list[dict[str,any]], 
        domain:str
    ):
        '''👉 Appends items to a mocked table.'''

        # Default to the active domain.
        if domain == None and DYNAMO_MOCK._activeDomain != None:
            domain = DYNAMO_MOCK._activeDomain

        ##LOG.Print(f'@(domain={domain}, table={table}, items={items})')
        
        # Register the domain, if necessary.
        ##LOG.Print(f'@.MOCK_DYNAMO._domains={MOCK_DYNAMO._domains}')
        if domain not in DYNAMO_MOCK._domains:
            DYNAMO_MOCK._domains[domain] = {}
        _domain = DYNAMO_MOCK._domains[domain]

        # Register the table, if necessary.
        if table not in _domain:
            _table = DYNAMO_MOCK_TABLE(table)
            _domain[table] = _table
        _table = _domain[table]

        # Verify if all items have an ID.
        for obj in items:
            if 'ID' not in obj:
                LOG.RaiseValidationException(f'ID attribute missing in: {obj}')

        # Add the items.
        _table.Append(items)

    
    def Table(self) -> DYNAMO_BASE_TABLE:
        '''👉 Mocked table.'''

        # Check the cache.
        if self._table:
            return self._table
        
        # Require an alias.
        if UTILS.IsNoneOrEmpty(self._alias):
            LOG.RaiseValidationException('Set the alias to use a table!')
        
        # Get the active domain.
        activeDomain = DYNAMO_MOCK._activeDomain
        if UTILS.IsNoneOrEmpty(activeDomain):
            LOG.RaiseValidationException('Set an active domain first!')
        
        domains = DYNAMO_MOCK._domains
        if activeDomain not in domains:
            domains[activeDomain] = {}
        domain = domains[activeDomain]
        
        # Get the mocked table.
        if self._alias not in domain:
            #LOG.ValidationException(f'First, mock table [{self._alias}] on domain [{activeDomain}].')
            domain[self._alias] = DYNAMO_MOCK_TABLE(self._alias)
        table = domain[self._alias]

        # Add to cache an return.
        self._table = table
        return self._table
    

    @classmethod
    def MockStream(cls, items:list):
        '''👉 Returns a mocked DynamoDB stream.'''
        return DYNAMO_MOCK_TABLE.MockStream(items=items)
        

    def MatchCount(self, count:int, msg:str=None):
        '''👉 Checks the number of items in the table.'''
        existing = len(self.GetAll())
        if existing != count:
            from NLWEB import NLWEB
            domain = NLWEB.CONFIG().RequireDomain()
            LOG.RaiseException(
                f'Count mismatch on table={self._alias} of domain=({domain})!',
                f'{count} items expected',
                f'but found {existing}!', 
                f'{msg=}')
    

    def FirstMock(self):
        '''👉 Returns the first item in the table.'''
        from ITEM import ITEM 
        return ITEM(self.GetAll()[0])
    

    def LastMock(self):
        '''👉 Returns the last item in the table.'''
        from ITEM import ITEM 
        items = self.GetAll()
        return ITEM(items[-1])
    

    def DumpAll(self):
        '''👉 Prints the items.'''
        LOG.Print(f'@(alias={self._alias})')
        for item in self.GetAll():
            LOG.Print(f'  - {item}')
    

    def DumpIDs(self):
        '''👉 Prints the item IDs.'''
        domain = DYNAMO_MOCK._activeDomain
        LOG.Print(f'@', f'table= {self._alias}', f'{domain=}')

        items = [x.RequireID() for x in self.GetAll()]
        items.sort()
        
        LOG.Print(f'@:', items)


    @classmethod
    def DumpToDir(cls, dir:DIRECTORY=None):
        LOG.Print(cls.DumpToDir, dict(
            dir= dir, 
            domains= DYNAMO_MOCK._domains.keys()))

        if dir == None:
            dir = LOG.GetLogDir().GetSubDir('DYNAMO').Touch()

        for d in DYNAMO_MOCK._domains:
            tables = DYNAMO_MOCK._domains[d]
            domain = dir.GetSubDir(d).Touch()

            for t in tables:
                items = tables[t]._Items()
                #items = list(tables[t]._Items().values())
                domain.GetFile(f'{t}.yaml').WriteYaml(items)

        dir.DeleteIfEmpty()


    def DumpAllIDs(self):
        '''👉 Prints the item IDs.'''
        for domain in DYNAMO_MOCK._domains:
            from NLWEB import NLWEB
            NLWEB.AWS().DYNAMO().SetMockDomain(domain)
            NLWEB.AWS().DYNAMO(self._alias).DumpIDs()


    def Require(self, key:Union[str,int,STRUCT,dict[str,str]]):
        #try:
            return super().Require(key)
        #except ValidationException as e:
        #    self.DumpIDs()
        #    self.DumpAllIDs()
        #    self.DumpToFile()
        #    raise