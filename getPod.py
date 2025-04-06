from kubernetes import client, config, watch

class getPods:
    def __init__(self):
        config.load_kube_config()
        self.api=client.CoreV1Api()

    def getPods(self):
        pods = self.api.list_pod_for_all_namespaces(watch=False)
        print(f"pods are {pods}")



event_handler = getPods()

event_handler.getPods()