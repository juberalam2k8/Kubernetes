from kubernetes import client, config, watch

class getDeploy:
    def __init__(self):
        config.load_kube_config()
        self.api = client.AppsV1Api()

    def getDeployment(self):
        deploys = self.api.list_deployment_for_all_namespaces(watch=False)
        print(f"Deployment are {deploys}")
            


event_handler = getDeploy()

event_handler.getDeployment()



 