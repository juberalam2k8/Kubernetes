from kubernetes import config, client
from kubernetes.stream import stream
from kubernetes.client.exceptions import ApiException

class ContainerMonitor:
    def __init__(self):
        config.load_kube_config()
        self.metrics_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

    def _parse_cpu(self, cpu_str: str) -> float:
        """Convert CPU metric string to cores"""
        if not cpu_str:
            return 0.0
        if cpu_str.endswith('n'):
            return float(cpu_str[:-1]) / 1e9  # nanocores to cores
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000  # millicores to cores
        return float(cpu_str)

    def _get_container_processes(self, pod_name: str, namespace: str, container_name: str):
        """Get process list with BusyBox-compatible commands"""
        try:
            # Check if shell exists in container
            test_command = ['/bin/sh', '-c', 'echo "Shell available"']
            stream(
                self.core_api.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=namespace,
                container=container_name,
                command=test_command,
                stderr=True, stdin=False,
                stdout=True, tty=False
            )

            # Get process list with supported columns
            exec_command = [
                '/bin/sh',
                '-c',
                'ps -o pid,comm,etime,time | head -n 10'
            ]
            
            resp = stream(
                self.core_api.connect_get_namespaced_pod_exec,
                name=pod_name,
                namespace=namespace,
                container=container_name,
                command=exec_command,
                stderr=True, stdin=False,
                stdout=True, tty=False
            )
            
            print(f"\nProcesses in {pod_name}/{container_name}:")
            print("PID   COMMAND          ELAPSED     CPU_TIME")
            print(resp.strip())
            print("-" * 40)

        except ApiException as e:
            if "no such file or directory" in str(e).lower():
                print(f"  ↳ Container {container_name} has no shell (/bin/sh)")
            else:
                print(f"  ↳ Error executing command: {str(e).strip()[:100]}...")

    def monitor_containers(self, namespace: str, cpu_threshold: float = 0.0005):
        """Monitor containers with adjustable threshold"""
        try:
            metrics = self.metrics_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="pods",
                namespace=namespace
            )

            print(f"Monitoring pods in {namespace} (threshold: {cpu_threshold} cores)")
            for pod in metrics.get('items', []):
                pod_name = pod['metadata']['name']
                for container in pod.get('containers', []):
                    cpu_usage = self._parse_cpu(container['usage'].get('cpu', '0'))
                    
                    if cpu_usage > cpu_threshold:
                        print(f"\n⚠️  High CPU ({cpu_usage:.2f} cores) in {pod_name}/{container['name']}")
                        self._get_container_processes(pod_name, namespace, container['name'])

        except ApiException as e:
            print(f"Metrics API Error: {str(e).strip()[:200]}")

if __name__ == '__main__':
    monitor = ContainerMonitor()
    # Adjust threshold as needed (0.5 cores = 500m)
    monitor.monitor_containers(namespace="default", cpu_threshold=0.0005)