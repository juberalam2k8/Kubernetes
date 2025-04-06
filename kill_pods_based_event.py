from kubernetes import client, config, watch
import time

class PodManager:
    def __init__(self):
        config.load_kube_config()
        self.api = client.CoreV1Api()

    def delete_pods_with_errors(self, namespace):
        pods = self.api.list_namespaced_pod(namespace)
        for pod in pods.items:
            pod_name = pod.metadata.name
            pod_status = pod.status.phase
            container_statuses = pod.status.container_statuses or []
            init_container_statuses = pod.status.init_container_statuses or []

            # Check for ImagePullBackOff in container statuses
            for status in container_statuses:
                if status.state.waiting and 'ImagePullBackOff' in status.state.waiting.reason:
                    print(f"Pod: {pod_name} has ImagePullBackOff status.")
                    self.delete_pod(namespace, pod_name)
                    break

            # Check for CrashLoopBackOff in container statuses
            for status in container_statuses:
                if status.state.waiting and 'CrashLoopBackOff' in status.state.waiting.reason:
                    print(f"Pod: {pod_name} has CrashLoopBackOff status.")
                    self.delete_pod(namespace, pod_name)
                    break

            # Check for ImagePullBackOff in init container statuses
            for status in init_container_statuses:
                if status.state.waiting and 'ImagePullBackOff' in status.state.waiting.reason:
                    print(f"Init container in pod: {pod_name} has ImagePullBackOff status.")
                    self.delete_pod(namespace, pod_name)
                    break

            # Check for CrashLoopBackOff in init container statuses
            for status in init_container_statuses:
                if status.state.waiting and 'CrashLoopBackOff' in status.state.waiting.reason:
                    print(f"Init container in pod: {pod_name} has CrashLoopBackOff status.")
                    self.delete_pod(namespace, pod_name)
                    break

    def delete_pod(self, namespace, pod_name):
        try:
            print(f"Deleting pod: {pod_name} in namespace: {namespace}")
            self.api.delete_namespaced_pod(
                name=pod_name,
                namespace=namespace,
                body=client.V1DeleteOptions(),
                grace_period_seconds=0,
                propagation_policy='Background'
            )
            time.sleep(5)  # Wait for a few seconds before checking again
        except Exception as e:
            print(f"Error deleting pod {pod_name}: {e}")

if __name__ == '__main__':
    namespace = 'default'
    pod_manager = PodManager()
    pod_manager.delete_pods_with_errors(namespace)
