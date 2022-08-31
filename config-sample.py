#
# config.py - User modifiable variables.
#

file_key = "botsv4"
data_file_path = "./data/" + file_key + ".json"
state_file_path = "./var/" + file_key + ".state"


splunk_url = "https://example.splk.me:8088/"
splunk_hec_token = "9802541d-394f-4053-b973-306757e15ed3"

splunk_index = "test"   # Currently we always override the data files index specification (but this may change)


should_loop = False
debug = False

speed_up_factor = 2
speed_up_interval = 2000

state_tracker_reporting_factor = 2000
state_tracker_write_to_disk_factor = 1000

events_per_hec_batch = 10