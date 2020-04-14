import argparse
import logging
import sys
import os

from kubernetes import client, config
#from .watcher import *

from .controller import Controller
from .threadedwatch import ThreadedWatcher
from .resourcewatcher import *
from .simpleclient import *

#for testing


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--tester")

def main():

    load_cluster_config()
    
    authorizedClient = create_authorized_client()

    rw = resourceWatcher()

    #Get Configs for what its watching. (Eventually)
    #rw._load_config()

    args = PARSER.parse_args()
    print(str(args.tester))

    if args.tester == "teststuff":
       print('tester working')
    else:
   
        #Primary Object Watcher
        #Build API
        api = create_api_client(rw.k8sApiVersion,authorizedClient)
        #Build API Resource
        apiWithResource = create_apiWithResource_client(api,rw.k8sApiResourceName)

        #Kwargs
        objectWatcher = ThreadedWatcher(rw.eventTypeFilter,apiWithResource,**rw.k8sAPIkwArgs)

        #Monitor anythign for changes?  Or is the "coordinator" doing all that?
        #serviceaccount_watcher = ThreadedWatcher(rwCoordinator.coreAPIfilter, rwCoordinator.coreAPI.list_service_account_for_all_namespaces)


        #Controller.  All "watchers" fed into Controller to process queues.
        controller = Controller(rwObject=rw, apiWatcher=objectWatcher)
        controller.start()
        
        objectWatcher.start()

        try:
            controller.join()
        except (KeyboardInterrupt, SystemExit):
            print('\n! Received keyboard interrupt, quitting threads.\n')
            controller.stop()
            controller.join()


if __name__ == '__main__':
    main()
