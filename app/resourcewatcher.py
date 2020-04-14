import logging
import os


from kubernetes.client.rest import ApiException
from kubernetes.client import models
from kubernetes import client, config
import copy

# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(0, '/customcode')

from .custompython import *
#import custompython



#k8s stuff
from .simpleclient import *


logger = logging.getLogger('resourcewatcher')

class resourceWatcher():
    def __init__(self):
        #Only updating this right now.
        #Actually load the values instead ay this point.
        self.status='Loaded'
        self._load_values_from_env()

    def _load_values_from_test(self):
        self.resourceWatcherName = 'resource-watcher-service'
        self.deployNamespace = 'research-watcher-testnamespace'
        self.watchNamespace = 'research-watcher-testnamespace'
        self.k8sApiVersion ='CoreV1Api'
        self.k8sApiResourceName = 'list_namespaced_service'
        self.k8sAPIkwArgs = {"namespace": self.watchNamespace}
        self.annotationFilterKey = 'service-watcher-key'
        self.eventTypeFilter = ['ADDED','MODIFIED','DELETED']
        self.parentOperatorAnnotationFilterKey = 'resourceWatcher-application-name'
        self.eventAction = "POST"
        #These will be used (SA at least) for any resources created by this Resource Watcher to perform tasks (e.g. pods)
        self.serviceAccountName = self.resourceWatcherName + '-sa'
        self.clusterRoleName = self.resourceWatcherName + '-clusterrole'
        self.clusterRoleBindingName = self.resourceWatcherName + '-clusterrolebinding'
        self.annotationFilterFinalDict = {self.annotationFilterKey:"Job Pod"}

    def _load_values_from_env(self):
        self.resourceWatcherName = os.getenv("RESOURCE_WATCHER_NAME")
        self.deployNamespace = os.getenv("DEPLOY_NAMESPACE")
        self.watchNamespace = os.getenv("WATCH_NAMESPACE")
        self.k8sApiVersion =os.getenv("K8S_API_VERSION")
        self.k8sApiResourceName = os.getenv("K8S_API_RESOURCE")
        
        buildKW = os.getenv("K8S_ADDITIONAL_KWARGS")
        self.k8sAPIkwArgs = eval(buildKW)

        self.annotationFilterKey = os.getenv("ANNOTATION_FILTER_KEY")
        self.eventTypeFilter = os.getenv("EVENT_TYPE_FILTER")
        self.parentOperatorAnnotationFilterKey = os.getenv("PARENT_OPERATOR_ANNOTATION_FILTER_KEY")
        self.eventAction = os.getenv("EVENT_ACTION")
        #These will be used (SA at least) for any resources created by this Resource Watcher to perform tasks (e.g. pods)
        self.serviceAccountName = self.resourceWatcherName + '-sa'
        self.clusterRoleName = self.resourceWatcherName + '-clusterrole'
        self.clusterRoleBindingName = self.resourceWatcherName + '-clusterrolebinding'
        self.annotationFilterFinalDict = {self.annotationFilterKey:"Job Pod"}

        
        # #From Config Object (eventually)
        #             self.resourceWatcherName = configObject['blah']['name']
        #     self.deployNamespace = configObject['spec']['deployNamespace']
        #     self.watchNamespace = configObject['spec']['watchNamespace']
        #     self.k8sApiVersion = configObject['spec']['k8sApiVersion']
        #     self.k8sApiResourceName = configObject['spec']['k8sApiResourceName']
        #     self.annotationFilterKey = configObject['spec']['annotationFilterBoolean']
        #     self.annotationFilterValue = configObject['spec']['annotationFilterString']
        #     self.eventTypeFilter = configObject['spec']['eventTypeFilter']
        #     self.fullJSONSpec = configObject['spec']
        #     self.parentAnnotationFilterKey = fixthis

        
