# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations
from pollyweb import LOG


from TALK_BASE import TALK_BASE


class TALK_PARSE(TALK_BASE):
    '''😃 Parses a script into a JSON structure.

    Methods:
    -------
    * `ParseScript(script)`: loads the script in JSON 

    Script example:
    --------------
        💬|Order:
        - SHARE|pollyweb.org/PROFILE/NAME/FRIENDLY
        - RUN|Items
        - CHARGE|{amount}
        - INFO|Wait...

        Items:
        - INT|Product code?
        - CONFIRM|{confirm}
        - REPEAT|Anything else?
    '''
   
    
    # ✅ DONE
    def ParseScript(self, script:str|list[str]):
        '''👉 Loads a script into the Groups[].'''

        from pollyweb import UTILS
        UTILS.AssertIsAnyType(script, options=[str, list])
        
        if type(script) == str:
            lines = script.splitlines()
        elif type(script) == list:
            lines = script

        for line in lines:
            self._parseLine(line)
        return self


    # ✅ DONE
    def _parseLine(self, line:str):
        '''👉 Parses a single line.'''
        ##LOG.Print(f'TALK._parseLine(line={line})')

        # Remove trailing comments.
        line = line.split('#')[0]

        # Remove leading and trailing white spaces.
        line = line.strip()
        
        if line.startswith('💬') and line.endswith(':'):
            # MENU, e.g.: 💬|Buy:
            parts = line.split('|')
            title = parts[1].replace(':', '').strip()
            self._addGroup(title, 'TOP')

        elif line.startswith('- '):
            # STEP, e.g.: - INT|Product code?
            raw = line.replace('- ', '').strip().split('|')

            # Calculate the next zero-based ID
            # e.g., '2.0' is the 1st step of the 3rd group.
            group = self.Last('Groups')
            next = group.Size('Steps')
            id = f"{group.RequireAtt('ID')}.{next}"

            step = {
                'ID': id,
                'Type': 'STEP',
                'Parts': raw
            }
            group.AppendToAtt('Steps', [step])

        elif line.endswith(':'):
            # PROC, e.g.: Items:
            title = line.replace(':', '').strip()
            self._addGroup(title, 'PROC')       


    def _addGroup(self, title:str, type:str):

        # Block duplicate groups.
        existing = self.GetStruct('Groups').First('Title', equals=title)
        if not existing.IsMissingOrEmpty():
            LOG.RaiseException(f'Group already added: {title}!')
        
        # Add the group.
        ##LOG.Print(f"TALK.PARSE._addGroup(): 1.Groups={self['Groups']}")
        self.AppendToAtt('Groups', { 
            'ID': str(self.Size('Groups')),
            'Title': title,
            'Type': type,
            'Steps': []
        })
        ##LOG.Print(f"TALK.PARSE._addGroup(): 2.Groups={self['Groups']}")
