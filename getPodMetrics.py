from kubernetes import client, config

class GetMetric:
    def __init__(self):
        config.load_kube_config()
        self.api = client.CustomObjectsApi()  # Use CustomObjectsApi

    def get_pod_metrics(self, namespace='default'):
        try:
            # Access metrics via the Metrics API endpoint
            metrics = self.api.list_namespaced_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                namespace=namespace,
                plural="pods"
            )
            
            for pod in metrics.get('items', []):
                print(f"Pod: {pod['metadata']['name']}")
                for container in pod.get('containers', []):
                    print(f"  Container: {container['name']}")
                    print(f"    CPU Usage: {container['usage'].get('cpu', 'N/A')}")
                    print(f"    Memory Usage: {container['usage'].get('memory', 'N/A')}")
                print("-" * 30)
                
        except client.exceptions.ApiException as e:
            print(f"API Exception: {e}")

if __name__ == "__main__":
    handler = GetMetric()
    handler.get_pod_metrics()