class eventObject():
    def __init__(self, event):
        self.fullEventObject = event
        self.eventType = self.fullEventObject['type']
        try:
             self.eventObjectType = self.fullEventObject['object'].kind
        except:
             self.eventObjectType = self.fullEventObject['object']['kind']

        try:
            self.objectName = self.fullEventObject['object'].metadata.name
        except:
            self.objectName = self.fullEventObject['object']['metadata']['name']

        try:
            self.objectNamespace = self.fullEventObject['object'].metadata.namespace
        except:
            self.objectNamespace = self.fullEventObject['object']['metadata']['namespace']
        if self.objectNamespace == None:
            self.objectNamespace = 'GLOBAL'            
       
        #Deprecated object key for parsing, but can just use direct ref now.   
        self.eventKey = self.eventType + "~~" + self.eventObjectType + "~~" + self.objectName + "~~" + self.objectNamespace

        #Other
        self.annotationFilterValue = None
        
    def retrieve_and_set_annotation_value(self, rwObject):
        
        #Get annotations from eventObject
        try:
            #annotationsDict = eventObject['object'].metadata.annotations
            annotationsDict = self.fullEventObject['object'].metadata.annotations

        except:
            annotationsDict = self.fullEventObject['object']['metadata']['annotations']

        if annotationsDict == None:
            return False
        
        #Check against rwObject's Key
        annotationValue = annotationsDict.get(rwObject.annotationFilterKey, "")

        if annotationValue == None:
            self.annotationFilterValue = None
            return False
        else:        
            self.annotationFilterValue = annotationValue
            return True

def should_event_be_processed(eventObject, rwObject):

    eventObject.retrieve_and_set_annotation_value(rwObject)    

    if eventObject.annotationFilterValue == None:
        return False
    else:
       return True

def process_added_event(eventObject, rwObject):

    if rwObject.eventAction == "POST":
        logger.info("[Message: %s]" % ("ADDED Event Processed"))
        logger.info("[Message: %s]" % ("Annotation Value for this Event: " + str(eventObject.annotationFilterValue)))
        logger.info("[Message: %s]" % (rwObject.eventAction))

    elif rwObject.eventAction == "CUSTOM":
        logger.info("[Message: %s]" % ("ADDED Event Processed"))
        logger.info("[Message: %s]" % ("Annotation Value for this Event: " + str(eventObject.annotationFilterValue)))
        logger.info("[Message: %s]" % (rwObject.eventAction))
        test_custom_code()
        
        #Call Custom Code

def process_modified_event(eventObject, rwObject):
    if rwObject.eventAction == "POST":
        logger.info("[Message: %s]" % ("MODIFIED Event Processed"))
        logger.info("[Message: %s]" % ("Annotation Value for this Event: " + str(eventObject.annotationFilterValue)))
        logger.info("[Message: %s]" % (rwObject.eventAction))

    elif rwObject.eventAction == "CUSTOM":
        logger.info("[Message: %s]" % ("MODIFIED Event Processed"))
        logger.info("[Message: %s]" % ("Annotation Value for this Event: " + str(eventObject.annotationFilterValue)))
        logger.info("[Message: %s]" % (rwObject.eventAction))
        test_custom_code()

        #Call Custom Code

def process_deleted_event(eventObject, rwObject):
    if rwObject.eventAction == "POST":
        logger.info("[Message: %s]" % ("DELETED Event Processed"))
        logger.info("[Message: %s]" % ("Annotation Value for this Event: " + str(eventObject.annotationFilterValue)))
        logger.info("[Message: %s]" % (rwObject.eventAction))
    elif rwObject.eventAction == "CUSTOM":
        logger.info("[Message: %s]" % ("DELETED Event Processed"))
        logger.info("[Message: %s]" % ("Annotation Value for this Event: " + str(eventObject.annotationFilterValue)))
        logger.info("[Message: %s]" % (rwObject.eventAction))
        test_custom_code()

        #Call Custom Code




# #Coorindator (Operator) object
# class coordinator():
#     #def __init__(self, customGroup, customVersion, customPlural, customKind, apiVersion, customEventFilter, deployEventFilter):
#     def __init__(self, authorizedClient):
        
#         #Running Operator (Controller) Values
#         self.customApiVersion = "CustomObjectsApi"
#         self.customEventFilter =  {'eventTypesList': ['ADDED','MODIFIED','DELETED']}
#         self.customApiInstance = client.CustomObjectsApi(authorizedClient)

