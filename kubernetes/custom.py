import argparse
import logging
import sys
import os

from kubernetes import client, config
from kubernetes.client import rest

logger = logging.getLogger('custom')

def test_custom_code(input=None):
    if input=None:
        logger.info("[Message: %s]" % ("Custom Code invoked!!!!"))
    else:
        logger.info("[Message: %s]" % ("Custom Input: " + input))

