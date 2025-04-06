from kubernetes import client, config, watch

class GetEvents:
    def __init__(self):
        config.load_kube_config()
        self.api = client.CoreV1Api()

    def getEvent(self):
        events = self.api.list_event_for_all_namespaces(watch=False)
        for event in events.items:
            print(f"Evenets are {event}")
        


event_handler=GetEvents()
event_handler.getEvent()
    









