from kubernetes import config, client
from kubernetes.stream import stream
from kubernetes.client.exceptions import ApiException

class monitorMem:
    def __init__(self):
        config.load_kube_config()
        self.api_metrics = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

    def monitorMem(self,namespace: str):
        metrics = self.api_metrics.list_namespaced_custom_object(group="metrics.k8s.io",version="v1beta1",namespace=namespace,plural="pods")
        for pod in metrics.get('items',[]):
            pod_name=f"{pod['metadata']['name']}"
            for container in pod.get('containers',[]):
                container_name=f"{container['name']}"
                print(f"\nPods:{pod_name}/Container:{container_name} and Memory: {container['usage'].get('memory','0')[:-2]}")
                self._getcontainermemory(namespace, pod_name, container_name)
                

    def _getcontainermemory(self, namespace: str, pod_name: str, container_name: str):
        test_command=['/bin/sh', '-c', 'ls -lrth']
        try:
            resp = stream(
                self.core_api.connect_get_namespaced_pod_exec,
                namespace=namespace, 
                name=pod_name, 
                container=container_name, 
                command=test_command, 
                stderr=True, stdin=False,
                stdout=True,tty=False
            )
            print(resp.strip())
        except Exception as e:
            print(f"{e}")
        
        

                


if __name__=='__main__':
    handler = monitorMem()
    handler.monitorMem(namespace="default")

