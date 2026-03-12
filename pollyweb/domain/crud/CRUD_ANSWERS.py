from typing import Union
from CRUD_BASE import CRUD_BASE
from CRUD_ENTITY import CRUD_ENTITY
from CRUD_SESSION import CRUD_SESSION
from CRUD_WALLET_ITEM import CRUD_WALLET_ITEM
from HOST_SESSION import HOST_SESSION
from PROMPT import PROMPT
from NLWEB import NLWEB
from pollyweb import LOG
from PROMPT_REPLY import PROMPT_REPLY
from SESSION import SESSION
from TALK_PROMPT import TALK_PROMPT
from pollyweb import UTILS


class CRUD_ANSWERS(CRUD_SESSION, CRUD_BASE):
    

    @classmethod
    def ShowMenu(cls, session:Union[SESSION, CRUD_SESSION]):
        LOG.Print(f'😃 CRUD.ShowMenu()')

        # Validations.
        UTILS.RequireArgs([session])
        UTILS.AssertIsAnyType(session, [SESSION, CRUD_SESSION])

        # Convert to session interface, if necessary.
        if UTILS.IsType(session, CRUD_SESSION):
            crud:CRUD_SESSION = session
            session = crud.ToInterface()

        # Build the list of options from the model.
        model = cls.MODELS().RequireModel('wallet')

        options = {}
        for group in model.RequireGroups():
            groupTitle = group.RequireTitle()
            options[groupTitle] = '=' + groupTitle    

            groupEntities = group.RequireEntities()
            for entityName in groupEntities:
                entityTitle = groupEntities[entityName]
                options[entityName] = entityTitle

        # Build the prompt.
        prompt = PROMPT.New(
            format= 'ONE',
            options= options,
            message= '😃 How can I help?')

        # Stage the prompt on the database.      
        TALK_PROMPT.Insert(
            stepID= 'CRUD',
            session= session,
            prompt= prompt)
        
        # Request the prompt to the broker.
        NLWEB.ROLES().BROKER().InvokePrompt(
            source= 'ShowMenu@Crud',
            session= session,
            promptID= prompt.RequirePromptID())
  


    @classmethod
    def HandleAnswer(cls, session: HOST_SESSION, reply:PROMPT_REPLY):
        '''👉 Handles a user's reply to a previously sent prompt.'''
        LOG.Print('😃 CRUD.ANSWERS.HandleAnswer()', f'reply=', reply)

        crud = cls.FromHostSession(session)

        if reply.GetAnswer() == 'CANCEL':
            return crud.InvokeGoodbye()

        prompt = TALK_PROMPT.RequirePrompt(
            promptID= reply.RequirePromptID())
        
        LOG.Print('😃 CRUD.ANSWERS.HandleAnswer: prompt=',  prompt)

        stepID = prompt.RequireStepID()

        if stepID == 'CRUD':
            # The user selected one of the entities types in the main menu.
            return crud._HandleReplyToMenu(prompt=prompt, reply=reply)

        elif stepID.startswith('CRUD.Entity/'):
            # On the description of entity type, the user selected Add or View.
            answer = str(reply.GetAnswer())
            answer = prompt.LookupOptionKey(answer)

            if answer == 'ADD':
                # The user wants to add an instance of the entity type.
                return crud._HandleReplyToAddEntity(prompt)
            
            elif answer == 'VIEW':
                # The user wants to view the only instance of the entity type.
                return crud._HandleReplyToViewEntity(prompt)
            
            elif answer == 'VIEW*':
                # The user wants to view one of the instances of the entity type.
                return crud._HandleReplyToViewEntities(prompt)
            
            elif answer == 'MENU':
                # The user wants to go back to the main menu.
                return cls.ShowMenu(crud)
            
            else:
                return LOG.RaiseException(f'Unexpected answer: {answer}')

        elif stepID.startswith('CRUD.Entity.View/'):
            # The user view the property values of an entity instance.

            answer = str(reply.GetAnswer())
            answer = prompt.LookupOptionKey(answer)

            if answer == 'UPDATE':
                # The user wants to change the entity instance.
                return crud._HandleReplyToUpdateEntity(prompt)        
            
            elif answer == 'ANOTHER':
                # The user wants to view another entity instance.
                return crud._HandleReplyToViewEntities(prompt)
            
            elif answer == 'DELETE':
                # The user wants to view another entity instance.
                return crud._HandleReplyToDeleteEntity(prompt)
            
            else:
                LOG.RaiseException(f'Unexpected answer: {answer}')

        elif stepID.startswith('CRUD.Entity.Delete/'):
            # The user selected one of the instances to delete.

            return crud._HandleReplyToConfirmDeleteEntity(
                reply= reply,
                prompt= prompt)

        elif stepID.startswith('CRUD.Entity.View*/'):
            # The user selected one of the instances to view.

            return crud._HandleReplyToViewEntity(
                prompt= prompt, 
                selectedItem= reply.GetAnswer())

        elif stepID.startswith('CRUD.Entity.Add.Confirm/'):
            # The user was informed of the properties that will be asked,
            # and wants to continue with adding a new entity instance.
            return crud._HandleReplyToConfirmAddEntity(prompt)
        
        elif stepID.startswith('CRUD.Entity.Add.Property/'):
            # The user inputted the value of a property of the entity.
            return crud._HandleReplyToEntityAddProperty(
                reply= reply,
                prompt= prompt)
        
        elif stepID.startswith('CRUD.Entity.Edit.Property/'):
            # The user inputted the value of a property of the entity.
            return crud._HandleReplyToEntityEditProperty(
                reply= reply,
                prompt= prompt)
        
        elif stepID.startswith('CRUD.Entity.Add.Summary/'):
            # The looked at the summary of data added, and confirmed or rejected it.
            return crud._HandleReplyToConfirmAddSummary(
                reply= reply,
                prompt= prompt)
        
        elif stepID.startswith('CRUD.Entity.Edit.Summary/'):
            # The looked at the summary of data updated, and confirmed or rejected it.
            return crud._HandleReplyToConfirmEditSummary(
                reply= reply,
                prompt= prompt)
        
        elif stepID == 'CRUD.WhatElse':
            # Nothing else to do on the the entity type, the wants go back home.
            answer = reply.GetAnswer()
            if answer == 'YES':
                return crud.ShowMenu(crud)
            elif answer == 'NO':
                return crud.InvokeGoodbye()
            else:
                return LOG.RaiseException('Unexpected answer!', 'answer:', answer)

        return LOG.RaiseException('To be continued...')


    def _ContinueReply(self, stepID:str, prompt:PROMPT):
        LOG.Print('😃 CRUD.ANSWERS._ContinueReply()', f'prompt=', prompt)

        # Stage the prompt on the database.      
        prompt.VerifyPrompt()
        TALK_PROMPT.Insert(
            stepID= stepID,
            session= self.ToInterface(),
            prompt= prompt)
        
        # Request the prompt to the broker.
        NLWEB.ROLES().BROKER().InvokePrompt(
            source= 'HandleAnswer@Crud',
            session= self.ToInterface(),
            promptID= prompt.RequirePromptID())


    def _HandleReplyToMenu(self, prompt:TALK_PROMPT, reply:PROMPT_REPLY):
        LOG.Print('😃 CRUD.ANSWERS._HandleReplyToMenu()', reply)

        # Process the input.
        entityTitle = reply.RequireAnswer()
        entityName = prompt.LookupOptionKey(entityTitle)
        entity = self.RequireEntity(entityName)
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)
        
        # Build the output.
        message = walletEntity.CalculateMessage()
        options = walletEntity.CalculateOptions()

        showMainMenu = 'Show main menu'
        options['MENU'] = showMainMenu
        default = showMainMenu
        
        # Send the prompt.
        self._ContinueReply(
            stepID= 'CRUD.Entity/'+entityName,
            prompt= PROMPT.New(
                format= 'ONE',
                options= options,
                default= default,
                message= message))
        

    def _HandleReplyToAddEntity(self, prompt:TALK_PROMPT):
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        entityName = stepID.split('/')[1]

        entity = self.RequireEntity(entityName)
        
        # Build the message.
        one = entity.RequireAbout().RequireOne()
        props = entity.RequireHumanPropertyList()
        message = \
            f"**Add {one.lower()}?**\n" + \
            f"{props}\n" + \
            "I'll give you the details as we go.\n" + \
            "😎 Ready?"
        
        # Send the prompt.
        return self._ContinueReply(
            stepID= 'CRUD.Entity.Add.Confirm/'+entityName,
            prompt= PROMPT.New(
                default= 'YES',
                format= 'CONFIRM',
                message= message))


    def _HandleReplyToViewEntity(self, 
        prompt:TALK_PROMPT, 
        selectedItem:str= None, itemID:str= None):
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        entityName = stepID.split('/')[1]
        entity = self.RequireEntity(entityName)
        
        # Get the saved values.
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)

        # Either get the first itemID, or the selected itemID.
        # The About.List property must be a unique index.
        if itemID == None:
            itemID = walletEntity.GetSelectedItemID(selectedItem)

        # Load the item details.
        item = walletEntity.RequireItem(itemID)
        message = item.CalculateViewMessage()
        options = item.CalculateViewOptions()

        showMainMenu = 'Show main menu'
        options['MENU'] = showMainMenu
        default = showMainMenu
        
        # Send the prompt.
        return self._ContinueReply(
            stepID= f'CRUD.Entity.View/{entityName}/{itemID}',
            prompt= PROMPT.New(
                format= 'ONE',
                options= options, 
                default= default,
                message= message))

    
    def _HandleReplyToViewEntities(self, prompt:TALK_PROMPT):
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        entityName = stepID.split('/')[1]

        # Get the wallet entity.
        entity = self.RequireEntity(entityName)        
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)

        # Get the list property with all possible values.
        options = walletEntity.GetListValues()

        # Build the message.
        one = entity.RequireAbout().RequireOne().lower()
        message = f'Which {one}?'
        
        # Send the prompt.
        return self._ContinueReply(
            stepID= f'CRUD.Entity.View*/{entityName}',
            prompt= PROMPT.New(
                format= 'ONE',
                options= options, 
                message= message))


    def _HandleReplyToDeleteEntity(self, prompt:TALK_PROMPT):
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        parts = stepID.split('/')
        entityName = parts[1].strip()
        itemID = parts[2].strip()

        entity = self.RequireEntity(entityName)

        # Build the message.
        one = entity.RequireAbout().RequireOne().lower()
        message = f'Are you sure you want to delete this {one}?'
        
        # Send the prompt.
        return self._ContinueReply(
            stepID= f'CRUD.Entity.Delete/{entityName}/{itemID}',
            prompt= PROMPT.New(
                format= 'CONFIRM',
                default= 'NO',
                message= message))


    def _HandleReplyToConfirmDeleteEntity(self, 
        reply:PROMPT_REPLY, prompt:TALK_PROMPT):
                
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        parts = stepID.split('/')
        entityName = parts[1]
        itemID = parts[2]

        if reply.GetAnswer() == 'NO':
            return self._HandleReplyToViewEntity(
                prompt= prompt,
                itemID= itemID)
        
        if reply.GetAnswer() != 'YES':
            return LOG.RaiseException('Unexpected answer!')
    
        entity = self.RequireEntity(entityName)
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)
        
        # Delete the saved values.
        item = walletEntity.RequireItem(itemID)
        walletEntity.CommitDelete(item)
        wallet.UpdateItem()
        
        # Send the prompt.
        one = entity.RequireAbout().RequireOne()
        message = f'{one} deleted!\nAnything else?'

        return self._ContinueReply(
            stepID= f'CRUD.WhatElse',
            prompt= PROMPT.New(
                format= 'CONFIRM',
                default= 'NO',
                message= message))
    

    def _HandleReplyToUpdateEntity(self, prompt:TALK_PROMPT):
        LOG.Print('😃 CRUD.ANSWERS._HandleReplyToUpdateEntity()', prompt)
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        parts = stepID.split('/')
        entityName = parts[1]
        itemID = parts[2]

        entity = self.RequireEntity(entityName)
        
        # Stage the answer.
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)
        item = walletEntity.RequireItem(itemID)
        
        return self._PromptEditProperty(
            entity= entity, 
            item= item,
            propertyIndex= 0)
        

    def _HandleReplyToConfirmAddEntity(self, prompt:TALK_PROMPT):
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        entityName = stepID.split('/')[1]
        entity = self.RequireEntity(entityName)
        
        return self._PromptAddProperty(
            entity= entity, 
            propertyIndex= 0)
        
    
    def _PromptAddProperty(self, 
        entity:CRUD_ENTITY, 
        propertyIndex:int,
        duplicateIndex:str=None
    ):
        LOG.Print('😃 CRUD.ANSWERS._PromptAddProperty()', 
            f'EntityName={entity.RequireName()}', f'{propertyIndex=}')

        # Build the message.
        entityName = entity.RequireName()
        prop = entity.RequireProperties()[propertyIndex]
        title = prop.RequireTitle()
        details = prop.RequireDetails()
        message = \
            f"**{title}?**\n" + \
            f"🤔 {details}"
        
        options = prop.CalculateOptions(
            language= self.RequireLanguage(), 
            wallet= self.RequireWallet())
        
        # Get the default from duplicate index failures.
        if duplicateIndex != None:
            default = duplicateIndex
        else: 
            default = prop.GetDefault()

        # Send the prompt.
        return self._ContinueReply(
            stepID= f'CRUD.Entity.Add.Property/{entityName}/{propertyIndex}',
            prompt= PROMPT.New(
                default= default,
                format= prop.RequireFormat(),
                options= options,
                message= message))
    

    def _PromptEditProperty(self, 
        entity:CRUD_ENTITY, 
        item: CRUD_WALLET_ITEM,
        propertyIndex:int,
        duplicateIndex:str=None
    ):
        LOG.Print('😃 CRUD.ANSWERS._PromptUpdateProperty()', 
            f'{propertyIndex=}',
            f'instance=', item,
            f'entity=', entity)
        
        # Validations.
        CRUD_ENTITY.AssertClass(entity, require=True)
        CRUD_WALLET_ITEM.AssertClass(item, require=True)

        # Build the message.
        prop = entity.RequireProperties()[propertyIndex]
        title = prop.RequireTitle()
        details = prop.RequireDetails()
        message = \
            f"**{title}?**\n" + \
            f"🤔 {details}"
        
        # Get the current value of the property.
        propName = prop.RequireName()
        
        # Get the default from duplicate index failures.
        if duplicateIndex != None:
            default = duplicateIndex
        else: 
            default= item.RequireAtt(propName)

        # Build the options.
        external = prop.GetExternal()
        if external == None:
            options = prop.GetOptions()
        else:
            # Get the session's language.
            options = external.GetRemoteOptions(
                language= self.RequireLanguage())
        
        # Send the prompt.
        entityName = entity.RequireName()
        return self._ContinueReply(
            stepID= f'CRUD.Entity.Edit.Property/{entityName}/{item.RequireID()}/{propertyIndex}',
            prompt= PROMPT.New(
                default= default,
                format= prop.RequireFormat(),
                options= options,
                message= message))


    def _HandleReplyToEntityAddProperty(self, reply:PROMPT_REPLY, prompt:TALK_PROMPT):
        LOG.Print('😃 CRUD.ANSWERS._HandleReplyToEntityAddProperty()',
            'reply=', reply)
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        parts = stepID.split('/')
        entityName = parts[1]
        propertyIndex = int(parts[2])

        entity = self.RequireEntity(entityName)
        props = entity.RequireProperties()
        prop = props[propertyIndex]

        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)

        # Stage the answer.
        if prompt.RequireFormat() == 'INFO':

            # Get the repeated value.
            answers = walletEntity.StagedAnswers(self)
            duplicateIndex = answers[prop.RequireName()]

            # Repeat the property.
            return self._PromptAddProperty(
                entity= entity, 
                propertyIndex= propertyIndex, 
                duplicateIndex= duplicateIndex)

        # Stage the value before checking the index,
        # this is to repeat with the duplicate value.
        walletEntity.StageAnswer(
            session= self,
            property= prop,
            reply= reply)
        
        # Check if it's an unique index
        deplicateMessage = walletEntity.CalculateDuplicateMessage(
            prop= prop,
            reply= reply)

        if deplicateMessage != None:
            # Reject the change.
            return self._ContinueReply(
                stepID= f'{stepID}',
                prompt= PROMPT.New(
                    format= 'INFO',
                    message= deplicateMessage))
        
        wallet.UpdateItem()

        # Get the next property index.
        nextIndex = entity.CalculateNextIndex(
            index= propertyIndex,
            stage= walletEntity.StagedAnswers(self))

        # Check if there are more properties.
        if nextIndex != -1:
            
            # Move to the next property.
            return self._PromptAddProperty(
                entity= entity, 
                propertyIndex= nextIndex)
    
        # Compose the message.
        message = walletEntity.CalculateConfirmMessage(self)
        
        # Send the prompt summarized.
        return self._ContinueReply(
            stepID= f'CRUD.Entity.Add.Summary/{entityName}',
            prompt= PROMPT.New(
                format= 'CONFIRM',
                default= 'YES',
                message= message))
        

    def _HandleReplyToEntityEditProperty(self, reply:PROMPT_REPLY, prompt:TALK_PROMPT):
        LOG.Print('😃 CRUD.ANSWERS._HandleReplyToEntityEditProperty()',
            'reply=', reply)
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        parts = stepID.split('/')
        entityName = parts[1]
        itemID = parts[2]
        propertyIndex = int(parts[3])

        # Stage the answer.
        entity = self.RequireEntity(entityName)
        answer= reply.GetAnswer()
        props = entity.RequireProperties()
        prop = props[propertyIndex]
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)
        item = walletEntity.RequireItem(itemID)

        # Stage the answer.
        if prompt.RequireFormat() == 'INFO':

            # Get the repeated value.
            answers = walletEntity.StagedAnswers(self)
            duplicateIndex = answers[prop.RequireName()]

            # Repeat the property.
            return self._PromptEditProperty(
                item= item,
                entity= entity, 
                propertyIndex= propertyIndex, 
                duplicateIndex= duplicateIndex)
        
        # Stage the value before checking the index,
        # this is to repeat with the duplicate value.
        walletEntity.StageAnswer(
            session= self,
            property= prop,
            reply= reply)

        # Check if it's an unique index
        deplicateMessage = walletEntity.CalculateDuplicateMessage(
            prop= prop,
            reply= reply,
            itemID= itemID)

        if deplicateMessage != None:
            # Reject the change.
            return self._ContinueReply(
                stepID= stepID,
                prompt= PROMPT.New(
                    format= 'INFO',
                    message= deplicateMessage))
        
        # Get the next property index.
        nextIndex = entity.CalculateNextIndex(
            index= propertyIndex,
            item= item, 
            stage= walletEntity.StagedAnswers(self))
        
        # Check if there are more properties.
        if nextIndex != -1:
            
            # Move to the next property.
            return self._PromptEditProperty(
                item= item, 
                entity= entity, 
                propertyIndex= nextIndex)
            
        else: 
            # Compose the message.
            message = walletEntity.CalculateConfirmMessage(self)
            
            # Send the prompt summarized.
            return self._ContinueReply(
                stepID= f'CRUD.Entity.Edit.Summary/{entityName}/{itemID}',
                prompt= PROMPT.New(
                    format= 'CONFIRM',
                    default= 'YES',
                    message= message))
        
    
    def _HandleReplyToConfirmAddSummary(self, 
        reply:PROMPT_REPLY, prompt:TALK_PROMPT):

        LOG.Print('😃 CRUD.ANSWERS._HandleReplyToConfirmAddSummary()',
            'reply=', reply)
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        entityName = stepID.split('/')[1]
        entity = self.RequireEntity(entityName)
        
        # Commit the answers.
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)
        walletEntity.CommitStage(session= self)
        wallet.UpdateItem()    
        
        # Compose the message.
        one = entity.RequireAbout().RequireOne()
        message = \
            f"🥳 {one} added!\n" + \
            "Anything else?"
        
        # Send the prompt summarized.
        return self._ContinueReply(
            stepID= 'CRUD.WhatElse',
            prompt= PROMPT.New(
                format= 'CONFIRM',
                default= 'NO',
                message= message))
    

    def _HandleReplyToConfirmEditSummary(self, reply:PROMPT_REPLY, prompt:TALK_PROMPT):
        LOG.Print('😃 CRUD.ANSWERS._HandleReplyToConfirmEditSummary()',
            'reply=', reply)
        
        # Get the entity from the stepID.
        stepID = prompt.RequireStepID()
        parts = stepID.split('/')
        entityName = parts[1]
        itemID = parts[2]
        entity = self.ENTITIES().RequireEntity(
            modelName= 'wallet',
            entityName= entityName)
                
        # Commit the answers.
        wallet = self.RequireWallet()
        walletEntity = wallet.RequireEntity(entity)
        item = walletEntity.RequireItem(itemID)

        walletEntity.CommitStage(
            session= self,
            item= item)

        wallet.UpdateItem()    
        
        # Compose the message.
        one = entity.RequireAbout().RequireOne()
        message = \
            f"🥳 {one} updated!\n" + \
            "Anything else?"
        
        # Send the prompt summarized.
        return self._ContinueReply(
            stepID= 'CRUD.WhatElse',
            prompt= PROMPT.New(
                format= 'CONFIRM',
                default= 'NO',
                message= message))
    
