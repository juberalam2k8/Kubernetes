from kubernetes import config, client, watch

class unhealthyPods:
    def __init__(self):
        config.load_kube_config()
        self.api=client.CoreV1Api()

    def unhealthyPods(self,namespace):
        field_selector = "status.phase!=Running"
        unhealthyPod=self.api.list_namespaced_pod(namespace,field_selector=field_selector)
        for pod in unhealthyPod.items:
            print(f"This pod is not running:{pod.metadata.name}")


if __name__=='__main__':
    handler=unhealthyPods()
    handler.unhealthyPods(namespace="default")