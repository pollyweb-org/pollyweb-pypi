from .LOG import LOG
from .DIRECTORY import DIRECTORY
from .FILE import FILE


class PYTHON_EDITOR:

    ICON='🐍'


    def FixLine(self, i:int, lines:list[str], find:str, replace:str):
        LOG.Print(self.FixLine)

        # find the class method.
        if not lines[i].strip().startswith('def '):
            return
        
        # get the method name.
        signature = lines[i].strip().split(' ')[1]
        method_name = signature.split('(')[0]
        i += 1
        LOG.Print(self.FixLine, f': {method_name=}')

        # get the name of the first parameter.
        param_name = signature.split('(')[1]
        param_name = param_name.split(')')[0]
        param_name = param_name.split(',')[0]
        
        LOG.Print(f'@: {param_name=}')
        if param_name == 'cls':
            method_name = f'cls.{method_name}'
        elif param_name == 'self':
            method_name = f'self.{method_name}'
        else:
            return
        
        # find the next "LOG.Print(self.FixLine" before the next method or the end of the class."
        while i < len(lines) \
        and not lines[i].strip().startswith('def '):
            
            short = lines[i].strip()
            if short.startswith('self.LOG().') or short.startswith('LOG.'):
                if find in lines[i].strip():
                    LOG.Print(f'@: found: {method_name}')
                    lines[i] = lines[i].replace(find, replace)
                    lines[i] = lines[i].replace('<method_name>', method_name)
                    return
            i += 1

        if i == len(lines):
            LOG.Print(self.FixLine, f': end of file')
        elif lines[i].strip().startswith('def '):
            LOG.Print('@: next method')
        else:
            LOG.Print('@: error')
                

    def FixCode(self, code:str):
        
        lines:list[str] = code.splitlines()
        
        # check if there is anything to fix.
        found = False
        for line in lines:
            if '@' in line and 'Print(' in line:
                found = True
        if not found:
            return code

        fixes = {
            "LOG.Print('@'": "LOG.Print(<method_name>",
            "LOG.Print(f'@'": "LOG.Print(<method_name>",
            "LOG.Print('@": "LOG.Print(<method_name>, f'",
            "LOG.Print(f'@": "LOG.Print(<method_name>, f'",
            "self.LOG().Print('@'": "self.LOG().Print(<method_name>",
            "self.LOG().Print(f'@'": "self.LOG().Print(<method_name>",
            "self.LOG().Print('@": "self.LOG().Print(<method_name>, f'",
            "self.LOG().Print(f'@": "self.LOG().Print(<method_name>, f'"
        }

        for i in range(len(lines)):
            for find, replace in fixes.items():
                self.FixLine(
                    i= i, 
                    lines= lines, 
                    find= find, 
                    replace= replace)

        return '\n'.join(lines)


    def FixFile(self, file:FILE):
        LOG.Print(f'🔧 Fixing file: {file.GetPath()}')
        
        if file.GetNameWithoutExtension() in [
            'PYTHON_EDITOR',
            'PYTHON_EDITOR_TEST',
            'UTILS_PYTHON_TESTS'
        ]:
            return

        oldCode = file.ReadText()
        if '@' not in oldCode:
            return
        
        newCode = self.FixCode(oldCode)

        if newCode.strip() != oldCode.strip():
            file.WriteText(newCode.rstrip())


    def FixFiles(self, 
        dir:DIRECTORY=None, 
        maxFiles:int=None
    ):
        LOG.Print(self.FixFiles)

        if dir is None:
            dir = DIRECTORY.GetCurrent().GetSubDir('python')

        for file in dir.GetDeepFiles(
            endsWith='.py', 
            maxFiles=maxFiles
        ):
            self.FixFile(file)

        LOG.Print(self.FixFiles, f': done!')