#
# const.py - Static and calculated variables.
#

import urllib3

from config import *


event_json_storage = ""

splunk_auth_header = {'Authorization': 'Splunk {}'.format(splunk_hec_token)}
splunk_hec_event_endpoint = "services/collector/event"

data_file_length = 0

sleep_counter = 0


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)