#         self.deploymentApiVersion = "AppsV1Api"
#         self.deployEventFilter = {'eventTypesList': ['zz']}
#         self.deploymentApiInstance = client.AppsV1Api(authorizedClient)

#         self.coreAPI = client.CoreV1Api(authorizedClient)
#         self.coreAPIfilter = {'eventTypesList': ['MODIFIED']}
#         self.rbacAPI = client.RbacAuthorizationV1Api(authorizedClient) 
#         self.rbacAPIfilter = {'eventTypesList': ['MODIFIED']}

#         self.childAnnotationFilterKey = "resourceWatcher-application-name"

    
#         #Maybe not needed
#         self.authorizedClient = authorizedClient
#         self.finalizer = ['watcher.delete.finalizer']
#         self.annotationFilterValue = "resource-watcher-service"   #Optional?


# class resourceWatcher():
#     def __init__(self, crOperand, parentAnnotationFilterKey):

#         self.resourceWatcherName = crOperand['metadata']['name']
#         self.deployNamespace = crOperand['spec']['deployNamespace']
#         self.watchNamespace = crOperand['spec']['watchNamespace']
#         self.k8sApiVersion = crOperand['spec']['k8sApiVersion']
#         self.k8sApiResourceName = crOperand['spec']['k8sApiResourceName']
#         self.annotationFilterBoolean = crOperand['spec']['annotationFilterBoolean']
#         self.annotationFilterString = crOperand['spec']['annotationFilterString']
#         self.eventTypeFilter = crOperand['spec']['eventTypeFilter']
#         self.fullJSONSpec = crOperand['spec']
#         #Need to add these to CR or hardcode
#         self.serviceAccountName = self.resourceWatcherName + '-sa'
#         self.clusterRoleName = self.resourceWatcherName + '-clusterrole'
#         self.clusterRoleBindingName = self.resourceWatcherName + '-clusterrolebinding'
#         self.parentAnnotationFilterKey = parentAnnotationFilterKey
#         self.annotationFilterFinalDict = {self.parentAnnotationFilterKey:self.resourceWatcherName}

#         # #Annotation Creation
#         # try:
#         #     # annotationString = {}
#         #     #     self.crdObject.annotationFilterKey
#         #     # }
#         #     # annotationDict = json.loads(self.crdObject.annotationFilterKey+":"+self.resourceWatcherName) 
#         #     annotationDict = {self.crdObject.annotationFilterKey:self.resourceWatcherName}
#         # except:
#         #     annotationDict = None
#         #     print('annotation creation did not work')
#         # self.annotationFilterFinalDict = annotationDict
 

#     def _build_deployment_definition(self):

#         # Configureate Pod template container
#         container = client.V1Container(
#             name="resource-watcher",
#            # image="image-registry.openshift-image-registry.svc:5000/watcher-operator/watcher-application:latest",
#             image="busybox",
#             command= ["/bin/sh", "-c", "tail -f /dev/null"],
#             ports=[client.V1ContainerPort(container_port=8080)],
#             env=[client.V1EnvVar(name='ANNOTATION_FILTER_BOOLEAN',value=self.annotationFilterBoolean),
#                 client.V1EnvVar(name='ANNOTATION_FILTER_STRING',value=self.annotationFilterString),
#                 client.V1EnvVar(name='WATCH_NAMESPACE',value=self.watchNamespace),
#                 client.V1EnvVar(name='API_VERSION',value=self.k8sApiVersion),
#                 client.V1EnvVar(name='API_RESOURCE_NAME',value=self.k8sApiResourceName),
#                 client.V1EnvVar(name='PATH_TO_CA_PEM',value='/ca/route'),   #Figure out later.
#                 client.V1EnvVar(name='JWT_TOKEN',value='141819048109481094')    #Figure out later.
#                 ]
#         )
#         # Create and configurate a spec section
#         template = client.V1PodTemplateSpec(
#             metadata=client.V1ObjectMeta(labels={"app": self.resourceWatcherName}),
#             spec=client.V1PodSpec(service_account=self.serviceAccountName,
#                                 service_account_name=self.serviceAccountName,
#                                 containers=[container]))

