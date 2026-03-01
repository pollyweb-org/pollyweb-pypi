from pollyweb.utils.UTILS import UTILS


class ECS_TASK:


    def __init__(self,
        taskArn: str,
        client,
        cluster
    ):
        '''👉 Initializes the task.'''
        
        self.Client = client
        self.Arn = taskArn

        from ECS_CLUSTER import ECS_CLUSTER
        self.Cluster:ECS_CLUSTER = cluster


    def Stop(self):
        
        self.Client.stop_task(
            cluster= self.Cluster.Name, 
            task= self.Arn)
        
        self._WaitToStop()


    def _WaitToStop(self):
        cluster_name = self.Cluster.Name
        task_arn = self.Arn
    
        while True:
            response = self.Client.describe_tasks(
                cluster=cluster_name, 
                tasks=[task_arn])
            task_status = response['tasks'][0]['lastStatus']

            if task_status == 'STOPPED':
                print("Task has stopped.")
                break
            else:
                print(f"Task is currently in {task_status} state. Waiting...")
                UTILS.TIME().Sleep(2)  # Check every N seconds


    @staticmethod
    def List(cluster):
        '''👉️ Lists the tasks in the cluster.'''

        from ECS_CLUSTER import ECS_CLUSTER
        self:ECS_CLUSTER = cluster

        response = self.Client.list_tasks(
            cluster= self.Name)
        
        ret:list[ECS_TASK] = []
        for taskArn in response['taskArns']:
            ret.append(ECS_TASK(
                taskArn= taskArn,
                cluster= self,
                client= self.Client))
        return ret