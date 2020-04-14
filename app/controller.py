import logging
import queue
import threading

from kubernetes.client.rest import ApiException
from kubernetes.client import models
from kubernetes import client, config
import copy
from .resourcewatcher import *


logger = logging.getLogger('controller')


class Controller(threading.Thread):
    """Reconcile current and desired state by listening for events and making
       calls to Kubernetes API.
    """

    def __init__(self, rwObject, apiWatcher, workqueue_size=10):
        """Initializes the controller.

        :param deploy_watcher: Watcher for pods events.
        :param workqueue_size: queue size for resources that must be processed.
        """
        super().__init__()
        # `workqueue` contains namespace/name of immortalcontainers whose status
        # must be reconciled
        self.rwObject = rwObject
        self.workqueue = queue.Queue(workqueue_size)

        self.apiWatcher = apiWatcher
        #self.config_watcher.add_handler(self._handle_watcherConfig_event)
        self.apiWatcher.add_handler(self._handle_event)

    def _handle_event(self,event):
        
        #New Event Object
        eo = eventObject(event)

        #Queue event object
        self._queue_work(eo)


    def _queue_work(self, eventObject):
        """Add a object name to the work queue."""
        if eventObject.eventObjectType == None:
            logger.error("Invalid eventObject ObjectType: {:s}".format(eventObject.eventObjectType))
            return
        self.workqueue.put(eventObject)

    def run(self):
        """Dequeue and process objects from the `workqueue`. This method
           should not be called directly, but using `start()"""
        self.running = True
        logger.info('Controller starting')
        while self.running:
            eo = self.workqueue.get()
            if not self.running:
                self.workqueue.task_done()
                break
            try:
                print("Reconcile state")
                self._process_event(eo)
                #self._printQueue(eo)
                self.workqueue.task_done()
            except Exception as e:
                logger.error("Error _reconcile state {:s}".format(e),exc_info=True)

    def stop(self):
        """Stops this controller thread"""
        self.running = False
        self.workqueue.put(None)


    def _printQueue(self, eventObject):
        """Make changes to go from current state to desired state and updates
           object status."""

        #eventType, eventObject, objectName, objectNamespace, annotationValue = object_key.split("~~")
        #ns = object_key.split("/")

        print("eventObject.eventObjectType: " + eventObject.eventObjectType)
        print("eventObject.objectName: " + eventObject.objectName)
        print("eventObject.objectNamespace: " + eventObject.objectNamespace)
        #print("eventObject.object 'object': " + str(eventObject.fullEventObject))

    def _process_event(self, eventObject):
        """Make changes to go from current state to desired state and updates
           object status."""
        #Can remove this logging later, not using event key anymore.
        logger.info("Event Pulled from Queue: {:s}".format(eventObject.eventKey))

        if should_event_be_processed(eventObject, self.rwObject):
            logger.info("[ObjectType: %s] [ObjectName: %s] [Namespace: %s] [EventType: %s] [Message: %s]" % (eventObject.eventObjectType, eventObject.objectName, eventObject.objectNamespace, eventObject.eventType, 
                "Event Processing."))    

            if eventObject.eventType in ['ADDED']:
                
                process_added_event(eventObject, self.rwObject)
            
            elif eventObject.eventType in ['MODIFIED']:
                
                process_added_event(eventObject, self.rwObject)

            elif eventObject.eventType in ['DELETED']:

                process_deleted_event(eventObject, self.rwObject)

            else:
                logger.info("[ObjectType: %s] [ObjectName: %s] [Namespace: %s] [EventType: %s] [Message: %s]" % (eventObject.eventObjectType, eventObject.objectName, eventObject.objectNamespace, eventObject.eventType, 
                    "Event found, but did not match any filters."))  
        else:
            logger.info("[ObjectType: %s] [ObjectName: %s] [Namespace: %s] [EventType: %s] [Message: %s]" % (eventObject.eventObjectType, eventObject.objectName, eventObject.objectNamespace, eventObject.eventType, 
                "Event Not Processed."))  



        #     else:
        #         if eventType in ['ADDED']:
        #             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][EventType: %s][Message: %s]" % (eventObject, objectName, objectNamespace, eventType,
        #                 "Event found.")) 
        #             if check_for_deployment(self.deployAPI, watcherApplicationConfig.watcherApplicationName, watcherApplicationConfig.objectNamespace):
        #                 dep = watcherApplicationConfig.get_deployment_object()
        #                 update_deployment(self.deployAPI, dep, watcherApplicationConfig.watcherApplicationName, watcherApplicationConfig.objectNamespace)
        #                 #watcherApplicationConfig.updateStatus(objectName, 'Added')

        #             else:
        #                 dep = watcherApplicationConfig.get_deployment_object()
        #                 create_deployment(self.deployAPI, dep, watcherApplicationConfig.deployNamespace)
        #             #self.createDeployment()
        #         elif eventType in ['MODIFIED']:
        #             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][EventType: %s][Message: %s]" % (eventObject, objectName, objectNamespace, eventType,
        #                 "Event found.")) 
        #             if check_for_deployment(self.deployAPI, watcherApplicationConfig.watcherApplicationName, watcherApplicationConfig.objectNamespace):
        #                 dep = watcherApplicationConfig.get_deployment_object()
        #                 update_deployment(self.deployAPI, dep, watcherApplicationConfig.watcherApplicationName, watcherApplicationConfig.objectNamespace)
        #                 #watcherApplicationConfig.updateStatus(objectName, 'Added and Modified')

        #             else:
        #                 dep = watcherApplicationConfig.get_deployment_object()
        #                 create_deployment(self.deployAPI, dep, watcherApplicationConfig.deployNamespace)
        #         elif eventType in ['DELETED']:
        #             #Since only sending "delete" events for custom resource, this is truly once its been deleted. 
        #             #Can't use for deleting deployment.
        #             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][EventType: %s][Message: %s]" % (eventObject, objectName, objectNamespace, eventType,
        #                 "Event found.")) 
        #             #watcherApplicationConfig.updateStatus(objectName, 'Deleted')
        #         else:
        #             logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][EventType: %s][Message: %s]" % (eventObject, objectName, objectNamespace, eventType,
        #                 "Event found, but did not match any filters.")) 

        # else:
        #     logger.info("[ObjectType: %s][ObjectName: %s][Namespace: %s][EventType: %s][Message: %s]" % (eventObject, objectName, objectNamespace, eventType,
        #                 "No WatcherConfig found."))  


     

   
