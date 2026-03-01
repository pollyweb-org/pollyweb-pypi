from .DIRECTORY import DIRECTORY
from .SETTINGS import SETTINGS
from .TESTS import TESTS
from .FILESYSTEM import FILESYSTEM
from .LOG import LOG


class DIRECTORY_TESTS:
    

    @classmethod 
    def TestAllDirectory(cls):
        '''👉 Test all directory functions.'''

        __dumps__ = FILESYSTEM.DIRECTORY('__dumps__').AssertExists()
        try:
            cls._TestAllDirectory(__dumps__)
        finally:
            __dumps__.GetParentDir().ChangeTo()
            

    @classmethod 
    def _TestAllDirectory(cls, __dumps__:DIRECTORY):
        
        name = 'DIRECTORY'
        dir = __dumps__.GetSubDir(name)
        
        TESTS.AssertNotEqual(
            dir.GetParentDir().GetName(),
            dir.GetName())

        # Delete it.
        if dir.Exists():
            dir.Delete(recursive=True)
        
        # Confirm that it's deleted.
        TESTS.AssertFalse(dir.Exists())
        TESTS.AssertFalse(dir.GetParentDir().ContainsDirectory(name))
        with TESTS.AssertValidation():
            dir.AssertExists()
        with TESTS.AssertValidation():
            dir.RequirePath()
        
        # Create it.
        dir.Touch()

        # Confirm that it's created.
        TESTS.AssertTrue(dir.Exists())
        TESTS.AssertEqual(dir.GetName(), name)
        dir.AssertExists()
        dir.RequirePath()
        
        # Change to this directory.
        TESTS.AssertNotEqual(
            dir.GetPath(), 
            DIRECTORY.GetCurrent().GetPath())
        dir.ChangeTo()

        isFileSystemDisabled = True
        if isFileSystemDisabled:
            TESTS.AssertNotEqual(
                dir.GetPath(), 
                DIRECTORY.GetCurrent().GetPath())
        else:
            TESTS.AssertEqual(
                dir.GetPath(), 
                DIRECTORY.GetCurrent().GetPath())
        
        # Find it in the parent.
        parent = dir.GetParentDir()
        found = parent.GetSubDir(name)
        TESTS.AssertEqual(found.GetName(), name, 'Directory should be found.')
        TESTS.AssertTrue(parent.ContainsDirectory(name))
        
        # list child directories.
        #   the [?] before the name is for SetRunning() and SetDone() tests;
        #   those actions require the directory to have a type between [].
        dir1 = dir.GetSubDir('[?]dir1').Touch()
        dir2 = dir.GetSubDir('[?]dir2').Touch()
        TESTS.AssertEqual(
            dir.GetSubDirNames(),
            ['[?]dir1', '[?]dir2'])

        # list grand children directories.
        with TESTS.AssertValidation():
            dir.FindSubDirectory('dir1A')
        dir1A = dir.GetSubDir('[?]dir1').GetSubDir('dir1A')

        TESTS.AssertFalse(dir1A.Exists())
        dir1A.Touch()
        TESTS.AssertTrue(dir1A.Exists())

        dir1B = dir.GetSubDir('[?]dir1').GetSubDir('dir1B')
        dir1B.Touch()

        TESTS.AssertEqual(
            [d.GetName() for d in dir.GetDeepDirs()],
            ['[?]dir1', 'dir1A', 'dir1B', '[?]dir2'])
        
        # find a grand child directory.
        TESTS.AssertTrue(
            dir.FindSubDirectory('dir1A').Exists())
        TESTS.AssertEqual(
            dir.FindSubDirectory('dir1A').GetParentDir().GetName(), 
            '[?]dir1')
                
        # Get a file.
        fileX = dir.GetFile('fileX.txt')
        TESTS.AssertFalse(fileX.Exists())
        fileX.WriteText('.')
        TESTS.AssertTrue(fileX.Exists())

        # list files.
        dir.GetFile('fileY.txt').WriteText('.')
        file1 = dir1.GetFile('file1.txt').WriteText('.')
        dir1A.GetFile('file1A.txt').WriteText('.')
        TESTS.AssertEqual(
            [f.GetName() for f in dir.GetFiles()],
            ['fileX.txt', 'fileY.txt'])
        TESTS.AssertEqual(
            [f.GetName() for f in dir.GetDeepFiles()],
            ['file1A.txt', 'file1.txt', 'fileX.txt', 'fileY.txt'],
            f'Directory should have the correct deep files. {dir.GetDeepFiles()}')
        
        # Rename a dir.
        dir1.AssertExists()
        dir1.Rename('dir1Renamed')
        TESTS.AssertEqual(
            dir1.AssertName('dir1Renamed').GetName(),
            'dir1Renamed')
        dir1.AssertExists()

        # Check if it was renamed in the parent's child list.
        TESTS.AssertEqual(
            [d.GetName() for d in dir.GetSubDirs()],
            ['dir1Renamed', '[?]dir2'])
                
        if SETTINGS.ICONS_ENABLED:
            # Check if it was renamed in the children's parent reference.
            TESTS.AssertEqual(
                file1.GetParentDir().GetName(),
                'dir1Renamed', 
                f'Parent directory was not renamed: {file1.GetParentDir()}.')

        else:
            # Check if it was NOT renamed in the children's parent reference.
            TESTS.AssertEqual(
                file1.GetParentDir().GetName(),
                '[?]dir1', 
                f'Parent directory should have remained the same!: {file1.GetParentDir()}.')

        if SETTINGS.ICONS_ENABLED:
            file1.GetParentDir().AssertName('dir1Renamed')
            with TESTS.AssertValidation():
                file1.GetParentDir().AssertName('[?]dir1')
        else:
            file1.GetParentDir().AssertName('[?]dir1')
            with TESTS.AssertValidation():
                file1.GetParentDir().AssertName('dir1Renamed')

        if SETTINGS.ICONS_ENABLED:
            TESTS.AssertEqual(
                file1.GetPath(),
                dir1.GetPath() + '/file1.txt')
        else:
            TESTS.AssertNotEqual(
                file1.GetPath(),
                dir1.GetPath() + '/file1.txt')
            
        # This should work with or without FILESYSTEM enabled.
        TESTS.AssertEqual(
            dir1.GetFiles()[0].GetPath(),
            dir1.GetPath() + '/file1.txt')
        
        # Rename a file.
        fileR = dir1.GetFile('fileR.txt').WriteText('.')
        fileR.Rename('fileRRenamed.txt')
        TESTS.AssertEqual(
            fileR.GetName(),
            'fileRRenamed.txt')
        TESTS.AssertTrue(fileR.Exists())
        TESTS.AssertTrue(fileR.GetPath().endswith('fileRRenamed.txt'))
        TESTS.AssertFalse(dir1.GetFile('fileR.txt').Exists())
        TESTS.AssertTrue(dir1.GetFile('fileRRenamed.txt').Exists())

        # Set an icon
        dir1.Rename('DirIconned')
        dir.GetSubDir('DirIconned').AssertExists()
        dir1.SetIcon('🙌')
        TESTS.AssertEqual(dir1.GetName(), '🙌 DirIconned')
        dir.GetSubDir('🙌 DirIconned').AssertExists()
        TESTS.AssertTrue(dir1.GetIcon() == '🙌')

        # Find the directory by simple name.
        TESTS.AssertTrue(dir1.GetSimpleName() == 'DirIconned')
        TESTS.AssertTrue(dir.GetSubDirIconned('DirIconned').Exists())
        TESTS.AssertTrue('🙌' in dir.GetSubDirIconned('DirIconned').GetFile('file1.txt').GetPath())
        TESTS.AssertTrue(dir.GetSubDirIconned('🙌 DirIconned').Exists())
        TESTS.AssertTrue(dir.GetSubDir('🙌 DirIconned').Exists())
        
        # Change states.
        dir2.SetRunning()
        TESTS.AssertTrue(dir2.GetIcon() == '🟡')
        dir2.SetDone()
        TESTS.AssertTrue(dir2.GetIcon() == '🟢')
        dir2.SetFailed()
        TESTS.AssertTrue(dir2.GetIcon() == '🔴')
        
        # Do not change from failed to done.
        dir2.SetDone()
        TESTS.AssertTrue(dir2.GetIcon() == '🔴')

        # Get a file without an icon.
        fileIconned = dir.GetFile('fileIconned.txt').WriteText('.')
        dir.GetFile('fileIconned.txt').AssertExists()
        with TESTS.AssertValidation():
            dir.GetFile('🧱 fileIconned.txt').AssertExists()
        
        # Set the icon.
        fileIconned.SetIcon('🧱')
        dir.GetFile('🧱 fileIconned.txt').AssertExists()
        with TESTS.AssertValidation():
            dir.GetFile('fileIconned.txt').AssertExists()

        # Find file with or without icon.
        f2 = dir.GetFileIconned('fileIconned.txt').AssertExists()
        f2.SetIcon('✅')

        # Zip as bytes
        zip = dir.Zip()
        TESTS.AssertEqual(
            zip.GetZipInfo().GetFileNames()[-1].split('/')[-1],
            'file1A.txt') 

        # Clean up.
        dir.Clean()
        dir.AssertExists()
        TESTS.AssertEqual(len(dir.GetFiles()), 0)
        TESTS.AssertEqual(len(dir.GetDeepFiles()), 0)
        TESTS.AssertEqual(len(dir.GetSubDirs()), 0)
        TESTS.AssertEqual(len(dir.GetDeepDirs()), 0)
    
        dir.Delete()