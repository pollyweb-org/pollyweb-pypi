# 📚 HOST_TALKER

from __future__ import annotations

from PW_AWS.ITEM import ITEM


class HOST_TALKER(ITEM):
    ''' 🪣 List of talkers to be used by host locators.
    {
        ID: DefaultTalker
        Script: <YAML>
    }
    '''


    def RequireTalkerID(self) -> str:
        return self.RequireStr('ID')
    

    def RequireScript(self) -> str:
        return self.RequireStr('Script')