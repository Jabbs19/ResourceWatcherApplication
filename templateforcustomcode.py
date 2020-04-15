import argparse
import logging
import sys
import os

from kubernetes import client, config
from kubernetes.client import rest

logger = logging.getLogger('custom')
logging.basicConfig(level=logging.INFO)


def test_custom_code(input=None):
    if input==None:
        logger.info("[Message: %s]" % ("Custom Code invoked!!!! (v2) "))
    else:
        logger.info("[Message: %s]" % ("Custom Input (v2): " + input))