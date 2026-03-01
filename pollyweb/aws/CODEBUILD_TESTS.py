from AWS import AWS
from AWS_RESOURCE_TESTER import AWS_RESOURCE_TESTER
from CODEBUILD_BUILD import CODEBUILD_EMPTY_REPO_EXCEPTION
from pollyweb.utils.UTILS import UTILS


class CODEBUILD_TESTS(AWS_RESOURCE_TESTER):
    

    @classmethod
    def GetAllTests(cls) -> list:
        return [
            cls.CodeBuildRole,
            cls.CodeBuildProject,
            cls.CodeBuildPython
        ]
    

    @classmethod
    def CodeBuildRole(cls):
        '''👉 Creates a CodeBuild role.'''
        AWS.CODEBUILD().EnsureRole()
        

    @classmethod
    def CodeBuildProject(cls):
        '''👉 Creates a CodeBuild project.
            1. Creates a CodeCommit repository.
            2. Creates a CodeBuild project.
            3. Starts a build.
            4. Waits for the build to complete.
            5. Deletes the resources.
        '''

        NAME = 'NLWEB-Test-CodeBuild'
        NAME2 = f'{NAME}-{UTILS.UUID()}'

        with AWS.CODECOMMIT().Ensure(
            # Cannot clone a previously deleted repository.
            name= NAME2
        ) as repo:
            ##repo.RetainOnFailure = True
                        
            with AWS.CODEBUILD().Ensure(
                name= NAME2,
                repo= repo,
            ) as project:
                ##project.RetainOnFailure = True
                
                build = project.StartBuild()
                try:
                    build.WaitToComplete()
                except CODEBUILD_EMPTY_REPO_EXCEPTION:
                    pass


    @classmethod
    def CodeBuildPython(cls):
        '''👉 Creates a CodeBuild project that builds a Python project.
            1. Creates a CodeCommit repository.
            2. Adds a Python project to the repository.
            3. Creates an ECR repository to store the built image.
            4. Creates a CodeBuild project that builds the Python project.
            5. Starts a build.
            6. Waits for the build to complete.
            7. Deletes the resources.
        '''

        NAME = 'NLWEB-Test-CodeBuild-Python'
        NAME2= f'{NAME}-{UTILS.UUID()}'


        # Create an ECR repository to store the built image
        with AWS.ECR().Ensure(
            name= NAME2.lower()
        ) as ecr:
        
            # Create a CodeBuild project that builds a Python project
            with AWS.CODECOMMIT().Ensure(
                # Cannot clone a previously deleted repository.
                name= NAME2
            ) as repo:
                ##repo.RetainOnFailure = True

                # Add a Python project to the CodeCommit repository
                with repo.Clone() as clone:
                    clone.AddPythonHellowWorld(ecr= ecr)

                # Create a CodeBuild project that builds the Python project
                with AWS.CODEBUILD().Ensure(
                    name= NAME2,
                    repo= repo,
                ) as project:
                    ##project.RetainOnFailure = True
                    
                    build = project.StartBuild()
                    build.WaitToComplete()