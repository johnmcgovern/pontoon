#
# const.py - Static and calculated variables.
#

import urllib3

from config import *



eventJsonStorage = ""

splunkAuthHeader = {'Authorization': 'Splunk {}'.format(splunkHecToken)}

dataFileLength = 0

sleepCounter = 0

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)