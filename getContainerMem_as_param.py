from kubernetes import config, client
from kubernetes.stream import stream
from kubernetes.client.exceptions import ApiException
import argparse

class KubernetesContainerManager:
    def __init__(self):
        config.load_kube_config()
        self.api_metrics = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

    def execute_container_action(self, namespace: str, pod_name: str, container_name: str):
        try:
            # Fetch metrics for the specified pod
            pod_metrics = self.api_metrics.get_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods",
                name=pod_name
            )
        except ApiException as e:
            print(f"Error retrieving metrics for pod {pod_name}: {e}")
            return

        # Locate the specified container
        containers = pod_metrics.get('containers', [])
        target_container = next((c for c in containers if c['name'] == container_name), None)
        
        if not target_container:
            print(f"Container '{container_name}' not found in pod '{pod_name}'")
            return

        # Display memory usage
        memory = target_container['usage'].get('memory', '0Ki')[:-2]
        print(f"Pod: {pod_name}\nContainer: {container_name}\nMemory Usage: {memory}KiB")

        # Execute predefined command in container
        self._execute_container_command(namespace, pod_name, container_name)

    def _execute_container_command(self, namespace: str, pod_name: str, container_name: str):
        command = ['/bin/sh', '-c', 'ls -lrth']
        try:
            response = stream(
                self.core_api.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=namespace,
                container=container_name,
                command=command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False
            )
            print("\nCommand execution result:\n" + response.strip())
        except ApiException as e:
            print(f"Command execution failed: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Execute commands in Kubernetes containers')
    parser.add_argument('--namespace', required=True, help='Namespace of the pod')
    parser.add_argument('--pod', required=True, help='Name of the pod')
    parser.add_argument('--container', required=True, help='Name of the container')
    
    args = parser.parse_args()
    
    manager = KubernetesContainerManager()
    manager.execute_container_action(
        namespace=args.namespace,
        pod_name=args.pod,
        container_name=args.container
    )