# # # Create and configurate a spec section
# #         template = client.V1PodTemplateSpec(
# #             metadata=client.V1ObjectMeta(labels={"app": self.watcherApplicresourceWatcherNameationName}),
# #             spec=client.V1PodSpec(containers=[container]))            
#         # Create the specification of deployment
#         spec = client.V1DeploymentSpec(
#             replicas=1,
#             template=template,
#             selector={'matchLabels': {'app':  self.resourceWatcherName}})
#         # Instantiate the deployment object
#         deployment = client.V1Deployment(
#             api_version="apps/v1",
#             kind="Deployment",
#             metadata=client.V1ObjectMeta(name= self.resourceWatcherName,annotations=self.annotationFilterFinalDict),
#             spec=spec)
#         return deployment



# #
# #Global Functions for Operators  
# #
# #  
# def get_custom_event_data(event,key):
#     if key == 'Namespace':
#         return event['object']['spec']['deployNamespace']

    



# def load_configuration_object(object_key, crdObject, rwCoordinatorObject, *args, **kwargs):
#     try:
#         eventType, eventObject, objectName, objectNamespace, annotation = object_key.split("~~")
#         #watcherConfigExist = check_for_custom_resource(objectName, *self.func_args, **self.func_kwargs) self.customAPI, self.customGroup, self.customVersion, self.customPlural, objectName)
        
#         #List the monitored objects that you want to use annotations to "trigger" events
#         if eventObject in ['ServiceAccount','ClusterRole','ClusterRoleBinding']:
#             lookupValue = annotation
#         elif eventObject in ['Deployment','ResourceWatcher']:
#             lookupValue = objectName
#         print("lookupValue: " + lookupValue)
#         try:
#             rwOperand = get_custom_resource(rwCoordinatorObject.customApiInstance, lookupValue, crdObject.customGroup,crdObject.customVersion, crdObject.customPlural)
#         except:
#             rwOperand = None

#         if rwOperand:
#             return rwOperand, True
#         else:
#             return None, False

#     except ApiException as e:
#         logger.info("No Object Found for 'should event be processed': {:s}".format(object_key))
#         logger.error("Error:" + e)
#         return None, False


# def remove_finalizer(object_key, crdObject, rwCoordinatorObject, rwName):
#     eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")

#     #Build Body to pass to customresources.patch
#     noFinalizerBody = {
#     "apiVersion": crdObject.customGroup + '/' + crdObject.customVersion,
#     "kind": crdObject.customKind,
#     "metadata": {
#         "name": rwName,
#         "finalizers": []
#                 }
#     }
#     try:
#         print("noFinalizerBody:" + str(noFinalizerBody))
#         api_response = patch_custom_resource(rwCoordinatorObject.customApiInstance, crdObject.customGroup, crdObject.customVersion, crdObject.customPlural, rwName, noFinalizerBody)
#     except ApiException as e:
#         logger.error("Finalizer Not removed. [ResourceWatcherName: " + rwName + "] Error: %s\n" % e)


# def check_marked_for_delete(object_key, crdObject, rwCoordinatorObject, *args, **kwargs):
#     eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")

#     if eventObject == 'ResourceWatcher':
#         operandName = objectName
#         try:
#             operandBody = get_custom_resource(rwCoordinatorObject.customApiInstance, operandName, crdObject.customGroup,crdObject.customVersion, crdObject.customPlural)
#             if (operandBody['metadata']['deletionTimestamp'] != ""):
#                 return True
#             else:
#                 return False

#         except:
#             return False
#     else:
#         return False
    

# def process_marked_for_deletion(object_key, crdObject, rwCoordinatorObject, rwObject, *args, **kwargs):
#     eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")

#     if check_for_deployment(rwCoordinatorObject.deploymentApiInstance,rwObject.resourceWatcherName, rwObject.deployNamespace) == True:
#         delete_deployment(rwCoordinatorObject.deploymentApiInstance, rwObject.resourceWatcherName, rwObject.deployNamespace)
#         logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                 "Deployment Deleted")) 
    
