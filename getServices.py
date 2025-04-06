from kubernetes import config, client, watch

class serviceManager():
    def __init__(self):
        config.load_kube_config()
        self.api=client.CoreV1Api()

    def getServices(self,namespace):
        try:
            list_service=self.api.list_namespaced_service(namespace)
            for svc in list_service.items:
                print(f"services are : {svc.metadata.name}")
        except Exception as e:
            print(f"Exception is {e}")
    
    def getEvents(self,namespace):
        try:
            list_events=self.api.list_namespaced_event(namespace)
            for event in list_events.items:
                print(f"Kind: {event.involved_object.kind} --> name : {event.involved_object.name} --> Reason: {event.reason}")
        except Exception as e:
            print(f"exception are : {e}")

if __name__=='__main__':
    namespace="default"
    handler = serviceManager()
    handler.getServices(namespace)
    handler.getEvents(namespace)