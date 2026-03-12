from __future__ import annotations

from CRUD_ENTITY import CRUD_ENTITY
from CRUD_SESSION import CRUD_SESSION
from CRUD_WALLET_ITEM import CRUD_WALLET_ITEM
from NLWEB import NLWEB
from pollyweb import LOG
from PROMPT_REPLY import PROMPT_REPLY
from pollyweb import STRUCT
from pollyweb import UTILS


class CRUD_WALLET_ENTITY(STRUCT):


    @classmethod
    def ENTITIES(cls):
        return NLWEB.BEHAVIORS().CRUD().ENTITIES()
    
    @classmethod
    def ITEMS(cls):
        return NLWEB.BEHAVIORS().CRUD().WALLETS().ITEMS()

    @classmethod
    def SESSIONS(cls):
        return NLWEB.BEHAVIORS().CRUD().WALLETS().SESSIONS()


    def __init__(self, obj:any, wallet, entity:CRUD_ENTITY):
        super().__init__(obj)

        # Map the parent entity
        UTILS.AssertIsType(entity, CRUD_ENTITY, require=True)
        self._entity = entity

        # Map the parent wallet
        from CRUD_WALLET import CRUD_WALLET
        UTILS.AssertIsType(wallet, CRUD_WALLET, require=True)
        self._wallet = wallet

    
    def RequireEntity(self):
        return self._entity
    

    def RequireWallet(self):
        from CRUD_WALLET import CRUD_WALLET
        ret:CRUD_WALLET = self._wallet
        return ret


    def RequireItem(self, itemID:str):
        '''👉 Returns an item by ID.'''
        UTILS.Require(itemID, msg= 'ItemID not provided!')

        return self.ITEMS().RequireItem(
            id= itemID, 
            walletEntity= self)

    
    def RequireIndexes(self):
        '''👉 Returns the list of indexes.'''
        self.Default('Indexes', {})
        return self.RequireStruct('Indexes')
    

    def GetListValues(self):
        '''👉 Returns the list property with all possible values.'''

        entity = self.RequireEntity()
        listProp = entity.RequireAbout().GetList()
        rankProp = entity.RequireAbout().GetRank()

        if rankProp == None:
            return self.GetIndexValues(listProp)
        else:
            listPairs = self.GetIndexPairs(listProp)
            rankPairs = self.GetIndexPairs(rankProp)

            tmps:dict[str,list[str]] = {}

            # For each ranking
            for rankKey in rankPairs:
                tmps[rankKey] = []
                # Find the matching display value by ItemID.
                for listKey in listPairs:
                    if rankPairs[rankKey] == listPairs[listKey]:
                        lst = tmps[rankKey]
                        lst.append(listKey)
                        break
                # Sort the subitems
                tmps[rankKey].sort()
            
            # Other the rank values.
            keys = list(tmps.keys())
            keys.sort(reverse=True)

            # Produce the final list.
            ret:list[str] = []
            for key in keys:
                for tmp in tmps[key]:
                    ret.append(tmp)
            return ret


    def GetIndexPairs(self, name:str):
        '''👉 Returns the indexed pair for all items.
        * index1:[a:<uuid1>,b:<uuid2>] -> [a:<uuid1>,b:<uuid2>]
        '''
        indexes = self.RequireIndexes()
        if name not in indexes:
            return []
        index = indexes.GetStruct(name)
        return index


    def GetIndexValues(self, name:str, rank:str=None):
        '''👉 Returns the indexed value for all items.
        * index1:[a:[<uuid1>],b:[<uuid2>]] -> [a,b]
        '''
        index = self.GetIndexPairs(name)
        ret = index.Attributes()
        ret.sort()
        return ret
    

    def GetIndexedItemID(self, name:str, key:str):
        '''👉 Returns the itemID associated with the value on an index.
        * given: index1:[a:[<uuid1>],b:[<uuid2>]]
        * when invoked(index1, a) 
        * then returns <uuid1>
        '''
        indexes = self.RequireIndexes()
        index = indexes.RequireStruct(name)
        ret = index.ListStr(key)[0].strip()
        UTILS.Require(ret)
        return ret
    

    def IsDuplicateIndex(self, prop:str, value:str, itemID:str=None):
        indexes = self.RequireIndexes()
        if prop not in indexes:
            return False
        index = indexes[prop]
        if value not in index:
            return False
        # check if an item exists other then self on the same value key.
        return len([x for x in index[value] if x != itemID]) > 0
    

    def GetSelectedItemID(self, selectedItem:str):
        '''👉 Returns the selected item, or the 1st if there's no selection.'''
        
        if selectedItem == None:
            ret = self.RequireItems()[0]
            UTILS.Require(ret)
            return ret
        
        entity = self.RequireEntity()
        listProperty = entity.RequireAbout().RequireList()

        ret = self.GetIndexedItemID(
            name= listProperty, 
            key= selectedItem)
        
        UTILS.Require(ret)
        return ret
            

    def RequireItems(self):
        self.Default('Items', [])
        return self.ListStr('Items', require=True)
    

    def AddStage(self, sessionID:str):
        return self.AppendToAtt('Sessions', sessionID)
    

    def Count(self):
        '''👉 Returns the number of items in the entity's repository.'''
        return len(self.RequireItems())
    

    def RequireStage(self, sessionID:str):
        stage = self.SESSIONS().GetSession(sessionID)
        UTILS.Require(stage)
        return stage
    

    def StageAnswer(self, 
        reply:PROMPT_REPLY,
        property:STRUCT, session:CRUD_SESSION):
        '''👉️ Adds an answer to the temporary sessions list.'''

        # Validations.
        UTILS.AssertIsType(session, CRUD_SESSION, require= True)
        UTILS.AssertIsType(reply, PROMPT_REPLY, require= True)

        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        UTILS.AssertIsType(property, CRUD_ENTITY_PROPERTY, require= True)
        prop:CRUD_ENTITY_PROPERTY = property
        
        # Context.
        sessionID = session.RequireSessionID()
        stage = self.RequireStage(sessionID)
        
        # Trim text answers.
        answer = reply.GetAnswer()
        if prop.RequireFormat() == 'TEXT':
            answer = str(answer).strip()

        # Save the value.
        name = prop.RequireName()
        stage.GetAtt(name, set= answer)
        stage.UpdateItem()

    
    def StagedAnswers(self, session:CRUD_SESSION):
        '''👉️ Returns the answers in the temporary sessions list.'''
        UTILS.AssertIsType(session, CRUD_SESSION, require= True)

        sessionID = session.RequireSessionID()
        stage = self.RequireStage(sessionID)
        UTILS.Require(stage)
        return stage
        

    def CommitStage(self, 
        session:CRUD_SESSION, item:CRUD_WALLET_ITEM=None):
        '''👉️ Moves the answers in the temporary sessions list into
              the permanent list of items.'''
        
        UTILS.AssertIsType(session, CRUD_SESSION, require=True)
        CRUD_WALLET_ITEM.AssertClass(item)
        
        # Get the staged items.
        sessionID = session.RequireSessionID()
        stage = self.RequireStage(sessionID)
        entity = self.RequireEntity()

        # Get the Item ID.
        if item != None:
            itemID = item.RequireID()
        else:
            itemID = stage.RequireID()

        # Update the index.
        indexes = self.RequireIndexes()
        for prop in entity.RequireProperties():
            name = prop.RequireName()
            
            if prop.RequireUnique() \
            or entity.RequireAbout().GetRank() == name \
            or entity.RequireAbout().GetList() == name:

                # Get the index.
                if name not in indexes:
                    indexes[name] = {}
                index:dict[str,list[str]] = indexes[name]
                
                # Remove the old index key.
                if item != None:
                    oldValue = str(item[name])
                    if oldValue in index:
                        # Remove the ItemID from the index value.
                        lst = index[oldValue]
                        if itemID in lst:
                            lst.remove(itemID)
                        # Remove the index value, if empty.
                        if len(lst) == 0:
                            del index[oldValue]
                    
                # Add the new index key.
                newValue = str(stage[name])
                UTILS.Require(newValue, 'Index values cannot be null!')
                if newValue not in index:
                    index[newValue] = []    
                index[newValue].append(itemID)

        # Add the staged answers into a new item.
        if item == None:

            # Create the item.
            stage['ItemSchema'] = self.RequireEntity().RequireName()
            stage['WalletID'] = self.RequireWallet().RequireID()
            self.ITEMS().InsertItem(stage)

            # Map the ID in the Wallet Entity list.
            itemID = stage.RequireID()
            self.AppendToAtt('Items', [itemID])

        else:
            
            # Copy the property values.
            for prop in entity.RequireProperties():
                name = prop.RequireName()
                item[name] = stage[name]
            item.UpdateItem()

        # Remove the stage answers.
        stage.Delete()
    

    def CommitDelete(self, item:CRUD_WALLET_ITEM):
        '''👉️ Deletes an item and all its indexes.'''

        LOG.Print('😃 CRUD.WALLET.ENTITY()', item)

        CRUD_WALLET_ITEM.AssertClass(item, require=True)
        entity = self.RequireEntity()

        # Update the index.
        itemID = item.RequireID()
        indexes = self.RequireIndexes()
        for prop in entity.RequireProperties():
            LOG.Print('😃 CRUD.WALLET.ENTITY: Prop', prop)
            
            # Get the index.
            name = prop.RequireName()
            if name not in indexes:
                LOG.Print('😃 CRUD.WALLET.ENTITY: no index')
                continue
            index:dict[str,list[str]] = indexes[name]
            
            # Remove the old index key.
            oldValue = str(item[name])
            if oldValue not in index:
                LOG.Print('😃 CRUD.WALLET.ENTITY: no value')
                continue

            # Remove the ItemID from the index value.
            lst = index[oldValue]
            if itemID in lst:
                LOG.Print('😃 CRUD.WALLET.ENTITY: itemID deleted', itemID)
                lst.remove(itemID)

            # Remove the index value, if empty.
            if len(lst) == 0:
                LOG.Print('😃 CRUD.WALLET.ENTITY: index deleted', oldValue)
                del index[oldValue]
                
        # Remove the item index.
        self.RemoveItem('Items', itemID)
        LOG.Print('😃 CRUD.WALLET.ENTITY.Items:', self)

        # Remove the item.
        item.Delete()


    def CalculateConfirmMessage(self, session:CRUD_SESSION):
        '''👉️ Calculates a confirmation message to commit the state values.'''
        UTILS.AssertIsType(session, CRUD_SESSION, require= True)

        # Get context.
        entity = self.RequireEntity()
        props = entity.RequireProperties()

        # Get all staged answers in the session.
        answers = self.StagedAnswers(session)
        
        # Compile a list of relevant answers.
        humanProperties = []
        for prop in props:

            # Hide OTPs from the final confirmation.
            if prop.RequireFormat() == 'OTP':
                continue

            # Hide dependent properties not asked.
            dependency = prop.GetIf()
            if not UTILS.IsNoneOrEmpty(dependency):
                if answers[dependency.RequireName()] != 'YES':
                    continue

            # Prepare the data.
            title = prop.RequireTitle()
            name = prop.RequireName()
            answer = answers.GetAtt(name)

            # Convert confirmations into ?:Yes/No
            if prop.RequireFormat() == 'CONFIRM':
                answer = str(answer)
                answer = answer.replace('YES', 'Yes')
                answer = answer.replace('NO', 'No')
                humanProperties.append(f'- {title}? {answer}')
                continue
            
            # Transform multi-line text into comma-separated.
            if prop.RequireFormat() == 'TEXT':
                answer = str(answer)
                answer = answer.strip().replace('\n', ', ')

            # Avoid presenting 'None' to users.
            if str(answer) == 'None':
                LOG.RaiseException('Presenting "None" is a bad practice!')

            # Finish the line.
            humanProperties.append(f'- {title}: {answer}')

        # Merge all lines.
        humanProperties = '\n'.join(humanProperties)
    
        # Compose the message.
        one = entity.RequireAbout().RequireOne()

        message = \
            f"**Thanks! All good?**\n" + \
            f"👀 Here are the {one.lower()} details:\n" + \
            humanProperties + "\n" + \
            f"Is that correct?"
        
        return message
    

    def CalculateMessage(self):
        '''👉 Build the message for an entity.'''

        entity = self.RequireEntity()
        about = entity.RequireAbout()
        message = about.RequireDetails().strip() \
            + '\n🙂 What should we do?'
        return message
    

    def IsMissingDependencies(self):
        '''👉 Indicates if there are internal dependencies missing.'''

        entity = self.RequireEntity()

        # Discover dependencies.
        dependencies = []
        for prop in entity.RequireProperties():
            internal = prop.GetInternal()
            if internal == None: continue
            dependency = internal.RequireFrom()
            dependencies.append(dependency)

        # Check if dependencies are missing.
        for dependency in dependencies:
            walletEntity = self.RequireWallet().RequireEntityByName(dependency)
            count = walletEntity.Count()
            if count == 0: 
                return True

        return False


    def CalculateOptions(self):
        '''👉 Build the options for an entity.'''

        entity = self.RequireEntity()
        
        about = entity.RequireAbout()
        one = about.RequireOne()
        count = self.Count()

        options = {}

        # Append the VIEW 
        if count == 1: 
            options['VIEW'] = f'View {one.lower()}'

        elif count > 1: 
            many = about.RequireMany()
            options['VIEW*'] = f'View {many.lower()}'

        # Append the ADD 
        hide = self.IsMissingDependencies()
        if not hide:

            format = entity.RequireAbout().RequireFormat()
            if (format == 'ONE' and count == 0) \
            or (format == 'MANY'):
                
                options['ADD'] = f'Add {one.lower()}'

        return options
    

    def CalculateDuplicateMessage(self, 
        prop:STRUCT, 
        reply: PROMPT_REPLY, 
        itemID:str= None):

        from CRUD_ENTITY_PROPERTY import CRUD_ENTITY_PROPERTY
        prop:CRUD_ENTITY_PROPERTY = prop

        entity = self.RequireEntity()

        # Check if it's an unique index
        if not prop.RequireUnique(): 
            return None
        
        # Check if it's duplicated.
        if not self.IsDuplicateIndex(
            prop= prop.RequireName(),
            value= reply.GetAnswer(),
            itemID= itemID
        ): 
            return None
        
        # If we got here, it's a duplicate index.
        name = prop.RequireTitle().lower()
        one = entity.RequireAbout().RequireOne().lower()
        message = \
            f'Sorry, I cannot use that {name}!\n' + \
            f'There is already another {one} with the same {name}.'
        
        return message
    


    def GetAllItems(self):
        '''👉 Returns all items of the entity schema.'''
        schema = self.RequireEntity().RequireName()
        items = self.ITEMS()._Table().Query('ItemSchema', equals=schema)
        return items
    