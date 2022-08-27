#
# const.py - Predefined or computed variables.
#

import urllib3

from config import *

# JSON object to hold all of the state information such as line number and time offset
# Gets written to disk at an interval
stateTracker = {"currentLine": 1, 
                "timeOffset": 0.0,
                "timeDelta": 0.0, 
                "speedUpOffset": 0 }

dataFileLength = 0

splunkAuthHeader = {'Authorization': 'Splunk {}'.format(splunkHecToken)}

eventJsonStorage = ""

sleepCounter = 0

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)