#     if check_for_clusterrolebinding(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleBindingName) == True:
#         delete_clusterrolebinding(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleBindingName)
#         logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                 "ClusterRoleBinding Deleted")) 

#     if check_for_clusterrole(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleName) == True:
#         delete_clusterrole(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleName)
#         logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                 "ClusterRole Deleted")) 
    
#     if check_for_serviceaccount(rwCoordinatorObject.coreAPI,rwObject.serviceAccountName,rwObject.deployNamespace) == True:
#         delete_serviceaccount(rwCoordinatorObject.coreAPI, rwObject.serviceAccountName, rwObject.deployNamespace)
#         logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#         "ServiceAccount Deleted")) 

#     remove_finalizer(object_key, crdObject, rwCoordinatorObject, objectName)

    
# def process_modified_event(object_key, crdObject, rwCoordinatorObject, rwObject, *args, **kwargs):
#     eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")

#     if eventObject == 'ServiceAccount':
#         saBody = create_quick_sa_definition(rwObject.serviceAccountName, rwObject.deployNamespace, rwObject.annotationFilterFinalDict)
#         if check_for_serviceaccount(rwCoordinatorObject.coreAPI,rwObject.serviceAccountName,rwObject.deployNamespace) == True:
#             update_serviceaccount(rwCoordinatorObject.coreAPI, rwObject.serviceAccountName,rwObject.deployNamespace, saBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Service Account Updated")) 
#         else:
#             create_serviceaccount(rwCoordinatorObject.coreAPI,saBody,rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Service Account Created")) 

#     if eventObject == 'ClusterRole':
#         clusterroleBody = create_quick_clusterrole_definition(rwObject.clusterRoleName, 'rules not implemented yet', rwObject.annotationFilterFinalDict)
#         if check_for_clusterrole(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleName) == True:
#             update_clusterrole(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleName, clusterroleBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRole Updated")) 
                                    
#         else:
#             create_clusterrole(rwCoordinatorObject.rbacAPI,clusterroleBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRole Updated")) 
                        
#     if eventObject == 'ClusterRoleBinding':
#         crBindingBody = create_quick_clusterrolebinding_definition(rwObject.clusterRoleBindingName,rwObject.clusterRoleName,rwObject.serviceAccountName,rwObject.deployNamespace, rwObject.annotationFilterFinalDict)
#         if check_for_clusterrolebinding(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleBindingName) == True:
#             update_clusterrolebinding(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleBindingName,     crBindingBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRoleBinding Updated")) 
#         else:
#             create_clusterrolebinding(rwCoordinatorObject.rbacAPI,crBindingBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRoleBinding Updated")) 
                                        

#     if eventObject == 'Deployment':
#         deployBody = rwObject._build_deployment_definition()
#         if check_for_deployment(rwCoordinatorObject.deploymentApiInstance,rwObject.resourceWatcherName, rwObject.deployNamespace) == True:
#             update_deployment(rwCoordinatorObject.deploymentApiInstance, deployBody, objectName, rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Deployment Updated")) 
                                        
#         else:
#             create_deployment(rwCoordinatorObject.deploymentApiInstance, deployBody, rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Deployment Updated")) 
                                        

#     if eventObject == 'ResourceWatcher':
#         #Deploy All
#         saBody = create_quick_sa_definition(rwObject.serviceAccountName, rwObject.deployNamespace, rwObject.annotationFilterFinalDict)
#         if check_for_serviceaccount(rwCoordinatorObject.coreAPI,rwObject.serviceAccountName,rwObject.deployNamespace) == True:
#             update_serviceaccount(rwCoordinatorObject.coreAPI, rwObject.serviceAccountName,rwObject.deployNamespace, saBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Service Account Updated")) 
#         else:
#             create_serviceaccount(rwCoordinatorObject.coreAPI,saBody,rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Service Account Created")) 

#         clusterroleBody = create_quick_clusterrole_definition(rwObject.clusterRoleName, 'rules not implemented yet', rwObject.annotationFilterFinalDict)
#         if check_for_clusterrole(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleName) == True:
#             update_clusterrole(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleName, clusterroleBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRole Updated")) 
                                    
#         else:
#             create_clusterrole(rwCoordinatorObject.rbacAPI,clusterroleBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRole Updated")) 
                        
