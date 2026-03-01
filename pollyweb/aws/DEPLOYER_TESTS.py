from pathlib import Path

from DEPLOYER import DEPLOYER
from aws.AWS_TEST import AWS_TEST
from DEPLOYER_ARGS import DEPLOYER_ARGS
from DEPLOYER_EXEC_DUMMY import DEPLOYER_EXEC_DUMMY
from DEPLOYER_TASK import DEPLOYER_TASK
from LOG import LOG
from PW_UTILS.TESTS import TESTS
from PW_UTILS.UTILS import UTILS

class DEPLOYER_TESTS():

    @classmethod
    def _fixtures_root(cls) -> Path:
        return Path(__file__).resolve().parents[2] / "tests" / "deployer"


    @classmethod
    def _find_fixture(cls, name: str, expect_dir: bool) -> Path:
        root = cls._fixtures_root()
        if not root.exists():
            LOG.RaiseException(f"Fixtures root not found: {root}")

        matches: list[Path] = []
        for path in root.rglob("*"):
            if expect_dir and not path.is_dir():
                continue
            if not expect_dir and not path.is_file():
                continue

            stem = path.stem
            if stem == name or stem.endswith(name):
                matches.append(path)

        if not matches:
            LOG.RaiseException(f"Fixture not found: {name}")
        if len(matches) > 1:
            LOG.RaiseException(f"Multiple fixtures found for {name}: {matches}")

        return matches[0]
    

    @classmethod
    def TestYaml(cls):
        file_path = cls._find_fixture("TestYaml", expect_dir=False)
        yaml = UTILS().FromYaml(file_path.read_text())

        AWS_TEST.SetDomain('any-test.com')     
        DEPLOYER(
            DEPLOYER_ARGS(
                Name= 'Deployer.Test.Yaml',
                Simulate= True)
        ).ExecuteYaml(
            stack= 'test', 
            yaml= yaml, 
            path= str(file_path))


    @classmethod
    def TestParser(cls):
        file_path = cls._find_fixture("TestParser", expect_dir=False)
        yaml = UTILS().FromYaml(file_path.read_text())
        tasks = DEPLOYER.PARSER().YamlToTasks(
            stack= 'MyStack', 
            yaml= yaml,
            path= str(file_path))
        
        TESTS.AssertEqual(len(tasks), 1)
        task = tasks[0]

        TESTS.AssertEqual(
            task.RequireStackName(), 
            'MyStack')
        
        TESTS.AssertEqual(
            task.RequireAsset(), 
            'MyResource')
        
        TESTS.AssertEqual(
            task.RequireType(), 
            'Dummy')
        
        TESTS.AssertEqual(
            task.RequireParams(), 
            {'MyParam': 'MyValue'})
        
        TESTS.AssertEqual(
            task.RequireDependencies(), 
            ['MyStack-MyDependency'])


    @classmethod
    def TestExecuteInSequence(cls):     
        
        file_path = cls._find_fixture("TestExecuteInSequence", expect_dir=False)
        yaml = UTILS().FromYaml(file_path.read_text())

        DEPLOYER(
            DEPLOYER_ARGS(
                Name='Deployer.Test.ExecuteInSequence',
                Simulate=True,
                Parallel=False)
        ).ExecuteYaml(stack='MyStack', 
            yaml=yaml, 
            path= str(file_path))


    @classmethod
    def TestExecuteInParallel(cls):
        file_path = cls._find_fixture("TestExecuteInParallel", expect_dir=False)
        yaml = UTILS().FromYaml(file_path.read_text())

        deployer = DEPLOYER(
            DEPLOYER_ARGS(
                Parallel= True,
                Seconds= 5))

        deployer.ExecuteYaml(
            stack= 'MyStack', 
            yaml= yaml, 
            path= str(file_path))
        
        LOG.PARALLEL().SetMethodDone()
        

    @classmethod
    def TestExecuteDirectoryInSequence(cls):
        
        # Get the directory path.
        dir_path = cls._find_fixture("TestExecuteDirectory", expect_dir=True)
        
        # Clear the executions.
        DEPLOYER_EXEC_DUMMY.DummyExecutions = []

        def myOnTask(task:DEPLOYER_TASK, result:dict):
            LOG.Print('Task executed:', task.RequireFullName())

        # Execute the directory.
        ret = DEPLOYER(
            DEPLOYER_ARGS(
                Name= 'Deployer.Test.ExecuteDirectoryInSequence',
                Parallel= False,
                OnTask= myOnTask)
        ).ExecuteDirectory(
            path= str(dir_path))
        
        # Check the results.
        TESTS.AssertEqual(
            DEPLOYER_EXEC_DUMMY.DummyExecutions, [
                'StackA.Step1',
                'StackB.Step2',
                'StackA.Step3',
                'StackB.Step4'
            ])
        

    @classmethod
    def TestExecuteDirectoryInParallel(cls):
        
        # Get the directory path.
        dir_path = cls._find_fixture("TestExecuteDirectory", expect_dir=True)
        
        # Clear the executions.
        DEPLOYER_EXEC_DUMMY.DummyExecutions = []

        cls._asserted = False
        def Assert():
            TESTS.AssertEqual(
                DEPLOYER_EXEC_DUMMY.DummyExecutions, [
                    'StackA.Step1',
                    'StackB.Step2',
                    'StackA.Step3',
                    'StackB.Step4'
                ])
            cls._asserted = True

        # Execute the directory.
        runner = DEPLOYER(
            DEPLOYER_ARGS(
                Parallel= True,
                Seconds= 5))
        
        runner.ExecuteDirectory(
            path= str(dir_path), 
            assertMethod= Assert)

        if not cls._asserted:
            LOG.RaiseException('Assert not executed.')

        LOG.PARALLEL().SetMethodDone()


    @classmethod
    def TestForInfiniteLoops(cls):
        
        file_path = cls._find_fixture("TestForInfiniteLoops", expect_dir=False)
        yaml = UTILS().FromYaml(file_path.read_text())
        tasks = DEPLOYER.PARSER().YamlToTasks('myStack', 
            yaml= yaml,
            path= str(file_path))
        
        with TESTS.AssertValidation():
            deployerArgs = DEPLOYER_ARGS()
            DEPLOYER.MAESTRO(deployerArgs).CheckForInfiniteLoops(tasks)        
            LOG.RaiseException('Infinite loop not detected.')


    @classmethod
    def TestDeadLockInSequence(cls):
        
        # Get the directory path.
        dir_path = cls._find_fixture("TestDeadLock", expect_dir=True)
        
        # Execute the directory.
        with TESTS.AssertValidation():
          DEPLOYER(
              name= 'Deployer.Test.DeadLockInSequence',
              parallel= False
          ).ExecuteDirectory(
              path= str(dir_path))
          LOG.RaiseException('Deadlock not detected.')


    @classmethod
    def TestDeadLockInParallel(cls):
        
        # Get the directory path.
        dir_path = cls._find_fixture("TestDeadLock", expect_dir=True)
        
        # Execute the directory, expecting a deadlock.
        with TESTS.AssertValidation():
            DEPLOYER(
                DEPLOYER_ARGS(
                    Name= 'Deployer.Test.DeadLockInParallel',
                    Parallel= True,
                    Seconds= 5)
            ).ExecuteDirectory(
                path= str(dir_path))
            LOG.RaiseException('Deadlock not detected.')
        

    @classmethod
    def TestAllDeployer(cls):
        
        '''👉️ Tests all the methods in the class.'''
        from AWS import AWS as AWS_FLAT
        from aws.AWS import AWS as AWS_PKG

        old_mockup_flat = AWS_FLAT.MockUp
        old_mockup_pkg = AWS_PKG.MockUp
        AWS_FLAT.MockUp = True
        AWS_PKG.MockUp = True
        AWS_TEST.SetDomain("any-test.com")

        try:
            cls.TestParser()
            cls.TestYaml()
            cls.TestForInfiniteLoops()
            cls.TestExecuteInSequence()
            cls.TestExecuteInParallel()
            cls.TestExecuteDirectoryInSequence()
            cls.TestExecuteDirectoryInParallel()
            cls.TestDeadLockInSequence()
            cls.TestDeadLockInParallel()
        finally:
            AWS_FLAT.MockUp = old_mockup_flat
            AWS_PKG.MockUp = old_mockup_pkg

        LOG.PARALLEL().SetClassDone()
