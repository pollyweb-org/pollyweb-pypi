from LOG import LOG
from PW_UTILS.UTILS import UTILS
from VPC_NETWORK import VPC_NETWORK


class ECS_SERVICE:

    def __init__(self, 
        name:str, 
        cluster,
        client: any
    ):
        LOG.Print('@')

        from ECS_CLUSTER import ECS_CLUSTER
        UTILS.AssertIsType(cluster, ECS_CLUSTER, require= True)

        self.Name = name
        self.Cluster = cluster
        self.Client = client


    def Delete(self):
        LOG.Print('@')

        self._ScaleDown()
        self._WaitToScaleDown()
        
        self.Client.delete_service(
            cluster= self.Cluster.Name,
            service= self.Name)


    def _ScaleDown(self):
        LOG.Print('@')

        # First, scale the service down to 0 tasks
        cluster_name= self.Cluster.Name
        service_name= self.Name

        self.Client.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=0)


    def _WaitToScaleDown(self):
        LOG.Print('@')

        cluster_name= self.Cluster.Name
        service_name= self.Name
        
        while True:

            response = self.Client.describe_services(
                cluster=cluster_name,
                services=[service_name])
            service = response['services'][0]
            running_count = service['runningCount']

            if running_count == 0:
                LOG.Print("@: Service has scaled down. Proceeding to delete.")
                break
            else:
                LOG.Print(f"@: Waiting for service to scale down... {running_count} tasks still running.")
                UTILS.TIME().Sleep(2)

    
    @staticmethod
    def List(cluster):
        '''👉️ Lists the services in the cluster.'''
        LOG.Print('@')

        from ECS_CLUSTER import ECS_CLUSTER
        self:ECS_CLUSTER = cluster

        response = self.Client.list_services(
            cluster= self.Name)
        
        ret:list[ECS_SERVICE] = []
        for service in response['serviceArns']:
            ret.append(ECS_SERVICE(
                name= service,
                cluster= self,
                client= self.Client))
        return ret
    

    @staticmethod
    def Create(
        taskdef, 
        name:str, 
        vpc: VPC_NETWORK,
        desiredCount:int= 1
    ):
        '''👉️ Creates a service.'''
        LOG.Print('@')

        from ECS_TASKDEF import ECS_TASKDEF
        self:ECS_TASKDEF = taskdef

        # Get the subnets as a list of IDs.
        subnets = [
            subnet.ID
            for subnet in vpc.GetPublicSubnets()]
        if len(subnets) == 0:
            LOG.RaiseException('No public subnets found in the VPC.')

        # Get the security groups as a list of IDs.
        securityGroups = [
            vpc.GetPublicSecurityGroup().ID]

        # Create the service.
        response = self.Client.create_service(
            cluster= self.Cluster.Name,
            serviceName= name,
            taskDefinition= self.Arn,
            desiredCount= desiredCount,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnets,
                    'securityGroups': securityGroups,
                    'assignPublicIp': 'DISABLED'  # or 'ENABLED' based on your needs
                    # Note: using a public IP will block the delete of the VPC until AWS eventually cleans up the ENI.
                }
            },
            loadBalancers=[{
                'targetGroupArn': target_group['TargetGroups'][0]['TargetGroupArn'],
                'containerName': self.Cluster.Name,
                'containerPort': 8501
            }])
        
        # Return the service twin.
        return ECS_SERVICE(
            name= name, 
            cluster= self.Cluster,
            client= self.Client)