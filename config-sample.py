#
# config.py - User modifiable variables.
#

# The name of the file to use. ".json" is assumed unless modified below.
file_key = "botsv4"
data_file_path = "./data/" + file_key + ".json"
state_file_path = "./var/" + file_key + ".state"


# Splunk URL, HEC Token, and Index to use.
splunk_url = "https://example.splk.me:8088/"
splunk_hec_token = "9802541d-394f-4053-b973-306757e15ed3"
splunk_index = "test"


should_loop = False
debug = False


# "linear" or "realtime"
# linear = equal amount of events per second (simpler)
# realtime = eps proportional to orgininal data file timestamps (more complex)
time_mode = "linear"

# Linear mode settings
time_playout_seconds = 14400 

# Realtime mode settings (in linear mode, batch size is calculated)
events_per_hec_batch = 10  
speed_up_factor = 2  
speed_up_interval = 2000  

# How often to log and write state to disk
state_tracker_reporting_factor = 2000
state_tracker_write_to_disk_factor = 1000

