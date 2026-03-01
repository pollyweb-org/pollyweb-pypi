from .LOG import LOG
from .TESTS import TESTS 
from .SETTINGS import SETTINGS

class FILESYSTEM_TESTS:


    @classmethod
    def TestAllFileSystem(cls):
        
        if not SETTINGS.ICONS_ENABLED:
            return

        # Create main folder.
        dumps = LOG.GetLogDir().AssertExists()

        # Test GetParent without rename.
        dir = dumps.GetSubDir('FILESYSTEM_TESTS').Touch()
        TESTS.AssertEqual(
            dir.GetParentDir().GetPath(), 
            dumps.GetPath())

        # Create /TESTES/A/f.txt
        a = dir.GetSubDir('A').Touch()
        b = dir.GetSubDir('B').Delete()
        f = a.GetFile('f.txt').Touch()

        # Confirm creation.
        TESTS.AssertTrue(f.GetPath().endswith('FILESYSTEM_TESTS/A/f.txt'))
        TESTS.AssertTrue(a.Exists())
        TESTS.AssertTrue(f.Exists())

        # Rename the child directory.
        TESTS.AssertFalse(b.Exists())
        a.Rename('B')
        TESTS.AssertTrue(b.Exists())

        # Confirm the rename.
        TESTS.AssertTrue(a.GetPath().endswith('FILESYSTEM_TESTS/B'))
        TESTS.AssertTrue(f.GetPath().endswith('FILESYSTEM_TESTS/B/f.txt'))
        TESTS.AssertTrue(a.Exists())
        TESTS.AssertTrue(f.Exists())

        # Rename the top directory.
        dir.Rename('FILESYSTEM_RENAMED')
        TESTS.AssertTrue(a.Exists())
        TESTS.AssertTrue(f.Exists())
        TESTS.AssertTrue(a.GetPath().endswith('FILESYSTEM_RENAMED/B'))
        TESTS.AssertTrue(f.GetPath().endswith('FILESYSTEM_RENAMED/B/f.txt'))

        # Delete the test directory.
        TESTS.AssertTrue(dir.Exists())
        dir.Delete(recursive=True)
        TESTS.AssertFalse(dir.Exists())