class CODEDEPLOY_GROUP:
    
    
    def __init__(self, client, meta:dict):
        self.Client = client
        self.Meta = meta
        self.Name = meta['deploymentGroupName']
        self.ApplicationName = meta['applicationName']
        self.DeploymentConfigName = meta['deploymentConfigName']
        self.ServiceRoleArn = meta['serviceRoleArn']
        self.EcsServices = meta['ecsServices']
        self.DeploymentGroupId = meta['deploymentGroupId']
        self.DeploymentGroupArn = meta['deploymentGroupArn']
        self.TargetRevision = meta['targetRevision']
        self.RevisionInfo = meta['revisionInfo']
        self.LastSuccessfulDeployment = meta['lastSuccessfulDeployment']
        self.DeploymentStyle = meta['deploymentStyle']
        self.BlueGreenDeploymentConfiguration = meta['blueGreenDeploymentConfiguration']
        self.LoadBalancerInfo = meta['loadBalancerInfo']
        self.Ec2TagSet = meta['ec2TagSet']
        self.OnPremisesInstanceTagSet = meta['onPremisesInstanceTagSet']
        self.TriggerConfigurations = meta['triggerConfigurations']
        self.AlarmConfiguration = meta['alarmConfiguration']
        self.AutoRollbackConfiguration = meta['autoRollbackConfiguration']
        self.DeploymentReadyOption = meta['deploymentReadyOption']
        self.DeploymentStyle = meta['deploymentStyle']
        self.BlueGreenDeploymentConfiguration = meta['blueGreenDeploymentConfiguration']
        self.LoadBalancerInfo = meta['loadBalancerInfo']
        self.Ec2TagSet = meta['ec2TagSet']
        self.OnPremisesInstanceTagSet = meta['onPremisesInstanceTagSet']
        self.TriggerConfigurations = meta['triggerConfigurations']
        self.AlarmConfiguration = meta['alarmConfiguration']
        self.AutoRollbackConfiguration = meta['autoRollbackConfiguration']
        self.DeploymentReadyOption = meta['deploymentReadyOption']
        self.DeploymentStyle = meta['deploymentStyle']
        self.BlueGreenDeploymentConfiguration = meta['blueGreenDeploymentConfiguration']
        self.LoadBalancerInfo = meta['loadBalancerInfo']
        self.Ec2TagSet = meta['ec2TagSet']
        self.OnPremisesInstanceTagSet = meta['onPremisesInstanceTagSet']
        self.TriggerConfigurations = meta['triggerConfigurations']
        self.AlarmConfiguration = meta['alarmConfiguration']
        self.AutoRollbackConfiguration = meta['autoRollbackConfiguration']
        self.DeploymentReadyOption = meta['deploymentReadyOption']
        self.DeploymentStyle = meta['deploymentStyle']


    def CreateDeployment(self,
        description:str='',
        ignoreApplicationStopFailures:bool=False,
        targetInstances:dict={}
    ) -> dict:
        '''👉 Creates a new deployment.'''

        deploymentGroupName = self.Name

        revision:dict = {
            'revisionType': 'AppSpecContent',
            'appSpecContent': {
                'content': '<APP_SPEC_CONTENT_HERE>',  # Specify the AppSpec content
                'sha256': 'HASH'
            }
        }

        response = self.Client.create_deployment(
            applicationName= self.ApplicationName,
            deploymentGroupName= deploymentGroupName,
            revision= revision,
            deploymentConfigName= self.DeploymentConfigName,
            description= description,
            ignoreApplicationStopFailures= ignoreApplicationStopFailures,
            targetInstances= targetInstances)
        
        return response