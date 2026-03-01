from DEPLOYER_TASK import DEPLOYER_TASK
from LOG import LOG
from pollyweb.utils.STRUCT import STRUCT
from pollyweb.utils.UTILS import UTILS

class DEPLOYER_PARSER():

    ICON= '🏗️'


    
    @classmethod
    def DirectoryToTasks(cls, path:str):
        '''👉️ Converts a directory of YAML files into a TASK list.'''

        UTILS.AssertIsStr(path, require=True)

        # Get the files.
        files = UTILS().OS().Directory(path).AssertExists().GetDeepFiles()
        if len(files) == 0:
            LOG.RaiseException(f'No files found in {path}.')

        # Convert the files to tasks.
        tasks:list[DEPLOYER_TASK] = []
        for file in files:
            
            if file.GetExtension() != '.yaml':
                LOG.Print(
                    '🏗️ DEPLOYER.PARSER.DirectoryToTasks:', 
                    'Skipping non-yaml file:', file) 
                continue

            if file.GetIcon() != '🧱':
                LOG.Print(
                    '🏗️ DEPLOYER.PARSER.DirectoryToTasks:', 
                    'Skipping non-🧱 file:', file) 
                continue

            subTasks = cls.FileToTasks(file.GetPath())
            tasks.extend(subTasks)

        # Verify the tasks.
        UTILS.AssertIsList(tasks, 
            require=True, 
            itemType=DEPLOYER_TASK)
        
        # Return the tasks.
        return tasks


    @classmethod
    def FileToTasks(cls, path:str):
        '''👉️ Converts a YAML file into an TASK list.'''

        LOG.Print(
            '🏗️ DEPLOYER.PARSER.FileToTasks:', 
            'Processing file:', path)

        UTILS.AssertIsStr(path, require=True)

        # Get the file.
        file = UTILS().OS().File(path)
        file.RequireExtension('yaml')
        file.AssertExists()

        # Convert the file to tasks.
        return cls.YamlToTasks(
            stack= file.GetSimpleName(),
            yaml= file.ReadYamlStruct(),
            path= file.GetPath())


    @classmethod
    def YamlsToTasks(cls, stack:str, yamls:list[STRUCT]):
        '''👉️ Converts a list of YAML objects into a TASK list.'''

        UTILS.AssertIsStr(stack, require=True)
        UTILS.AssertIsList(yamls, require=True, itemType=STRUCT)

        tasks:list[DEPLOYER_TASK] = []

        # Iterate through the YAML objects.
        for yaml in yamls:
            subTasks = cls.YamlToTasks(stack, yaml)
            tasks.extend(subTasks)

        # Return the tasks.
        return tasks


    @classmethod
    def YamlToTasks(cls, stack:str, yaml:dict|STRUCT, path:str):
        '''👉️ Converts a YAML object into a TASK list.'''

        # Ensure the parameters.
        UTILS.RequireArgs([stack, yaml])
        UTILS.AssertIsStr(stack, require=True)
        UTILS.AssertIsAnyType(yaml, [dict, STRUCT])

        # Initialize the deployment tasks.
        yaml = STRUCT(yaml)
        yaml.AssertOnlyKeys([
            'Inputs', 'Include', 'Params', 'Deploy', 
            '👉', '🤝'])
        
        # Verify the parameters.
        if yaml.ContainsAtt('Params'):
            yaml.GetStruct('Params').AssertOnlyKeys([
                'Handler',
                'Verifier'
            ])
        
        # Iterate through the assets.
        assets = yaml.GetStruct('Deploy')
        if UTILS.IsNoneOrEmpty(assets):
            LOG.Print(cls.YamlToTasks, f': No deploy section found in yaml.', 
                f'{stack=}', yaml)
            return []

        tasks:list[DEPLOYER_TASK] = []
        for key, value in assets.items():

            LOG.Print(cls.YamlToTasks, f': Processing asset', 'key=', key, 'value=', value)

            resource = STRUCT(value)
            resource.AssertOnlyKeys(
                ['👉', 'Type', 'Params', 'Dependencies'])

            LOG.Print(cls.YamlToTasks, f': Get the dependencies.')
            dependencies:list[str] = []
            if resource.ContainsAtt('Dependencies'):
                
                LOG.Print(cls.YamlToTasks, f': Get the dependency keys.', resource)
                dependencyKeys = resource.ListStr('Dependencies')
                if len(dependencyKeys) == 0:
                    LOG.RaiseException(
                        f'No dependencies found for {key} in {dependencyKeys}.',
                        'dependencyStruct=', dependencyKeys)

                # Iterate through the dependencies.
                for name in dependencyKeys:

                    # Forbid dots.
                    if '.' in name:
                        LOG.RaiseException(
                            f'Dependency [{name}] cannot have dots, '
                            f'task=[{key}] in stack=[{stack}].',)

                    # Add the stack to the dependency, if necessary.
                    if '-' not in name:
                        dependencies.append(f'{stack}-{name}')
                    else:
                        dependencies.append(name)

            # Create the task.
            task = DEPLOYER_TASK.New(
                path= path,
                stack= stack,
                asset= key,
                type= resource.RequireStr('Type'),
                params= resource.GetStruct('Params'),
                stackParams= yaml.GetStruct('Params'),
                dependencies= dependencies)
            
            # Append the task.
            tasks.append(task)

        # Verify the tasks.
        UTILS.AssertIsList(tasks, 
            itemType=DEPLOYER_TASK)

        # Get the inputs as tasks.
        inputs = yaml.GetStruct('Inputs')
        if not UTILS.IsNoneOrEmpty(inputs):
            for key, value in inputs.items():
                task = DEPLOYER_TASK.New(
                    path= path,
                    stack= stack,
                    asset= key,
                    type= 'Input',
                    params= STRUCT(value),
                    stackParams= yaml.GetStruct('Params'),
                    dependencies= [])
                
                tasks.append(task)
                
        # Verify the tasks.
        UTILS.AssertIsList(tasks, 
            itemType=DEPLOYER_TASK)
        
        return tasks