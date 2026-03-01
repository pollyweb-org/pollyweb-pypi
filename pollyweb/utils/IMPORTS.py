''' 📚 IMPORTS

* Imports all dependencies in imports.json

'''

import sys
import json

from  import LOADER

class IMPORTS(LOADER):

    # Get the current folder.
    import os
    folder = os.path.dirname(os.path.abspath(__file__))

    # Read the imports file.
    f = open(f'{folder}/imports.json', "r")
    imports = json.loads(f.read())

    if "Base" not in imports:
        raise Exception("Base missing from imports.json")

    # Reference all code folders.
    base = imports['Base']

    # If base is relative, merge the base with the current folder.
    if not os.path.isabs(base):
        base = os.path.join(folder, base)
    
    # Loop through directories.
    for dir in imports['Directories']:

        # Replace placeholders.
        relative = dir.replace('{base}', base)
        absolute = os.path.expanduser(relative)

        # Check if it exists.
        if not os.path.isdir(absolute):
            raise Exception(f'Folder not found: {absolute}')

        # Load to the python environment.
        sys.path.append(absolute)

    from .LOG import LOG 
    LOG.Print('✅ Libraries imported.')