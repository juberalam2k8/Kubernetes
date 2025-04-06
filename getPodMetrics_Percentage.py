from kubernetes import client, config

class GetMetric:
    def __init__(self):
        config.load_kube_config()
        self.metrics_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()  # To fetch pod resource limits

    def _parse_cpu(self, cpu_str):
        """Convert CPU string (e.g., '500m' = 0.5 cores) to float"""
        if cpu_str.endswith("n"):
            return float(cpu_str[:-1]) / 1e9  # nanocores to cores
        if cpu_str.endswith("m"):
            return float(cpu_str[:-1]) / 1000  # millicores to cores
        return float(cpu_str)

    def _parse_memory(self, memory_str):
        """Convert memory string (e.g., '512Mi' = 512*1024^2 bytes) to bytes"""
        units = {"K": 1024, "M": 1024**2, "G": 1024**3, "Ki": 1024, "Mi": 1024**2, "Gi": 1024**3}
        if not memory_str:
            return 0
        if memory_str[-2:] in units:
            return int(memory_str[:-2]) * units[memory_str[-2:]]
        elif memory_str[-1] in units:
            return int(memory_str[:-1]) * units[memory_str[-1]]
        return int(memory_str)

    def _get_pod_resource_limits(self, pod_name, namespace):
        """Fetch CPU/memory limits for a pod"""
        pod = self.core_api.read_namespaced_pod(pod_name, namespace)
        limits = {}
        for container in pod.spec.containers:
            if container.resources.limits:
                limits[container.name] = {
                    "cpu": self._parse_cpu(container.resources.limits.get("cpu", "0")),
                    "memory": self._parse_memory(container.resources.limits.get("memory", "0"))
                }
        return limits

    def get_pod_metrics(self, namespace='default'):
        try:
            metrics = self.metrics_api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            for pod in metrics.get('items', []):
                pod_name = pod['metadata']['name']
                print(f"Pod: {pod_name}")

                # Fetch resource limits for this pod
                limits = self._get_pod_resource_limits(pod_name, namespace)

                for container in pod.get('containers', []):
                    container_name = container['name']
                    cpu_usage = container['usage'].get('cpu', '0')
                    memory_usage = container['usage'].get('memory', '0')

                    # Convert usage to numeric values
                    cpu_cores = self._parse_cpu(cpu_usage)
                    memory_bytes = self._parse_memory(memory_usage)

                    # Get limits for this container
                    container_limits = limits.get(container_name, {})
                    cpu_limit = container_limits.get("cpu", 0)
                    memory_limit = container_limits.get("memory", 0)

                    # Calculate percentages
                    cpu_percent = (cpu_cores / cpu_limit * 100) if cpu_limit > 0 else 0
                    memory_percent = (memory_bytes / memory_limit * 100) if memory_limit > 0 else 0

                    print(f"  Container: {container_name}")
                    print(f"    CPU Usage: {cpu_cores:.3f} cores ({cpu_percent:.1f}% of limit)")
                    print(f"    Memory Usage: {memory_bytes / 1024**2:.2f} MiB ({memory_percent:.1f}% of limit)")
                print("-" * 30)
                
        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")

if __name__ == "__main__":
    handler = GetMetric()
    handler.get_pod_metrics()