#         crBindingBody = create_quick_clusterrolebinding_definition(rwObject.clusterRoleBindingName,rwObject.clusterRoleName,rwObject.serviceAccountName,rwObject.deployNamespace, rwObject.annotationFilterFinalDict)
#         if check_for_clusterrolebinding(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleBindingName) == True:
#             update_clusterrolebinding(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleBindingName,     crBindingBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRoleBinding Updated")) 
#         else:
#             create_clusterrolebinding(rwCoordinatorObject.rbacAPI,crBindingBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRoleBinding Updated")) 
                                        

#         deployBody = rwObject._build_deployment_definition()
#         if check_for_deployment(rwCoordinatorObject.deploymentApiInstance,rwObject.resourceWatcherName, rwObject.deployNamespace) == True:
#             update_deployment(rwCoordinatorObject.deploymentApiInstance, deployBody, objectName, rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Deployment Updated")) 
                                        
#         else:
#             create_deployment(rwCoordinatorObject.deploymentApiInstance, deployBody, rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Deployment Updated")) 

    
# def process_added_event(object_key, crdObject, rwCoordinatorObject, rwObject, *args, **kwargs):
#     eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")


#     if eventObject == 'ResourceWatcher':
#     #Deploy All
#         saBody = create_quick_sa_definition(rwObject.serviceAccountName, rwObject.deployNamespace, rwObject.annotationFilterFinalDict)
#         if check_for_serviceaccount(rwCoordinatorObject.coreAPI,rwObject.serviceAccountName,rwObject.deployNamespace) == True:
#             update_serviceaccount(rwCoordinatorObject.coreAPI, rwObject.serviceAccountName,rwObject.deployNamespace, saBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Service Account Updated")) 
#         else:
#             create_serviceaccount(rwCoordinatorObject.coreAPI,saBody,rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Service Account Created")) 

#         clusterroleBody = create_quick_clusterrole_definition(rwObject.clusterRoleName, 'rules not implemented yet', rwObject.annotationFilterFinalDict)
#         if check_for_clusterrole(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleName) == True:
#             update_clusterrole(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleName, clusterroleBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRole Updated")) 
                                    
#         else:
#             create_clusterrole(rwCoordinatorObject.rbacAPI,clusterroleBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRole Updated")) 
                        
#         crBindingBody = create_quick_clusterrolebinding_definition(rwObject.clusterRoleBindingName,rwObject.clusterRoleName,rwObject.serviceAccountName,rwObject.deployNamespace, rwObject.annotationFilterFinalDict)
#         if check_for_clusterrolebinding(rwCoordinatorObject.rbacAPI,rwObject.clusterRoleBindingName) == True:
#             update_clusterrolebinding(rwCoordinatorObject.rbacAPI, rwObject.clusterRoleBindingName,     crBindingBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRoleBinding Updated")) 
#         else:
#             create_clusterrolebinding(rwCoordinatorObject.rbacAPI,crBindingBody)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "ClusterRoleBinding Updated")) 
                                        

#         deployBody = rwObject._build_deployment_definition()
#         if check_for_deployment(rwCoordinatorObject.deploymentApiInstance,rwObject.resourceWatcherName, rwObject.deployNamespace) == True:
#             update_deployment(rwCoordinatorObject.deploymentApiInstance, deployBody, objectName, rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Deployment Updated")) 
                                        
#         else:
#             create_deployment(rwCoordinatorObject.deploymentApiInstance, deployBody, rwObject.deployNamespace)
#             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][Message: %s]" % (eventObject, objectName, objectNamespace, 
#                         "Deployment Updated")) 
        
   
# def process_deleted_event(object_key, *args, **kwargs):
#     eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")

#     logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][EventType: %s][Annotation: %s][Message: %s]" % (eventObject, objectName, objectNamespace, eventType, annotationValue,
#                     "Object Delete.")) 
#                 #Since only sending "delete" events for custom resource, this is truly once its been deleted. 
#                 #Can't use for deleting deployment.
#     #             #watcherApplicationConfig.updateStatus(objectName, 'Deleted')   
     

   
