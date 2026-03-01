  
from __future__ import annotations
from typing import Union
from pollyweb import UTILS
from pollyweb import LOG


class PROMPT_OPTION(str):
    '''https://quip.com/CDrjAxNKwLpI/-Prompt#temp:C:KSce8ac7c8cdfd54249991baa11c'''


    @classmethod
    def ParseOptions(cls, options:any) -> Union[list[str],dict]:
        '''👉️ Parses a string into a list of option objects:
        * "[a,b]" -> [a,b]
        * [a,b] -> [a,b]
        * "[1:a,2:b]" -> ['1:a','2:b']
        * {a:x,b:y} -> Exception
        * None -> None

        '''
        if options == None:
            return None

        any = UTILS.Copy(options)

        if isinstance(any, str):
            strs = any.replace('[','').replace(']','').split(',')
            ret = []

            # Remove spaces.
            for s in strs:
                ret.append(s.strip())

            # Verify duplicates.
            for s in ret:
                if ret.count(s) > 1:
                    LOG.RaiseValidationException(f'Option ({s}) should not be repeated!')
                
            # return.
            return ret

        elif isinstance(any, list):
            ret = []
            for item in any:
                
                # Convert ints to str.
                if isinstance(item, int):
                    item = str(item)

                # Verify is all are strings.
                UTILS.AssertIsAnyType(item, [str, dict])

                # Remove spaces from strings.
                if isinstance(item, str):
                    item = str(item).strip()

                # Add to return list.
                ret.append(item)
                
            # Verify duplicates.
            for s in ret:
                if ret.count(s) > 1:
                    LOG.RaiseValidationException(f'Option ({s}) should not be repeated!')

            return ret
        
        
        elif isinstance(any, dict):
            return any
            # This was to transform a dictionary into 'key:value'.
            # The prob is that ':' becomes a special character.
            # It's better to return an dictionary or a list.
            ret = []
            for key in any:
                ret.append(f'{key}:{any[key]}')
            return ret

        LOG.RaiseValidationException(
            f'Unexpected type of Options list={type(options).__name__} for options={options}!')


