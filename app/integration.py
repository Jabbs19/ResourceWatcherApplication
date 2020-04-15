import logging
import os
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(0, '/customcode')

#from .custompython import *
#import custompython
import custompython

logger = logging.getLogger('integration')
logging.basicConfig(level=logging.INFO)

def integration_test_custom_code(inputString="test"):
    try:
        test_cutom_code(inputString)
    except:
        print("ERROR")